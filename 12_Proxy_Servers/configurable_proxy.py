from fastmcp import FastMCP

config = {
    "mcpServers": {
        "add": {
            "url": "http://127.0.0.1:9001/sse",
            "transport": "sse"
        },
        "subtract": {
            "url": "http://127.0.0.1:9002/sse",
            "transport": "sse"
        }
    }
}

proxy = FastMCP.as_proxy(config, name="ModernProxyToLegacy")

if __name__ == "__main__":
    print("starting proxy on port 8000")
    proxy.run(transport="streamable-http", host="127.0.0.1", port=8000)
