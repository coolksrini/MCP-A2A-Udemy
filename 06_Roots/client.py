import asyncio
import os

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


async def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    demo_root = os.path.join(script_dir, "demo_root")
    project_root = os.path.join(demo_root, "project")

    transport = StreamableHttpTransport(url="http://127.0.0.1:8000/mcp/")

    roots = [
        # f"file://{docs_root}",
        f"file://{project_root}",
    ]

    client = Client(transport, roots=roots)

    async with client:
        result = await client.call_tool("find_file", {"filename": "helper.py"})
        print("✅ Found paths:")
        if not result:
            print("  (no matches)")
        for r in result:
            print("  -", r.text)


if __name__ == "__main__":
    asyncio.run(main())
