from mcp.server.fastmcp import FastMCP

# ► Stateful Mode (default), damit SSE funktioniert
mcp = FastMCP("Add-SSE-Server")

@mcp.tool(description="Addiere zwei ganze Zahlen")
def add(a: int, b: int) -> int:
    """Add two integers"""
    return a + b

if __name__ == "__main__":
    #  ► run over SSE transport (mount path default "/sse")
    mcp.run(transport="sse")
