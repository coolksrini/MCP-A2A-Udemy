# client.py
#!/usr/bin/env python3
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def main():
    # point at the FastAPI‐mounted endpoint
    transport = StreamableHttpTransport(
        url="http://127.0.0.1:8000/mcp-server/mcp"
    )
    client = Client(transport=transport)

    async with client:
        # call your single 'add' tool
        result = await client.call_tool("add", {"a": 5, "b": 7})
        print("5 + 7 =", result[0].text)

if __name__ == "__main__":
    asyncio.run(main())
