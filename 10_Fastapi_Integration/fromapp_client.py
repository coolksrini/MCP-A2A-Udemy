import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER = "http://127.0.0.1:3000/mcp"

async def main() -> None:
    async with streamablehttp_client(SERVER) as (read, write, get_sid):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("⧉ Session ID (stateless):", get_sid(), "\n")

            await session.send_ping()
            print("✅ Ping OK\n")

            res_defs = await session.list_resources()
            list_uri = str(res_defs.resources[0].uri)
            print("📂 Discovered resource URI for listing products:", list_uri)

            tool_defs = await session.list_tools()
            create_tool = tool_defs.tools[0].name
            print("🔧 Discovered tool name for creating products:", create_tool, "\n")

            all_prod = await session.read_resource(list_uri)
            print("📦 All products:", all_prod.contents[0].text, "\n")

            new_prod = await session.call_tool(
                create_tool,
                {
                    "name": "Widget",
                    "price": 19.99,
                },
            )
            print("➕ Created product:", new_prod.content[0].text, "\n")

            updated = await session.read_resource(list_uri)
            print("🔄 Updated products:", updated.contents[0].text)

if __name__ == "__main__":
    asyncio.run(main())
