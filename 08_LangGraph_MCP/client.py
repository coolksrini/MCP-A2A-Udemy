import asyncio

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()


async def main():
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:3000/mcp/",
            }
        }
    )

    tools = await client.get_tools()
    agent = create_react_agent("openai:gpt-4o-mini", tools)

    question = "How will the weather be in Munich today?"

    result = await agent.ainvoke({"messages": question})

    messages = result["messages"]
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            print("Agent response:", msg.content)
            break
    else:
        print("No AIMessage found.")


if __name__ == "__main__":
    asyncio.run(main())
