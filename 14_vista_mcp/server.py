from dataclasses import dataclass
from enum import Enum
from fastmcp import Context, FastMCP
from fastmcp.server.auth import RemoteAuthProvider, JWTVerifier
from fastmcp.server.dependencies import get_access_token, AccessToken
from dotenv import load_dotenv
import os
from auth0.authentication import GetToken
import asyncio

load_dotenv()


host = "localhost"
port = 8005
base_url = f"http://{host}:{port}/mcp"

class OAUTH_ISSUER(str, Enum):
    CIMPRESS = "https://oauth.cimpress.io/"
    AUTH0 = "https://cimpress.auth0.com/"

CIMPRESS_AUTH0_DOMAIN = "cimpress.auth0.com"
CIMPRESS_OAUTH_BASE_URL: str = "https://oauth.cimpress.io/"
CIMPRESS_OAUTH_ISSUER: str = OAUTH_ISSUER.CIMPRESS # Future will move to this eventually legacy OAuthIssuers.AUTH0
CIMPRESS_OAUTH_JWKS_URI = f"{CIMPRESS_OAUTH_BASE_URL}.well-known/jwks.json"
CIMPRESS_OAUTH_AUDIENCE = "https://api.cimpress.io/"
CIMPRESS_OAUTH_ALGORITHM = "RS256"

AUTH_TOKEN_MAX_AGE_SECONDS = 24 * 60 * 60  # 24 hours
jwt_verifier = JWTVerifier(jwks_uri=CIMPRESS_OAUTH_JWKS_URI, issuer=OAUTH_ISSUER.AUTH0, 
                          audience=CIMPRESS_OAUTH_AUDIENCE, base_url=base_url)
auth_provider = RemoteAuthProvider(token_verifier=jwt_verifier, authorization_servers=[CIMPRESS_OAUTH_BASE_URL], 
                                   base_url=base_url)

mcp = FastMCP("My Vista MCP Server", auth=jwt_verifier)

@mcp.tool
async def add(a: int, b: int, ctx: Context) -> dict:

    """Get information about the authenticated user."""
    # Get the access token (None if not authenticated)
    token: AccessToken | None = get_access_token()
    
    if token is None:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "client_id": token.client_id,
        "scopes": token.scopes,
        "expires_at": token.expires_at,
        "token_claims": token.claims,  # JWT claims or custom token data
        "result": a + b
    }

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8005)
