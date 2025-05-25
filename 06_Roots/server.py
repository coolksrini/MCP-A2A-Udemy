import os
from urllib.parse import unquote, urlparse

from fastmcp import Context, FastMCP

mcp = FastMCP(name="FileSearchServer")


@mcp.tool(
    name="find_file", description="Search for a file in the provided root directories"
)
async def find_file(filename: str, ctx: Context) -> list[str]:
    """
    Recursively searches all file:// roots for 'filename' and
    returns all found absolute paths.
    """
    roots = await ctx.list_roots()
    matches: list[str] = []

    for root in roots:
        uri_str = str(root.uri)
        parsed = urlparse(uri_str)

        if parsed.scheme != "file":
            continue

        path = unquote(parsed.path)

        if (
            os.name == "nt"
            and path.startswith("/")
            and len(path) > 2
            and path[2] == ":"
        ):
            path = path[1:]

        for dirpath, _, files in os.walk(path):
            if filename in files:
                matches.append(os.path.join(dirpath, filename))

    return matches


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
