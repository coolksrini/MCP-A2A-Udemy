# client.py
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    url = "http://127.0.0.1:8000/mcp"
    async with streamablehttp_client(url) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            print("Vor initialize:", get_session_id())

            await session.initialize()        

            sid = get_session_id()
            print("Session-ID nach initialize:", sid)

            result = await session.call_tool("add", {"a": 21, "b": 21})
            print("Ergebnis vom Server:", result)

if __name__ == "__main__":
    asyncio.run(main())
