# api_server.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Literal, Union  # Hinzugefügt
from contextlib import asynccontextmanager
import uvicorn

from llm_furniture_agent import FurnitureAgent
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage  # Hinzugefügt


# --- Neue Pydantic Modelle für die API-Schicht ---
class ApiMessage(BaseModel):
    role: Literal["human", "ai", "system"]  # "system" hinzugefügt, falls mal benötigt
    content: str


class AskWithHistoryRequest(BaseModel):
    messages: List[ApiMessage] = Field(
        ..., min_length=1
    )  # Stelle sicher, dass mindestens eine Nachricht vorhanden ist


# Das Response-Modell bleibt gleich, da wir nur den Inhalt der letzten AI-Antwort zurückgeben
class AskResponse(BaseModel):
    answer: str


# --- Hilfsfunktion zur Konvertierung ---
def convert_api_messages_to_langchain(
    api_messages: List[ApiMessage],
) -> List[BaseMessage]:
    lc_messages: List[BaseMessage] = []
    for msg in api_messages:
        if msg.role == "human":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "ai":
            lc_messages.append(AIMessage(content=msg.content))
        # elif msg.role == "system": # Systemnachrichten werden i.d.R. am Anfang des Prompts vom Agenten selbst gehandhabt
        #     lc_messages.append(SystemMessage(content=msg.content)) # Für den ReAct-Agent ist das nicht typisch als Teil der User-Historie
        else:
            # Fallback oder Fehler, falls unerwarteter Rollentyp kommt
            print(
                f"Warning: Unknown message role '{msg.role}' encountered. Skipping message."
            )
    return lc_messages


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("API Lifespan: Initializing FurnitureAgent...")
    agent = FurnitureAgent()
    initialized_successfully = await agent.initialize()
    if not initialized_successfully:
        print(
            "API Lifespan: CRITICAL - FurnitureAgent failed to initialize during startup."
        )
        app.state.furniture_agent = None
    else:
        app.state.furniture_agent = agent
        print("API Lifespan: FurnitureAgent initialized and attached to app.state.")

    yield

    current_agent = getattr(app.state, "furniture_agent", None)
    if current_agent:
        print("API Lifespan: Shutting down, closing FurnitureAgent...")
        await current_agent.close()
        print("API Lifespan: FurnitureAgent closed.")
    else:
        print(
            "API Lifespan: Shutting down, no active FurnitureAgent to close or it was never initialized."
        )


app = FastAPI(
    title="Minimal Furniture Info Agent API with History", lifespan=lifespan
)  # Titel angepasst


@app.post("/ask", response_model=AskResponse)
async def ask_agent_endpoint(
    request_data: AskWithHistoryRequest, fastapi_request: Request
):  # Request-Modell geändert
    agent: FurnitureAgent | None = getattr(
        fastapi_request.app.state, "furniture_agent", None
    )

    if not agent or not agent.is_initialized:
        print("API /ask: FurnitureAgent not available or not initialized.")
        raise HTTPException(
            status_code=503,
            detail="The furniture information assistant is currently unavailable.",
        )

    if not request_data.messages:  # Prüfung bleibt, auch wenn min_length=1 gesetzt ist
        raise HTTPException(status_code=400, detail="Messages list cannot be empty.")

    # Konvertiere die API-Nachrichten in Langchain BaseMessage-Objekte
    try:
        langchain_messages = convert_api_messages_to_langchain(request_data.messages)
        if not langchain_messages:  # Falls alle Nachrichten ungültige Rollen hatten
            raise HTTPException(
                status_code=400,
                detail="No valid messages provided in the list after conversion.",
            )
    except Exception as e:
        print(f"API /ask: Error converting API messages: {e}")
        raise HTTPException(
            status_code=400, detail="Invalid message format in the request."
        )

    try:
        # Der Agent erwartet jetzt die gesamte Liste der Nachrichten
        answer_content = await agent.ask(langchain_messages)
        return AskResponse(answer=answer_content)
    except Exception as e:
        print(f"API /ask: Error during agent.ask(): {e}")
        # Hier könnte man spezifischere Fehlercodes für Agentenfehler zurückgeben
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your request with the agent.",
        )


if __name__ == "__main__":
    print("Starting Minimal API server for Furniture Agent with History support...")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
