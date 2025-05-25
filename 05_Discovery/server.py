import asyncio

from fastmcp import Context, FastMCP


class DynamicToolProvider:
    @classmethod
    def dynamic_method(cls, text: str) -> str:
        return f"Dynamic tool processed: {text.upper()}"


mcp = FastMCP(name="Progress Demo Server")


@mcp.tool(
    name="process_items",
    description="Processes a list of items with progress updates and dynamic tool modification",
)
async def process_items(items: list[str], ctx: Context) -> list[str]:
    total = len(items)
    results: list[str] = []
    await ctx.info(f"Starting processing of {total} items.")
    for i, item in enumerate(items, start=1):
        await ctx.info(f"Processing item {i}/{total}: {item}")
        await ctx.report_progress(progress=i, total=total)
        await asyncio.sleep(0.5)
        results.append(item.upper())

    await ctx.info("Item processing completed.")
    await asyncio.sleep(1)

    tool_name_dynamic = "dynamic_tool_on_the_fly"
    await ctx.info(f"Adding dynamic tool: '{tool_name_dynamic}'")
    ctx.fastmcp.add_tool(DynamicToolProvider.dynamic_method, name=tool_name_dynamic)

    await asyncio.sleep(3)

    await ctx.info(f"Attempting to remove dynamic tool: '{tool_name_dynamic}'")
    try:
        ctx.fastmcp.remove_tool(tool_name_dynamic)
        await ctx.info(f"Dynamic tool '{tool_name_dynamic}' removed successfully.")
    except AttributeError:
        await ctx.error(
            "Error: 'remove_tool' is not available in this FastMCP version. Please use FastMCP >= 2.3.4."
        )
    except Exception as e:
        await ctx.error(
            f"Unexpected error while removing tool '{tool_name_dynamic}': {e}"
        )

    return results


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000)
