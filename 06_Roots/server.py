#!/usr/bin/env python3
import os
from fastmcp import FastMCP, Context
from urllib.parse import urlparse, unquote

mcp = FastMCP(name="FileSearchServer")

@mcp.tool(
    name="find_file",
    description="Sucht nach einer Datei in den übergebenen Stammverzeichnissen"
)
async def find_file(filename: str, ctx: Context) -> list[str]:
    """
    Durchsucht alle file://-Roots rekursiv nach 'filename' und
    liefert alle gefundenen absoluten Pfade zurück.
    """
    roots = await ctx.list_roots()
    matches: list[str] = []

    for root in roots:
        uri_str = str(root.uri)
        parsed = urlparse(uri_str)

        if parsed.scheme != "file":
            continue

        # Pfad extrahieren und URL-dekodieren
        path = unquote(parsed.path)

        # Unter Windows: führenden Slash vor Laufwerk entfernen
        if os.name == "nt" and path.startswith("/") and len(path) > 2 and path[2] == ":":
            path = path[1:]

        # Nun im Dateisystem suchen
        for dirpath, _, files in os.walk(path):
            if filename in files:
                matches.append(os.path.join(dirpath, filename))

    return matches

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
