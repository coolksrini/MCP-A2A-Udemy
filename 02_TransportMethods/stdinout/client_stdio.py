# client_stdio.py
import asyncio
import sys
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def main() -> None:
    # 1) Konfiguration, mit der stdio_client den Server-Subprozess selbst startet
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server_stdio.py"],
        env=None,
    )

    # 2) stdio_client startet den Prozess und verbindet stdin/stdout
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()              # Handshake

            # 3) Tool aufrufen
            res = await session.call_tool("add", {"a": 7, "b": 5})
            print("7 + 5 =", res.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
