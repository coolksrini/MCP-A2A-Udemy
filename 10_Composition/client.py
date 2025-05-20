#!/usr/bin/env python3
import asyncio
import httpx

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from mcp import McpError

# --- Auth0-Einstellungen ---
AUTH0_DOMAIN = "dev-ra0g3i6fh7x0s3ti.us.auth0.com" # Dein Auth0 Domain
API_AUDIENCE = "http://localhost:3000/mcp"      # Deine API Audience

# --- Admin Client (sollte 'read:add' UND 'admin:delete' Scopes in Auth0 haben) ---
ADMIN_CLIENT_ID = "7En3BDIRwLL3QFs2FtyJ9R1uyW7ESFPq"
ADMIN_CLIENT_SECRET = "ozZ1zFJaKtvzKMsjwNFNGykjiISCBCB122Qh-eVpKHwN4PzwWWTmQPpRnHDVMZvB"

# --- Praktikant Client (sollte NUR 'read:add' Scope in Auth0 haben) ---
PRAKTIKANT_CLIENT_ID = "DnqGPEVTOqpv5SD89ubDIAycCY8FuoJ2"
PRAKTIKANT_CLIENT_SECRET = "3S87FstudnXLdngJOR9D19gtZPzBSkyvAqqqp21ZLB7cagH6uQNavI76mEK9DkHw"

async def get_auth0_token(client_name: str, client_id: str, client_secret: str) -> str | None:
    """
    Fordert per Client-Credentials-Grant ein Access-Token von Auth0 an.
    """
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type":    "client_credentials",
        "client_id":     client_id,
        "client_secret": client_secret,
        "audience":      API_AUDIENCE
    }
    async with httpx.AsyncClient() as http:
        print(f"\n[{client_name}] Token-Anfrage an: {token_url}")
        print(f"[{client_name}] Client ID: {client_id[:4]}...{client_id[-4:]}, Audience: {API_AUDIENCE}")
        try:
            resp = await http.post(token_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            token = data.get("access_token")
            scopes = data.get("scope", "N/A")
            if token:
                print(f"[{client_name}] ✅ Token erfolgreich erhalten.")
                print(f"[{client_name}]   Zugewiesene Scopes im Token: {scopes}")
                return token
            else:
                print(f"[{client_name}] ❌ Fehler: Kein Access Token in der Antwort gefunden.")
                print(f"[{client_name}]   Antwort: {data}")
                return None
        except httpx.HTTPStatusError as e:
            print(f"[{client_name}] ❌ Fehler bei der Token-Anfrage (HTTP {e.response.status_code}):")
            try:
                error_details = e.response.json()
                print(f"[{client_name}]   Auth0 Fehlermeldung: {error_details.get('error_description', e.response.text)}")
            except Exception:
                print(f"[{client_name}]   Antwort (Text): {e.response.text}")
            return None
        except Exception as e:
            print(f"[{client_name}] ❌ Unerwarteter Fehler bei der Token-Anfrage: {e}")
            return None

async def test_tool_call(client: Client, client_name: str, tool_name: str, params: dict, expected_success: bool):
    """Hilfsfunktion zum Testen eines Tool-Aufrufs und zur Ausgabe der Ergebnisse."""
    print(f"\n[{client_name}] Aufruf von Tool '{tool_name}' mit Parametern: {params}")
    try:
        result = await client.call_tool(tool_name, params)
        print(f"[{client_name}] ✅ ERFOLG: '{tool_name}' Ergebnis: {result[0].text}")
        if not expected_success:
            print(f"[{client_name}] ⚠️ WARNUNG: Erfolg war nicht erwartet für '{tool_name}'. Überprüfe die Scopes!")
    except McpError as e: # Korrigierter Exception-Typ
        if expected_success:
            print(f"[{client_name}] ❌ FEHLER (MCP): '{tool_name}' fehlgeschlagen, obwohl Erfolg erwartet wurde: {e.message} (Code: {e.code}, Typ: {e.type})")
        else:
            print(f"[{client_name}] ✅ ERWARTETER FEHLER (MCP): '{tool_name}' korrekt fehlgeschlagen: {e.message} (Code: {e.code}, Typ: {e.type})")
            # McpError hat 'code' (oft HTTP Status) und 'type' (z.B. 'forbidden')
            if e.code == 403 or (e.type and "forbidden" in e.type.lower()) or (e.type and "insufficient_scope" in e.type.lower()):
                 print(f"[{client_name}]   Dies deutet korrekt auf fehlende Berechtigungen hin.")
            else:
                 print(f"[{client_name}]   Unerwarteter MCP Fehlercode/Typ. Überprüfe Server Logs. Details: {e}")
    except Exception as e:
        print(f"[{client_name}] ❌ FEHLER (Allgemein): Unerwarteter Fehler bei Aufruf von '{tool_name}': {e}")

async def run_tests_for_client(client_name: str, token: str):
    """Führt die definierten Tool-Tests für einen Client mit einem gegebenen Token durch."""
    print(f"\n--- Testdurchlauf für: {client_name} ---")
    if not token:
        print(f"[{client_name}] Kein Token vorhanden. Tests werden übersprungen.")
        return

    transport = StreamableHttpTransport(
        url="http://127.0.0.1:3000/mcp",
        headers={"Authorization": f"Bearer {token}"}
    )
    mcp_client = Client(transport)
    async with mcp_client:
        is_admin_client = "Admin" in client_name

        await test_tool_call(
            client=mcp_client,
            client_name=client_name,
            tool_name="adder_add",
            params={"a": 10, "b": 20},
            expected_success=True
        )

        await test_tool_call(
            client=mcp_client,
            client_name=client_name,
            tool_name="deleter_delete_item",
            params={"item_id": f"item_for_{client_name.lower().replace(' ', '_')}"},
            expected_success=is_admin_client
        )

async def main():
    print("Starte MCP Client Tests mit verschiedenen Benutzerrollen...")

    admin_token = await get_auth0_token(
        client_name="Admin Client",
        client_id=ADMIN_CLIENT_ID,
        client_secret=ADMIN_CLIENT_SECRET
    )
    await run_tests_for_client("Admin Client", admin_token)

    print("\n" + "="*70 + "\n")

    praktikant_token = await get_auth0_token(
        client_name="Praktikant Client",
        client_id=PRAKTIKANT_CLIENT_ID,
        client_secret=PRAKTIKANT_CLIENT_SECRET
    )
    await run_tests_for_client("Praktikant Client", praktikant_token)

    print("\nAlle Tests abgeschlossen.")

if __name__ == "__main__":
    asyncio.run(main())