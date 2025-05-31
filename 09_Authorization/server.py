import os

from auth0_provider import Auth0Provider
from fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from dotenv import load_dotenv
load_dotenv()

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
API_AUDIENCE = os.environ.get("API_AUDIENCE", "http://localhost:8000/mcp")
REQUIRED_SCOPES = ["read:add"]

provider = Auth0Provider(AUTH0_DOMAIN, API_AUDIENCE)
settings = AuthSettings(
    issuer_url=AUTH0_DOMAIN, required_scopes=REQUIRED_SCOPES
)

mcp = FastMCP(
    name="SecureAddServer",
    stateless_http=True,
    auth_server_provider=provider,
    auth=settings,
)


@mcp.tool(description="Add two integers")
def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
