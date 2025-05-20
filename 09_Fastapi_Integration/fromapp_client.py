#!/usr/bin/env python3
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER = "http://127.0.0.1:3000/mcp"

async def main() -> None:
    # ────────── open a streamable-HTTP transport ──────────
    async with streamablehttp_client(SERVER) as (read, write, get_sid):
        # ────────── open an MCP session ──────────
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("⧉ Session-ID (stateless):", get_sid(), "\n")

            # ────────── ping / liveness ──────────
            await session.send_ping()
            print("✅ Ping OK\n")

            # ────────── discover your resources ──────────
            res_defs = await session.list_resources()
            list_uri = str(res_defs.resources[0].uri)
            print("📂 discovered resource URI for listing products:", list_uri)

            # ────────── discover your tools ──────────
            tool_defs = await session.list_tools()
            create_tool = tool_defs.tools[0].name
            print("🔧 discovered tool name for creating products:", create_tool, "\n")

            # ── 1) fetch all products ───────────────────────────
            all_prod = await session.read_resource(list_uri)
            print("📦 All products:", all_prod.contents[0].text, "\n")

            # ── 2) create a new product (flattened args!) ──────
            new_prod = await session.call_tool(
                create_tool,
                {
                    "name": "Widget",      # <— pass these at top level
                    "price": 19.99
                }
            )
            print("➕ Created product:", new_prod.content[0].text, "\n")

            # ── 3) fetch updated list ───────────────────────────
            updated = await session.read_resource(list_uri)
            print("🔄 Updated products:", updated.contents[0].text)

if __name__ == "__main__":
    asyncio.run(main())
