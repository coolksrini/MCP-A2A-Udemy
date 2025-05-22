import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

MODERN_PROXY_URL = "http://127.0.0.1:8000/mcp"

async def main():
    print(f"Connecting to Modern Proxy Server (StreamableHTTP) at: {MODERN_PROXY_URL}")

    try:
        proxy_transport = StreamableHttpTransport(url=MODERN_PROXY_URL)
    except NameError:
        print("ERROR: StreamableHttpTransport not found. Check import.")
        return

    client = Client(transport=proxy_transport)

    async with client:
        try:
            name_to_greet = "Modern HTTP User"
            print(f"\nCalling 'greet_legacy' tool (exposed by Modern Proxy) with name='{name_to_greet}'...")
            result_greet_parts = await client.call_tool("greet_legacy", {"name": name_to_greet})
            if result_greet_parts:
                print(f"Response from 'greet_legacy' via Modern Proxy: {result_greet_parts[0].text}")
            else:
                print("No response from 'greet_legacy' tool.")

            request_id_for_data = 123
            print(f"\nCalling 'get_legacy_data' tool (exposed by Modern Proxy) for ID {request_id_for_data}...")
            result_data_parts = await client.call_tool("get_legacy_data", {"request_id": request_id_for_data})
            if result_data_parts:
                print(f"Response from 'get_legacy_data' via Modern Proxy: {result_data_parts[0].text}")
            else:
                print("No response from 'get_legacy_data' tool.")

        except Exception as e:
            print(f"An error occurred while communicating with the modern proxy: {e}")
            print(f"Is the modern_proxy_server running at {MODERN_PROXY_URL}?")
            print("Is the legacy SSE backend accessible by the proxy?")

if __name__ == "__main__":
    asyncio.run(main())
