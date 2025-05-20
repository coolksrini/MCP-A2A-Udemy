#!/usr/bin/env python3
import asyncio
from fastmcp import FastMCP, Context

# Stateful HTTP, damit Logs & Progress ankommen
mcp = FastMCP(
    name="ProgressDemoServer",
    stateless_http=False,
)

@mcp.tool(
    name="process_items",
    description="Verarbeitet eine Liste von Items mit Fortschrittsanzeige"
)
async def process_items(items: list[str], ctx: Context) -> list[str]:
    """Gibt für jedes Item nach einer kleinen Verzögerung das Uppercase zurück."""
    total = len(items)
    results: list[str] = []
    for i, item in enumerate(items, start=1):
        await ctx.info(f"Processing item {i}/{total}: {item}")
        await ctx.report_progress(progress=i, total=total)
        await asyncio.sleep(0.5)  # Simuliere Arbeit
        results.append(item.upper())
    return results

if __name__ == "__main__":
    # Startet Uvicorn, mountet Streamable-HTTP auf /mcp
    mcp.run(transport="streamable-http")
