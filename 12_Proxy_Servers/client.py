import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

PROXY_URL = "http://127.0.0.1:8000/mcp/"

async def main():
    print(f"Connecting to proxy at {PROXY_URL}")
    client = Client(transport=StreamableHttpTransport(url=PROXY_URL))

    async with client:
        print("Calling add")
        res_add = await client.call_tool("add_add", {"a": 7, "b": 5})
        if res_add:
            print(f"add response: {res_add[0].text}")

        print("Calling subtract")
        res_sub = await client.call_tool("subtract_subtract", {"a": 7, "b": 5})
        if res_sub:
            print(f"subtract response: {res_sub[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
