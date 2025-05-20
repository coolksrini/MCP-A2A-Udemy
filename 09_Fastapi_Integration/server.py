# mcp_server.py
#!/usr/bin/env python3
from fastmcp import FastMCP    # ← make sure you're importing from fastmcp, not mcp.server.fastmcp

# A completely stateless server exposing one tool under streamable‐http
mcp = FastMCP("AddServer", stateless_http=True)

@mcp.tool(description="Add two integers")
def add(a: int, b: int) -> int:
    return a + b