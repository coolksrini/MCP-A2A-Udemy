from fastmcp import FastMCP

BACKEND_SSE_URL = "http://127.0.0.1:9001/sse"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8000

proxy = FastMCP.as_proxy(BACKEND_SSE_URL, name="ModernProxyToLegacy")

if __name__ == "__main__":
    print(f"Proxying {BACKEND_SSE_URL} → http://{PROXY_HOST}:{PROXY_PORT}/mcp (streamable-http)")
    proxy.run(
        transport="streamable-http",
        host=PROXY_HOST,
        port=PROXY_PORT,
    )
