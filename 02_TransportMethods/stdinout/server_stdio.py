from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Add-STDIO-Server")          # sessions are irrelevant for stdio


@mcp.tool(description="Addiere zwei ganze Zahlen")
def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    # ► run over the process’ stdin/stdout pipes
    mcp.run(transport="stdio")
