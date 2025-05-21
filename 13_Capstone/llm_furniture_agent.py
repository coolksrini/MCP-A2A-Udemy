# llm_furniture_agent.py
import asyncio
import os
import httpx
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage,
)  # BaseMessage hinzugefügt
from typing import List  # Hinzugefügt
from mcp import McpError


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
            and datetime.now(timezone.utc)
            < self.token_expires_at - timedelta(minutes=1)
        ):
            return self.current_auth0_token
        print("FurnitureAgent: Requesting new Auth0 access token...")
        if not all(
            [
                self.auth0_domain,
                self.auth0_client_id,
                self.auth0_client_secret,
                self.api_audience,
            ]
        ):
            print(
                "ERROR: Auth0 M2M client credentials not fully configured in environment variables."
            )
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
                print(
                    f"FurnitureAgent: Token Scopes from Auth0: {token_data.get('scope')}"
                )
                received_scopes = token_data.get("scope", "").split()
                if (
                    "read:furniture" not in received_scopes
                ):  # Wichtig für den Furniture Server
                    print(
                        f"FurnitureAgent: WARNING - Required scope 'read:furniture' not found in received scopes: {received_scopes}"
                    )

                self.current_auth0_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.now(timezone.utc) + timedelta(
                    seconds=expires_in
                )
                print(
                    f"FurnitureAgent: Successfully obtained new Auth0 token (expires: {self.token_expires_at.isoformat()})."
                )
                return self.current_auth0_token
        except httpx.HTTPStatusError as e:
            print(
                f"FurnitureAgent: HTTP Error obtaining Auth0 token: {e.response.status_code} - {e.response.text}"
            )
            self.current_auth0_token = None
            self.token_expires_at = None
            return None
        except Exception as e:
            print(f"FurnitureAgent: Error obtaining Auth0 token: {e}")
            self.current_auth0_token = None
            self.token_expires_at = None
            return None

    async def initialize(self) -> bool:
        if self.is_initialized:
            return True

        print("FurnitureAgent: Initializing...")
        access_token = await self._get_auth0_access_token_internal()
        if not access_token:
            print("FurnitureAgent: Failed to initialize - Could not get Auth0 token.")
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
                print(
                    "FurnitureAgent: No tools found for 'furniture_service'. Check server, token, and scopes (expected 'read:furniture')."
                )
                self.current_auth0_token = None
                return False

            print(
                f"FurnitureAgent: MCP Tools loaded for 'furniture_service': {list(t.name for t in tools)}"
            )

            self.agent_executor = create_react_agent(
                self.llm,
                tools,
            )
            self.is_initialized = True
            print("FurnitureAgent: Initialized successfully.")
            return True
        except httpx.ConnectError as e:
            print(f"FurnitureAgent: ConnectError during tool loading: {e}")
            return False
        except McpError as e:
            print(
                f"FurnitureAgent: MCPError during tool loading: {e.message} (Code: {e.code}, Type: {e.type})"
            )
            if e.code == 403 or e.code == 401:
                print(
                    "FurnitureAgent: Suspected token/scope issue. Invalidating current token."
                )
                self.current_auth0_token = None
                self.token_expires_at = None
            return False
        except Exception as e:
            print(f"FurnitureAgent: General error during tool loading: {e}")
            if (
                hasattr(e, "response")
                and isinstance(e, httpx.HTTPStatusError)
                and e.response is not None
            ):
                if e.response.status_code in [401, 403]:
                    print(
                        "FurnitureAgent: Suspected token/scope issue from HTTP error. Invalidating token."
                    )
                    self.current_auth0_token = None
                    self.token_expires_at = None
            return False

    # GEÄNDERT: Die Methode akzeptiert jetzt eine Liste von BaseMessage-Objekten
    async def ask(self, messages: List[BaseMessage]) -> str:
        if not self.is_initialized:
            print(
                "FurnitureAgent: ask() called, agent not initialized. Attempting to initialize..."
            )
            initialized_now = await self.initialize()
            if not initialized_now:
                # Rückgabe eines Fehlerstrings, da die Methode einen String zurückgeben muss
                return "Error: The furniture information assistant is currently unavailable. Please try again later."

        access_token = await self._get_auth0_access_token_internal()
        if not access_token:
            return "Error: Temporary authentication issue with the furniture information system. Please try again."

        if self.mcp_client:
            connection_config = self.mcp_client.connections.get("furniture_service")
            current_bearer_in_config = ""
            if connection_config and isinstance(connection_config, dict):
                headers = connection_config.get("headers")
                if headers and isinstance(headers, dict):
                    current_bearer_in_config = headers.get("Authorization", "")

            if current_bearer_in_config != f"Bearer {access_token}":
                print("FurnitureAgent: Auth0 token has changed. Re-initializing agent.")
                self.is_initialized = False
                initialized_now = await self.initialize()
                if not initialized_now:
                    return "Error: Could not re-initialize connection to the furniture system after token update."
        else:
            print("FurnitureAgent: CRITICAL - mcp_client is None. Re-initializing.")
            self.is_initialized = False
            initialized_now = await self.initialize()
            if not initialized_now:
                return (
                    "Critical error: Furniture system client could not be established."
                )

        # Logge die empfangenen Nachrichten (oder zumindest deren Typen und Anzahl)
        print(
            f"FurnitureAgent: Asking agent with {len(messages)} messages in history. Last message: '{messages[-1].content if messages else 'N/A'}'"
        )
        try:
            if not self.agent_executor:
                print("FurnitureAgent: Agent executor not available before invoking.")
                return "Error: Agent executor not available. Initialization might have critically failed."

            # Der Agent erwartet ein Dictionary mit dem Key "messages"
            # Die gesamte Historie wird übergeben
            result = await self.agent_executor.ainvoke({"messages": messages})

            # Die Antwort des ReAct-Agenten ist in der Regel die letzte AIMessage
            # in der "messages"-Liste des Ergebnisses.
            output_messages = result.get("messages", [])
            for m in reversed(output_messages):
                if isinstance(m, AIMessage):
                    return m.content  # Nur den Content der AIMessage zurückgeben
            # Fallback, falls keine AIMessage gefunden wird (sollte nicht passieren bei erfolgreichem Aufruf)
            return "Error: Could not formulate a direct answer from the furniture information system."
        except McpError as e:
            print(
                f"FurnitureAgent: MCPError during agent invocation: {e.message} (Code: {e.code}, Type: {e.type})"
            )
            if e.code == 403 or e.code == 401:
                print(
                    "FurnitureAgent: Auth/Authz error from MCP server. Invalidating token."
                )
                self.current_auth0_token = None
                self.token_expires_at = None
                self.is_initialized = False
                return "Error: Temporary issue accessing the furniture system due to permissions. Please try again."
            return f"Error from furniture system: {e.message}"
        except httpx.ConnectError as e:
            print(f"FurnitureAgent: ConnectError during agent invocation: {e}")
            self.is_initialized = False
            return "Error: Trouble connecting to the furniture system. Please ensure it's running and try again."
        except Exception as e:
            print(
                f"FurnitureAgent: General error during agent invocation: {type(e).__name__} - {e}"
            )
            return "Error: Unexpected error while processing your request with the furniture system."

    async def close(self):
        if self.mcp_client:
            print("FurnitureAgent: Clearing MCP client reference.")
            self.mcp_client = None
        self.is_initialized = False
        print("FurnitureAgent: Closed.")
