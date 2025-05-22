from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Literal, Union
from contextlib import asynccontextmanager
import uvicorn

from llm_furniture_agent import FurnitureAgent
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

class ApiMessage(BaseModel):
    role: Literal["human", "ai", "system"]
    content: str

class AskWithHistoryRequest(BaseModel):
    messages: List[ApiMessage] = Field(..., min_length=1)

class AskResponse(BaseModel):
    answer: str

def convert_api_messages_to_langchain(api_messages: List[ApiMessage]) -> List[BaseMessage]:
    lc_messages: List[BaseMessage] = []
    for msg in api_messages:
        if msg.role == "human":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "ai":
            lc_messages.append(AIMessage(content=msg.content))
        else:
            print(f"Warning: Unknown message role '{msg.role}' encountered. Skipping message.")
    return lc_messages

@asynccontextmanager
async def lifespan(app: FastAPI):
    agent = FurnitureAgent()
    initialized = await agent.initialize()
    if initialized:
        app.state.furniture_agent = agent
    else:
        app.state.furniture_agent = None

    yield

    current_agent = getattr(app.state, "furniture_agent", None)
    if current_agent:
        await current_agent.close()

app = FastAPI(title="Minimal Furniture Info Agent API with History", lifespan=lifespan)

@app.post("/ask", response_model=AskResponse)
async def ask_agent_endpoint(request_data: AskWithHistoryRequest, fastapi_request: Request):
    agent: FurnitureAgent | None = getattr(fastapi_request.app.state, "furniture_agent", None)

    if not agent or not agent.is_initialized:
        raise HTTPException(
            status_code=503,
            detail="The furniture information assistant is currently unavailable."
        )

    if not request_data.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty.")

    langchain_messages = convert_api_messages_to_langchain(request_data.messages)
    if not langchain_messages:
        raise HTTPException(
            status_code=400,
            detail="No valid messages provided in the list after conversion."
        )

    try:
        answer_content = await agent.ask(langchain_messages)
        return AskResponse(answer=answer_content)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your request with the agent."
        )

if __name__ == "__main__":
    print("Starting Minimal API server for Furniture Agent with History support...")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
