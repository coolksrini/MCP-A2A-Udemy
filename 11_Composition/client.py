import asyncio
import os

import httpx
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from mcp import McpError

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
API_AUDIENCE = os.environ["API_AUDIENCE", "http://localhost:8000/mcp"]
AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
API_AUDIENCE = os.environ["API_AUDIENCE"]
ADMIN_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
ADMIN_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
PRAKTIKANT_CLIENT_ID = os.environ["PRAKTIKANT_CLIENT_ID"]
PRAKTIKANT_CLIENT_SECRET = os.environ["PRAKTIKANT_CLIENT_SECRET"]


async def get_auth0_token(
    client_name: str, client_id: str, client_secret: str
) -> str | None:
    """
    Request an access token from Auth0 using the Client Credentials Grant.
    """
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": API_AUDIENCE,
    }
    async with httpx.AsyncClient() as http:
        print(f"[{client_name}] Requesting token from: {token_url}")
        try:
            response = await http.post(token_url, json=payload)
            response.raise_for_status()
            data = response.json()
            token = data.get("access_token")
            scopes = data.get("scope", "")
            if token:
                print(f"[{client_name}] Token obtained.")
                print(f"[{client_name}] Scopes granted: {scopes}")
                return token
            print(f"[{client_name}] No access token in response: {data}")
            return None
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            print(f"[{client_name}] Token request failed (HTTP {status}).")
            try:
                error_info = e.response.json()
                print(
                    f"[{client_name}] Auth0 error: {error_info.get('error_description', e.response.text)}"
                )
            except Exception:
                print(f"[{client_name}] Response text: {e.response.text}")
            return None
        except Exception as e:
            print(f"[{client_name}] Unexpected error during token request: {e}")
            return None


async def test_tool_call(
    client: Client,
    client_name: str,
    tool_name: str,
    params: dict,
    expected_success: bool,
):
    """
    Test a tool call and print the result or error.
    """
    print(f"[{client_name}] Calling tool '{tool_name}' with {params}")
    try:
        result = await client.call_tool(tool_name, params)
        print(f"[{client_name}] Success: {tool_name} returned: {result[0].text}")
        if not expected_success:
            print(f"[{client_name}] Warning: call succeeded but failure was expected.")
    except McpError as e:
        if expected_success:
            print(
                f"[{client_name}] Error: {tool_name} failed unexpectedly: {e.message} (code={e.code}, type={e.type})"
            )
        else:
            print(
                f"[{client_name}] Expected failure: {tool_name} failed: {e.message} (code={e.code}, type={e.type})"
            )
            if (
                e.code == 403
                or (e.type and "forbidden" in e.type.lower())
                or (e.type and "insufficient_scope" in e.type.lower())
            ):
                print(f"[{client_name}] Insufficient permissions detected.")
            else:
                print(f"[{client_name}] Unexpected MCP error. Details: {e}")
    except Exception as e:
        print(f"[{client_name}] Unexpected error during tool call '{tool_name}': {e}")


async def run_tests_for_client(client_name: str, token: str):
    """
    Run predefined tool tests for a client with the given token.
    """
    print(f"--- Running tests for {client_name} ---")
    if not token:
        print(f"[{client_name}] No token available. Skipping tests.")
        return

    transport = StreamableHttpTransport(
        url="http://127.0.0.1:3000/mcp/", headers={"Authorization": f"Bearer {token}"}
    )
    mcp_client = Client(transport)
    async with mcp_client:
        is_admin = "Admin" in client_name

        await test_tool_call(
            client=mcp_client,
            client_name=client_name,
            tool_name="adder_add",
            params={"a": 10, "b": 20},
            expected_success=True,
        )

        await test_tool_call(
            client=mcp_client,
            client_name=client_name,
            tool_name="deleter_delete_item",
            params={"item_id": f"item_for_{client_name.lower().replace(' ', '_')}"},
            expected_success=is_admin,
        )


async def main():
    print("Starting MCP client tests with different user roles...")

    admin_token = await get_auth0_token(
        client_name="Admin Client",
        client_id=ADMIN_CLIENT_ID,
        client_secret=ADMIN_CLIENT_SECRET,
    )
    await run_tests_for_client("Admin Client", admin_token)

    print("\n" + "=" * 70 + "\n")

    intern_token = await get_auth0_token(
        client_name="Intern Client",
        client_id=PRAKTIKANT_CLIENT_ID,
        client_secret=PRAKTIKANT_CLIENT_SECRET,
    )
    await run_tests_for_client("Intern Client", intern_token)

    print("All tests completed.")


if __name__ == "__main__":
    asyncio.run(main())
