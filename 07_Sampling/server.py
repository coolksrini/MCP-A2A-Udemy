from fastmcp import FastMCP, Context

mcp = FastMCP(name="DocGenServer")


@mcp.tool(
    name="generate_docstring",
    description="Generate a Python docstring for a given function code snippet",
)
async def generate_docstring(code: str, ctx: Context) -> str:
    print("[Server] Tool 'generate_docstring' called")
    print("[Server] Input code:\n", code)

    prompt = (
        "Given the following Python function code, write a concise, "
        "PEP-257–compliant docstring. Your answer should include only the "
        "triple-quoted docstring.\n\n"
        f"{code}"
    )
    print("[Server] Sampling prompt constructed:\n", prompt)

    response = await ctx.sample(
        messages=prompt,
        system_prompt="You are a Python documentation assistant.",
        temperature=0.7,
        max_tokens=150,
    )
    result = response.text.strip()
    print("[Server] Returning docstring:\n", result)
    return result


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=3000)
