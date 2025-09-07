import asyncio
from fastmcp import Client
from auth0.authentication import GetToken
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = "http://localhost:8005/mcp"

client_id = os.getenv("CIMPRESS_API_CLIENT_ID")
client_secret = os.getenv("CIMPRESS_API_CLIENT_SECRET")
CIMPRESS_AUTH0_DOMAIN = "cimpress.auth0.com"
CIMPRESS_OAUTH_AUDIENCE = "https://api.cimpress.io/"

get_token = GetToken(CIMPRESS_AUTH0_DOMAIN, client_id, client_secret)
access_token = get_token.client_credentials(CIMPRESS_OAUTH_AUDIENCE)["access_token"]

client = Client(SERVER_URL, auth=access_token)

async def call_add():
    async with client:
        result = await client.call_tool("add", {"a": 10, "b": 20})
        print("10 + 20 =", result)

if __name__ == "__main__":
    asyncio.run(call_add())
