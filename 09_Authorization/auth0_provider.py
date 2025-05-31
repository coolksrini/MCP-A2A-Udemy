import httpx
from jose import jwt as jose_jwt
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    OAuthAuthorizationServerProvider,
    RefreshToken,
)
from mcp.shared.auth import OAuthClientInformationFull


class Auth0Provider(
    OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]
):
    def __init__(self, domain: str, audience: str):
        self.jwks_url = f"https://{domain}/.well-known/jwks.json"
        self.issuer = f"https://{domain}/"
        self.audience = audience
        self._jwks = None

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return OAuthClientInformationFull(
            client_id=client_id,
            client_name=None,
            redirect_uris=[],
            grant_types=["client_credentials"],
            scopes_registered=[],
        )

    async def load_access_token(self, token: str) -> AccessToken | None:
        if self._jwks is None:
            response = httpx.get(self.jwks_url)
            response.raise_for_status()
            self._jwks = response.json()["keys"]

        header = jose_jwt.get_unverified_header(token)
        key = next(k for k in self._jwks if k["kid"] == header["kid"])

        claims = jose_jwt.decode(
            token,
            key,
            algorithms=[header["alg"]],
            audience=self.audience,
            issuer=self.issuer,
        )

        scope_str = claims.get("scope", "")
        scopes = scope_str.split() if scope_str else []

        if not scopes:
            return None

        return AccessToken(
            token=token,
            client_id=claims.get("sub"),
            scopes=scopes,
            expires_at=claims.get("exp"),
        )
