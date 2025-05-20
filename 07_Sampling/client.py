#!/usr/bin/env python3
import asyncio
from dotenv import load_dotenv

load_dotenv()

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.sampling import SamplingMessage, SamplingParams, RequestContext

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

async def sampling_handler(
    messages: list[SamplingMessage],
    params: SamplingParams,
    context: RequestContext
) -> str:
    print("[Client] sampling_handler invoked")
    print(f"[Client] Received {len(messages)} message(s), params: {params}")

    lc_msgs = []
    # Include system prompt if provided
    if params.systemPrompt:
        print("[Client] Using system_prompt:", params.systemPrompt)
        lc_msgs.append(SystemMessage(content=params.systemPrompt))

    # Append each user message
    for idx, msg in enumerate(messages, start=1):
        print(f"[Client] Message #{idx} content:", msg.content.text)
        lc_msgs.append(HumanMessage(content=msg.content.text))

    # Create the LLM with the provided sampling parameters
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=params.temperature or 0.0,
        max_tokens=params.maxTokens or 64
    )

    # IMPORTANT: pass messages via the `input` keyword, not as a dict
    result = await llm.ainvoke(input=lc_msgs)
    return result.content

async def main():
    transport = StreamableHttpTransport(url="http://127.0.0.1:3000/mcp")
    client = Client(
        transport,
        sampling_handler=sampling_handler
    )

    # Example function code for which we want a docstring
    code_snippet = """\
def add(a: int, b: int) -> int:
    return a + b
"""

    async with client:
        result = await client.call_tool(
            "generate_docstring",
            {"code": code_snippet}
        )
        print("Generated Docstring:\n", result[0].text)

if __name__ == "__main__":
    asyncio.run(main())
