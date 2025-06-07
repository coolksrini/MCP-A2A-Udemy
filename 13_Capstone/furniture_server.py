import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider

load_dotenv()

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"].rstrip("/")
API_AUDIENCE = os.environ["API_AUDIENCE"]
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

furniture_db = {
    "chair_001": {"name": "Classic Wood Chair", "price": 49.99},
    "table_001": {"name": "Rustic Dining Table", "price": 199.50},
    "sofa_001": {"name": "Comfort Corner Sofa", "price": 499.00},
}


@server.tool(description="List all furniture and prices")
def list_all_furniture() -> str:
    return (
        "\n".join(
            f"- {item['name']}: ${item['price']:.2f} (ID: {fid})"
            for fid, item in furniture_db.items()
        )
        or "No furniture items are available."
    )


@server.tool(description="Get price/details for a furniture item by ID or name")
def get_furniture_price(identifier: str) -> str:
    if identifier in furniture_db:
        itm = furniture_db[identifier]
        return f"{itm['name']} costs ${itm['price']:.2f} (ID: {identifier})"
    matches = [
        (fid, itm)
        for fid, itm in furniture_db.items()
        if identifier.lower() in itm["name"].lower()
    ]
    if not matches:
        return "No matching furniture item found."
    if len(matches) == 1:
        fid, itm = matches[0]
        return f"{itm['name']} costs ${itm['price']:.2f} (ID: {fid})"
    return "Multiple matches:\n" + "\n".join(
        f"- {itm['name']} (ID: {fid})" for fid, itm in matches
    )


if __name__ == "__main__":
    server.run(transport="streamable-http", host="0.0.0.0", port=3000)
