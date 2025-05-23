import os
import httpx
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv


from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage, BaseMessage
from typing import List
from mcp import McpError

load_dotenv()


class FurnitureAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.mcp_client: MultiServerMCPClient | None = None
        self.agent_executor = None
        self.is_initialized = False
        self.current_auth0_token: str | None = None
        self.token_expires_at: datetime | None = None
        self.auth0_domain = os.getenv("AUTH0_DOMAIN")
        self.auth0_client_id = os.getenv("AUTH0_CLIENT_ID")
        self.auth0_client_secret = os.getenv("AUTH0_CLIENT_SECRET")
        self.api_audience = os.getenv("API_AUDIENCE")

    async def _get_auth0_access_token_internal(self) -> str | None:
        if (
            self.current_auth0_token
            and self.token_expires_at
            and datetime.now(timezone.utc) < self.token_expires_at - timedelta(minutes=1)
        ):
            return self.current_auth0_token

        print("FurnitureAgent: Requesting new Auth0 access token...")
        if not all([self.auth0_domain, self.auth0_client_id, self.auth0_client_secret, self.api_audience]):
            print("FurnitureAgent: ERROR - Auth0 client credentials not fully configured.")
            return None

        token_url = f"https://{self.auth0_domain}/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.auth0_client_id,
            "client_secret": self.auth0_client_secret,
            "audience": self.api_audience,
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=payload)
                response.raise_for_status()
                token_data = response.json()
                print(f"FurnitureAgent: Token scopes from Auth0: {token_data.get('scope')}")
                received_scopes = token_data.get("scope", "").split()
                if "read:furniture" not in received_scopes:
                    print(f"FurnitureAgent: WARNING - 'read:furniture' not in scopes: {received_scopes}")
                self.current_auth0_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                print(f"FurnitureAgent: Obtained Auth0 token, expires at {self.token_expires_at.isoformat()}.")
                return self.current_auth0_token
        except httpx.HTTPStatusError as e:
            print(f"FurnitureAgent: HTTP error obtaining token: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"FurnitureAgent: Error obtaining token: {e}")

        self.current_auth0_token = None
        self.token_expires_at = None
        return None

    async def initialize(self) -> bool:
        if self.is_initialized:
            return True

        print("FurnitureAgent: Initializing...")
        access_token = await self._get_auth0_access_token_internal()
        if not access_token:
            print("FurnitureAgent: Initialization failed - could not obtain Auth0 token.")
            return False

        self.mcp_client = MultiServerMCPClient(
            connections={
                "furniture_service": {
                    "transport": "streamable_http",
                    "url": "http://furniture_server:3000/mcp",
                    "headers": {"Authorization": f"Bearer {access_token}"},
                }
            }
        )

        try:
            tools = await self.mcp_client.get_tools(server_name="furniture_service")
            if not tools:
                print("FurnitureAgent: No tools found. Check server, token, and scopes.")
                self.current_auth0_token = None
                return False

            print(f"FurnitureAgent: Loaded tools: {[t.name for t in tools]}")
            self.agent_executor = create_react_agent(self.llm, tools)
            self.is_initialized = True
            print("FurnitureAgent: Initialized successfully.")
            return True
        except httpx.ConnectError as e:
            print(f"FurnitureAgent: Connection error loading tools: {e}")
        except McpError as e:
            print(f"FurnitureAgent: MCP error loading tools: {e.message} (code={e.code}, type={e.type})")
            if e.code in (401, 403):
                print("FurnitureAgent: Auth error detected. Invalidating token.")
                self.current_auth0_token = None
                self.token_expires_at = None
        except Exception as e:
            print(f"FurnitureAgent: Unexpected error loading tools: {e}")
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code in (401, 403):
                print("FurnitureAgent: HTTP auth error. Invalidating token.")
                self.current_auth0_token = None
                self.token_expires_at = None

        return False

    async def ask(self, messages: List[BaseMessage]) -> str:
        if not self.is_initialized:
            print("FurnitureAgent: ask() called before initialization. Reinitializing...")
            if not await self.initialize():
                return "Error: Furniture assistant is unavailable, please try again later."

        access_token = await self._get_auth0_access_token_internal()
        if not access_token:
            return "Error: Authentication issue with the furniture system."

        if self.mcp_client:
            config = self.mcp_client.connections.get("furniture_service", {})
            headers = config.get("headers", {})
            token_header = headers.get("Authorization", "")
            if token_header != f"Bearer {access_token}":
                print("FurnitureAgent: Token changed. Reinitializing connection.")
                self.is_initialized = False
                if not await self.initialize():
                    return "Error: Could not re-establish connection after token update."
        else:
            print("FurnitureAgent: No MCP client. Reinitializing...")
            self.is_initialized = False
            if not await self.initialize():
                return "Critical error: Cannot connect to furniture system."

        print(f"FurnitureAgent: Sending {len(messages)} messages. Last: '{messages[-1].content}'")
        try:
            if not self.agent_executor:
                return "Error: Agent executor not available."
            result = await self.agent_executor.ainvoke({"messages": messages})
            output_messages = result.get("messages", [])
            for msg in reversed(output_messages):
                if isinstance(msg, AIMessage):
                    return msg.content
            return "Error: No valid AI response."
        except McpError as e:
            print(f"FurnitureAgent: MCP error during invocation: {e.message} (code={e.code}, type={e.type})")
            if e.code in (401, 403):
                print("FurnitureAgent: Permission error. Invalidating token.")
                self.current_auth0_token = None
                self.token_expires_at = None
                self.is_initialized = False
                return "Error: Permission issue accessing furniture system."
            return f"Error from furniture system: {e.message}"
        except httpx.ConnectError as e:
            print(f"FurnitureAgent: Connection error during invocation: {e}")
            self.is_initialized = False
            return "Error: Cannot connect to furniture system."
        except Exception as e:
            print(f"FurnitureAgent: Unexpected error during invocation: {type(e).__name__} - {e}")
            return "Error: Unexpected error processing request."

    async def close(self):
        if self.mcp_client:
            print("FurnitureAgent: Closing MCP client.")
            self.mcp_client = None
        self.is_initialized = False
        print("FurnitureAgent: Closed.")
