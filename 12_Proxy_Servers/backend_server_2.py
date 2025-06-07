from fastmcp import FastMCP

legacy_backend_subtract = FastMCP(name="LegacySSEBackendSubtract")

@legacy_backend_subtract.tool(description="Subtract two integers")
def subtract(a: int, b: int) -> int:
    print(f"[LegacySSEBackendSubtract] subtract a={a} b={b}")
    return a - b

if __name__ == "__main__":
    print("Starting LegacySSEBackendSubtract (SSE) on port 9002")
    legacy_backend_subtract.run(transport="sse", host="127.0.0.1", port=9002)
