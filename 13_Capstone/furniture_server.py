import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "").rstrip("/")
API_AUDIENCE = os.getenv("API_AUDIENCE", "")
REQUIRED_SCOPES = ["read:add"]

auth = BearerAuthProvider(
    jwks_uri=f"{AUTH0_DOMAIN}/.well-known/jwks.json",
    issuer=f"{AUTH0_DOMAIN}/",
    audience=API_AUDIENCE,
    required_scopes=REQUIRED_SCOPES,
)

server = FastMCP(
    name="FurniturePriceInfoServer",
    stateless_http=True,
    auth=auth,
)

furniture_db = [
    {"name": "Classic Wood Chair", "price": 49.99},
    {"name": "Rustic Dining Table", "price": 199.50},
    {"name": "Comfort Corner Sofa", "price": 499.00},
]

def _find_matches(fragment: str):
    q = fragment.lower()
    return [item for item in furniture_db if q in item["name"].lower()]

def _format_item(item):
    return f"{item['name']} costs ${item['price']:.2f}"

@server.tool(description="List all furniture and prices")
def list_all_furniture() -> str:
    if not furniture_db:
        return "No furniture items are available."
    return "\n".join(
        f"- {item['name']}: ${item['price']:.2f}" for item in furniture_db
    )

@server.tool(description="Get price/details for furniture by (partial) name")
def get_furniture_price(name_fragment: str) -> str:
    matches = _find_matches(name_fragment)
    if not matches:
        return "No matching furniture item found."
    if len(matches) == 1:
        return _format_item(matches[0])
    return "Multiple matches:\n" + "\n".join(
        f"- {item['name']}" for item in matches
    )

if __name__ == "__main__":
    server.run(transport="streamable-http", host="0.0.0.0", port=3000)
