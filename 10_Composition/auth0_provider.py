# auth0_provider.py
import httpx
from jose import jwt as jose_jwt
from mcp.server.auth.provider import OAuthAuthorizationServerProvider
from mcp.shared.auth import OAuthClientInformationFull
from mcp.server.auth.provider import AccessToken, AuthorizationCode, RefreshToken

class Auth0Provider(
    OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]
):
    def __init__(self, domain: str, audience: str):
        # Domain ohne https:// und abschließenden Slash
        # Z.B. dev-xyz.us.auth0.com
        self.jwks_url = f"https://{domain}/.well-known/jwks.json"
        self.issuer   = f"https://{domain}/"
        self.audience = audience
        self._jwks    = None

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        # wir nutzen nur Client-Credentials, darum hier keine DB-Abfrage
        return OAuthClientInformationFull(
            client_id=client_id,
            client_name=None,
            redirect_uris=[],
            grant_types=["client_credentials"],
            scopes_registered=[],
        )

    async def load_access_token(self, token: str) -> AccessToken | None:
        # JWKS einmal holen
        if self._jwks is None:
            resp = httpx.get(self.jwks_url)
            resp.raise_for_status()
            self._jwks = resp.json()["keys"]

        # Header parsen und den zugehörigen Key finden
        header = jose_jwt.get_unverified_header(token)
        key = next(k for k in self._jwks if k["kid"] == header["kid"])

        # Token verifizieren
        claims = jose_jwt.decode(
            token,
            key,
            algorithms=[header["alg"]],
            audience=self.audience,
            issuer=self.issuer
        )

        # **Nur** das scope-Claim auswerten
        scope_str = claims.get("scope", "")
        scopes = scope_str.split() if scope_str else []

        # Wenn keine Scopes drin, dann kein valides Token
        if not scopes:
            return None

        return AccessToken(
            token=token,
            client_id=claims.get("sub"),
            scopes=scopes,
            expires_at=claims.get("exp")
        )

