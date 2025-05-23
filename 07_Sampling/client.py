import asyncio
from dotenv import load_dotenv



from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.sampling import SamplingMessage, SamplingParams, RequestContext

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

async def sampling_handler(
    messages: list[SamplingMessage],
    params: SamplingParams,
    context: RequestContext
) -> str:
    print("[Client] sampling_handler invoked")
    print(f"[Client] Received {len(messages)} message(s), params: {params}")

    lc_msgs = []
    if params.systemPrompt:
        print("[Client] Using system_prompt:", params.systemPrompt)
        lc_msgs.append(SystemMessage(content=params.systemPrompt))

    for idx, msg in enumerate(messages, start=1):
        print(f"[Client] Message #{idx} content:", msg.content.text)
        lc_msgs.append(HumanMessage(content=msg.content.text))

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=params.temperature or 0.0,
        max_tokens=params.maxTokens or 64
    )

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
