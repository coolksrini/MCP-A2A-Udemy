import asyncio

from fastmcp import Client, FastMCP
from fastmcp.client.transports import SSETransport

LEGACY_SSE_BACKEND_URL = "http://127.0.0.1:9001/sse"


async def create_modern_proxy_instance() -> FastMCP | None:
    print(f"Creating modern proxy for legacy SSE backend at: {LEGACY_SSE_BACKEND_URL}")
    try:
        legacy_backend_client = Client(
            transport=SSETransport(url=LEGACY_SSE_BACKEND_URL)
        )
    except NameError:
        print("ERROR: SSETransport not found. Check import.")
        return None
    except Exception as e:
        print(f"ERROR creating SSETransport for backend: {e}")
        return None

    try:
        print(f"Initializing proxy client for {LEGACY_SSE_BACKEND_URL}")
        modern_proxy_mcp = FastMCP.from_client(
            legacy_backend_client, name="ModernProxyToLegacy", stateless_http=True
        )
        tools_on_proxy = await modern_proxy_mcp.get_tools()
        if not tools_on_proxy:
            print(
                f"WARNING: Proxy '{modern_proxy_mcp.name}' created but no tools were proxied."
            )
        else:
            print(
                f"Proxy '{modern_proxy_mcp.name}' created with tools: "
                f"{list(tools_on_proxy.keys())}"
            )
        return modern_proxy_mcp
    except Exception as e:
        print(f"ERROR creating proxy instance: {e}")
        return None


def main():
    print("Starting modern proxy server (StreamableHTTP) using SSE backend")
    proxy_mcp = asyncio.run(create_modern_proxy_instance())
    if proxy_mcp:
        proxy_host = "127.0.0.1"
        proxy_port = 8000
        print(
            f"Starting proxy server '{proxy_mcp.name}' "
            f"at http://{proxy_host}:{proxy_port}/mcp"
        )
        proxy_mcp.run(transport="streamable-http", host=proxy_host, port=proxy_port)
    else:
        print("Failed to start modern proxy server.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Shutting down modern proxy server.")
    except RuntimeError as e:
        if "Already running asyncio" in str(e):
            print(f"Runtime error: {e}")
        else:
            print(f"Unexpected runtime error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
