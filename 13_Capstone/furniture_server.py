# furniture_server.py
import datetime
from fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from auth0_provider import Auth0Provider

# --- Auth0 Konfiguration (bleibt gleich) ---
AUTH0_DOMAIN = "dev-ra0g3i6fh7x0s3ti.us.auth0.com"
API_AUDIENCE = "http://localhost:3000/mcp"
REQUIRED_SCOPES = ["read:furniture"]

# --- Fiktive Möbel-Datenbank ---
# Struktur: { "produkt_id": {"name": "Produktname", "preis": 123.45, "kategorie": "...", "beschreibung": "..."} }
furniture_db = {
    "chair_001": {
        "name": "Klassischer Holzstuhl",
        "price": 49.99,
        "category": "Stühle",
        "description": "Ein robuster Stuhl aus Eichenholz.",
    },
    "table_001": {
        "name": "Esstisch 'Rustikal'",
        "price": 199.50,
        "category": "Tische",
        "description": "Großer Esstisch für bis zu 6 Personen.",
    },
    "sofa_001": {
        "name": "Bequemes Ecksofa",
        "price": 499.00,
        "category": "Sofas",
        "description": "Modernes Ecksofa mit Stoffbezug.",
    },
    "shelf_001": {
        "name": "Bücherregal 'Bibliothek'",
        "price": 89.90,
        "category": "Regale",
        "description": "Hohes Regal mit viel Stauraum.",
    },
    "lamp_001": {
        "name": "Designer Stehlampe",
        "price": 75.00,
        "category": "Beleuchtung",
        "description": "Elegante Stehlampe für gemütliches Licht.",
    },
    "desk_001": {
        "name": "Schreibtisch 'Minimalist'",
        "price": 120.00,
        "category": "Tische",
        "description": "Schlichter Schreibtisch mit Schublade.",
    },
}

# --- FastMCP Server Setup ---
auth0_mcp_provider = Auth0Provider(AUTH0_DOMAIN, API_AUDIENCE)
auth_settings = AuthSettings(
    issuer_url=f"https://{AUTH0_DOMAIN}/", required_scopes=REQUIRED_SCOPES
)

furniture_mcp = FastMCP(
    name="FurniturePriceInfoServer",
    stateless_http=True,
    auth_server_provider=auth0_mcp_provider,
    auth=auth_settings,
)


@furniture_mcp.tool(
    description="Lists all available furniture items with their names and prices."
)
def list_all_furniture() -> str:
    """
    Gibt eine Liste aller Möbelstücke mit Namen und Preisen zurück.
    """
    print("[FurnitureServer] list_all_furniture called.")
    if not furniture_db:
        return "Currently, no furniture items are listed."

    response_parts = ["Here are the available furniture items and their prices:"]
    for item_id, details in furniture_db.items():
        response_parts.append(
            f"- {details['name']}: ${details['price']:.2f} (ID: {item_id})"
        )

    return "\n".join(response_parts)


@furniture_mcp.tool(
    description="Gets the price and details for a specific furniture item by its name or ID. If searching by name, it will try to find the best match."
)
def get_furniture_price(identifier: str) -> str:
    """
    Ruft Preis und Details für ein bestimmtes Möbelstück anhand des Namens oder der ID ab.
    """
    print(f"[FurnitureServer] get_furniture_price called with identifier: {identifier}")

    # Zuerst prüfen, ob der Identifier eine bekannte ID ist
    if identifier in furniture_db:
        details = furniture_db[identifier]
        return f"The price for '{details['name']}' (ID: {identifier}) is ${details['price']:.2f}. Description: {details.get('description', 'N/A')}"

    # Wenn keine ID, versuche eine Namenssuche (einfache Teilstring-Suche, case-insensitive)
    identifier_lower = identifier.lower()
    found_items = []
    for item_id, details in furniture_db.items():
        if identifier_lower in details["name"].lower():
            found_items.append({"id": item_id, "details": details})

    if not found_items:
        return f"Sorry, I could not find any furniture item matching '{identifier}'."

    if len(found_items) == 1:
        item = found_items[0]
        return f"The price for '{item['details']['name']}' (ID: {item['id']}) is ${item['details']['price']:.2f}. Description: {item['details'].get('description', 'N/A')}"
    else:
        # Mehrere Treffer, gib eine Auswahl zurück
        response_parts = [
            f"I found multiple items matching '{identifier}'. Please be more specific or use the ID:"
        ]
        for item in found_items:
            response_parts.append(
                f"- {item['details']['name']}: ${item['details']['price']:.2f} (ID: {item['id']})"
            )
        return "\n".join(response_parts)


if __name__ == "__main__":
    print(
        f"Starting Furniture Price Info Server ({furniture_mcp.name}) on http://127.0.0.1:3000/mcp"
    )
    print(f"This server requires an Auth0 token with the scope(s): {REQUIRED_SCOPES}")
    furniture_mcp.run(transport="streamable-http", host="0.0.0.0", port=3000)
