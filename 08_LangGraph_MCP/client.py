#!/usr/bin/env python3
import asyncio
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage


async def main():
    # 1) LLM-Instanz
    llm = ChatOpenAI(model="gpt-4o-mini")

    # 2) MultiServerMCPClient konfigurieren
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:3000/mcp",
            }
        }
    )

    tools = await client.get_tools()
    agent = create_react_agent("openai:gpt-4o-mini", tools)

    question = "How will the weather be in Munich today?"

    result = await agent.ainvoke({"messages": question})

    msgs = result["messages"]
    for m in reversed(msgs):
        if isinstance(m, AIMessage):
            print("Agent-Antwort:", m.content)
            break
    else:
        print("Keine AIMessage gefunden.")


if __name__ == "__main__":
    asyncio.run(main())
