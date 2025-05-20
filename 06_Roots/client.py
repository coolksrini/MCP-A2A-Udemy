#!/usr/bin/env python3
import os
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    demo_root   = os.path.join(script_dir, "demo_root")
    docs_root   = os.path.join(demo_root, "docs")
    project_root= os.path.join(demo_root, "project")

    transport = StreamableHttpTransport(url="http://127.0.0.1:8000/mcp")

    # Roots definieren – hier einfach nach Bedarf einkommentieren:
    roots = [
        # f"file://{docs_root}",       # ⬅ in docs/ suchen
        f"file://{project_root}",       # ⬅ oder beide aktivieren
    ]

    client = Client(transport, roots=roots)

    async with client:
        result = await client.call_tool("find_file", {"filename": "helper.py"})
        print("✅ Gefundene Pfade:")
        if not result:
            print("  (keine Treffer)")
        for r in result:
            print("  -", r.text)

if __name__ == "__main__":
    asyncio.run(main())
