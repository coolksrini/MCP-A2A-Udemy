from fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from auth0_provider import Auth0Provider

AUTH0_DOMAIN = "dev-ra0g3i6fh7x0s3ti.us.auth0.com"
API_AUD = "http://localhost:3000/mcp"

auth0_provider = Auth0Provider(AUTH0_DOMAIN, API_AUD)

add_scopes = ["read:add"]
add_auth_settings = AuthSettings(
    issuer_url=f"https://{AUTH0_DOMAIN}/",
    required_scopes=add_scopes
)
add_server = FastMCP(
    name="AddService",
    stateless_http=True,
    auth_server_provider=auth0_provider,
    auth=add_auth_settings,
)

@add_server.tool(description="Add two integers")
def add(a: int, b: int) -> int:
    print(f"Executing add tool with a={a}, b={b}")
    return a + b

delete_scopes = ["admin:delete"]
delete_auth_settings = AuthSettings(
    issuer_url=f"https://{AUTH0_DOMAIN}/",
    required_scopes=delete_scopes
)
delete_server = FastMCP(
    name="DeleteService",
    stateless_http=True,
    auth_server_provider=auth0_provider,
    auth=delete_auth_settings,
)

@delete_server.tool(description="Simulate deleting an item")
def delete_item(item_id: str) -> str:
    print(f"Executing delete_item tool for item_id={item_id}")
    return f"Item '{item_id}' was 'deleted' successfully."

main_mcp = FastMCP(
    name="MainAppServer",
    stateless_http=True,
)

main_mcp.mount("adder", add_server)
main_mcp.mount("deleter", delete_server)

if __name__ == "__main__":
    print("Starting MainAppServer with mounted services.")
    print(f"AddService requires scopes: {add_scopes}")
    print(f"DeleteService requires scopes: {delete_scopes}")
    print(f"Auth0 Provider configured for domain: {AUTH0_DOMAIN}, audience: {API_AUD}")
    main_mcp.run(transport="streamable-http", host="127.0.0.1", port=3000)
