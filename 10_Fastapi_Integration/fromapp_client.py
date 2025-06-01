import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

SERVER = "http://127.0.0.1:3000/mcp/"

async def main() -> None:
    async with Client(StreamableHttpTransport(SERVER)) as session:
        resources = await session.list_resources()
        list_uri = str(resources[0].uri)

        tools = await session.list_tools()
        create_tool_name = tools[0].name

        all_products = await session.read_resource(list_uri)
        print("All products:", all_products[0].text)

        created = await session.call_tool(
            create_tool_name,
            {"name": "Widget", "price": 19.99},
        )
        print("Created product:", created[0].text)

        updated_products = await session.read_resource(list_uri)
        print("Updated products:", updated_products[0].text)

if __name__ == "__main__":
    asyncio.run(main())
