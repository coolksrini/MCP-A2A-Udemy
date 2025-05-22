import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER = "http://127.0.0.1:3000/mcp"

async def main() -> None:
    async with streamablehttp_client(SERVER) as (read, write, get_sid):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Session ID (stateless):", get_sid())

            await session.send_ping()
            print("Ping OK")

            resource_definitions = await session.list_resources()
            list_uri = str(resource_definitions.resources[0].uri)
            print("Resource URI for listing products:", list_uri)

            tool_definitions = await session.list_tools()
            create_tool_name = tool_definitions.tools[0].name
            print("Tool name for creating products:", create_tool_name)

            all_products = await session.read_resource(list_uri)
            print("All products:", all_products.contents[0].text)

            new_product = await session.call_tool(
                create_tool_name,
                {
                    "name": "Widget",
                    "price": 19.99,
                },
            )
            print("Created product:", new_product.content[0].text)

            updated_products = await session.read_resource(list_uri)
            print("Updated products:", updated_products.contents[0].text)

if __name__ == "__main__":
    asyncio.run(main())
