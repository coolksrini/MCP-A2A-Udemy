# auth0_provider.py
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
            async with httpx.AsyncClient() as client:
                resp = await client.get(self.jwks_url)
                resp.raise_for_status()
                self._jwks = resp.json()["keys"]
        try:
            header = jose_jwt.get_unverified_header(token)
            key = next((k for k in self._jwks if k["kid"] == header["kid"]), None)
            if key is None:
                print(f"Auth0Provider: Key ID {header.get('kid')} not found in JWKS.")
                return None
            claims = jose_jwt.decode(
                token,
                key,
                algorithms=[header["alg"]],
                audience=self.audience,
                issuer=self.issuer,
            )
        except jose_jwt.JWTError as e:
            print(f"Auth0Provider: JWTError - {e}")
            return None
        except Exception as e:
            print(f"Auth0Provider: Error decoding token - {e}")
            return None

        scope_str = claims.get("scope", "")
        scopes = scope_str.split() if scope_str else []

        return AccessToken(
            token=token,
            client_id=claims.get("sub") or claims.get("azp"),
            scopes=scopes,
            expires_at=claims.get("exp"),
        )
