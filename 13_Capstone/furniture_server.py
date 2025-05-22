import datetime
from fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from auth0_provider import Auth0Provider

AUTH0_DOMAIN = "dev-ra0g3i6fh7x0s3ti.us.auth0.com"
API_AUDIENCE = "http://localhost:3000/mcp"
REQUIRED_SCOPES = ["read:furniture"]

furniture_db = {
    "chair_001": {
        "name": "Classic Wood Chair",
        "price": 49.99,
        "category": "Chairs",
        "description": "A sturdy oak chair.",
    },
    "table_001": {
        "name": "Rustic Dining Table",
        "price": 199.50,
        "category": "Tables",
        "description": "Large table for up to six people.",
    },
    "sofa_001": {
        "name": "Comfort Corner Sofa",
        "price": 499.00,
        "category": "Sofas",
        "description": "Modern fabric corner sofa.",
    },
    "shelf_001": {
        "name": "Library Bookshelf",
        "price": 89.90,
        "category": "Shelves",
        "description": "Tall shelf with ample storage.",
    },
    "lamp_001": {
        "name": "Designer Floor Lamp",
        "price": 75.00,
        "category": "Lighting",
        "description": "Elegant lamp for cozy lighting.",
    },
    "desk_001": {
        "name": "Minimalist Desk",
        "price": 120.00,
        "category": "Tables",
        "description": "Sleek desk with a drawer.",
    },
}

auth0_provider = Auth0Provider(AUTH0_DOMAIN, API_AUDIENCE)
auth_settings = AuthSettings(
    issuer_url=f"https://{AUTH0_DOMAIN}/",
    required_scopes=REQUIRED_SCOPES
)

furniture_mcp = FastMCP(
    name="FurniturePriceInfoServer",
    stateless_http=True,
    auth_server_provider=auth0_provider,
    auth=auth_settings,
)

@furniture_mcp.tool(
    description="Provide a list of all furniture items along with their prices."
)
def list_all_furniture() -> str:
    """
    Compiles a summary of every furniture item and its price.
    """
    print("[FurniturePriceInfoServer] Running list_all_furniture.")
    if not furniture_db:
        return "No furniture items are currently available."

    output = ["Available furniture and their prices:"]
    for item_id, item in furniture_db.items():
        output.append(f"- {item['name']}: ${item['price']:.2f} (ID: {item_id})")
    return "\n".join(output)

@furniture_mcp.tool(
    description="Retrieve details and price for a specific furniture item by ID or name."
)
def get_furniture_price(identifier: str) -> str:
    """
    Looks up and returns price and description for the specified furniture item.
    """
    print(f"[FurniturePriceInfoServer] Running get_furniture_price for '{identifier}'.")
    if identifier in furniture_db:
        item = furniture_db[identifier]
        return (
            f"'{item['name']}' (ID: {identifier}) costs ${item['price']:.2f}. "
            f"Details: {item.get('description', 'No description available')}."
        )

    key = identifier.lower()
    matches = [
        (item_id, info)
        for item_id, info in furniture_db.items()
        if key in info["name"].lower()
    ]

    if not matches:
        return f"Could not find any furniture matching '{identifier}'."

    if len(matches) == 1:
        item_id, item = matches[0]
        return (
            f"'{item['name']}' (ID: {item_id}) costs ${item['price']:.2f}. "
            f"Details: {item.get('description', 'No description available')}."
        )

    output = [f"Multiple items match '{identifier}'. Please specify an ID:"]
    for item_id, item in matches:
        output.append(f"- {item['name']}: ${item['price']:.2f} (ID: {item_id})")
    return "\n".join(output)

if __name__ == "__main__":
    print(
        f"Starting {furniture_mcp.name} at http://0.0.0.0:3000/mcp"
    )
    print(
        f"Required Auth0 scope(s): {REQUIRED_SCOPES}"
    )
    furniture_mcp.run(transport="streamable-http", host="0.0.0.0", port=3000)
