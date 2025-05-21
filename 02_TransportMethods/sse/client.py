import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

SERVER_URL = "http://127.0.0.1:8000/sse"


async def main() -> None:
    async with sse_client(SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool("add", {"a": 7, "b": 5})
            print("7 + 5 =", res.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
