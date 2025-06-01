import uvicorn
from fastapi import FastAPI
from server import mcp

mcp_app = mcp.http_app(path="/mcp")

app = FastAPI(lifespan=mcp_app.router.lifespan_context)

app.mount("/mcpserver", mcp_app)

if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8000)
