from fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from auth0_provider import Auth0Provider

AUTH0_DOMAIN = "dev-ra0g3i6fh7x0s3ti.us.auth0.com"
API_AUD = "http://localhost:3000/mcp"
REQUIRED_SCOPES = ["read:add"]

provider = Auth0Provider(AUTH0_DOMAIN, API_AUD)
settings = AuthSettings(
    issuer_url=f"https://{AUTH0_DOMAIN}/",
    required_scopes=REQUIRED_SCOPES
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
    mcp.run(transport="streamable-http", host="127.0.0.1", port=3000)
