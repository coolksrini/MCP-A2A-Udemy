from contextlib import asynccontextmanager
from typing import List, Literal

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from pydantic import BaseModel, Field

from llm_furniture_agent import FurnitureAgent


class ApiMessage(BaseModel):
    role: Literal["human", "ai", "system"]
    content: str


class AskWithHistoryRequest(BaseModel):
    messages: List[ApiMessage] = Field(..., min_length=1)


class AskResponse(BaseModel):
    answer: str


def to_langchain(messages: List[ApiMessage]) -> List[BaseMessage]:
    out: List[BaseMessage] = []
    for m in messages:
        if m.role == "human":
            out.append(HumanMessage(content=m.content))
        elif m.role == "ai":
            out.append(AIMessage(content=m.content))
    return out


@asynccontextmanager
async def lifespan(app: FastAPI):
    agent = FurnitureAgent()
    await agent.initialize()
    app.state.furniture_agent = agent
    try:
        yield
    finally:
        await agent.close()


app = FastAPI(
    title="Furniture Info Agent API (with history)",
    lifespan=lifespan,
)


@app.post("/ask", response_model=AskResponse)
async def ask_agent(
    payload: AskWithHistoryRequest,
    request: Request,
):
    agent: FurnitureAgent = request.app.state.furniture_agent  # type: ignore

    if not agent.is_initialized:
        raise HTTPException(
            status_code=503,
            detail="Furniture assistant is currently unavailable.",
        )

    lc_msgs = to_langchain(payload.messages)
    if not lc_msgs:
        raise HTTPException(status_code=400, detail="No valid messages in request.")

    try:
        answer = await agent.ask(lc_msgs)
        return AskResponse(answer=answer)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error while processing request: {exc}",
        ) from exc


if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000)
