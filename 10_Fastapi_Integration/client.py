import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


async def main():
    transport = StreamableHttpTransport(url="http://127.0.0.1:8000/mcpserver/mcp")
    client = Client(transport=transport)

    async with client:
        result = await client.call_tool("add", {"a": 5, "b": 7})
        print("5 + 7 =", result[0].text)


if __name__ == "__main__":
    asyncio.run(main())
