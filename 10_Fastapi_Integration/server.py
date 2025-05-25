from fastmcp import FastMCP

mcp = FastMCP("AddServer", stateless_http=True)


@mcp.tool(description="Add two integers")
def add(a: int, b: int) -> int:
    return a + b
