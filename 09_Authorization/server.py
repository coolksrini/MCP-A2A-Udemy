import os

from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider
from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
API_AUDIENCE = os.environ.get("API_AUDIENCE", "http://localhost:8000/mcp")
REQUIRED_SCOPES = ["read:add"]

auth = BearerAuthProvider(
    jwks_uri=f"{AUTH0_DOMAIN.rstrip('/')}/.well-known/jwks.json",
    issuer=AUTH0_DOMAIN.rstrip("/") + "/",
    audience=API_AUDIENCE,
    required_scopes=REQUIRED_SCOPES,
)

mcp = FastMCP(
    name="SecureAddServer",
    stateless_http=True,
    auth=auth,
)


@mcp.tool(description="Add two integers")
def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
