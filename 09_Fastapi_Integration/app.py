# app.py
#!/usr/bin/env python3
import uvicorn
from fastapi import FastAPI

from server import mcp

# export the MCP ASGI app under the internal path "/mcp"
mcp_app = mcp.http_app(path="/mcp")


app = FastAPI(lifespan=mcp_app.router.lifespan_context)

# mount the MCP app at /mcp-server so its endpoint is /mcp-server/mcp
app.mount("/mcp-server", mcp_app)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000)
