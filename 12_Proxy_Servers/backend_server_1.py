from fastmcp import FastMCP

legacy_backend_mcp = FastMCP(name="LegacySSEBackendAdd")

@legacy_backend_mcp.tool(description="Add two integers")
def add(a: int, b: int) -> int:
    print(f"[LegacySSEBackendAdd] add a={a} b={b}")
    return a + b

if __name__ == "__main__":
    print("Starting LegacySSEBackendAdd (SSE) on port 9001")
    legacy_backend_mcp.run(transport="sse", host="127.0.0.1", port=9001)
