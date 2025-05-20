#!/usr/bin/env python3
from fastmcp import FastMCP

mcp = FastMCP(name="WeatherServer")

@mcp.tool(
    name="get_weather",
    description="Gibt eine Wetterbeschreibung für eine angegebene Stadt zurück"
)
def get_weather(city: str) -> str:
    """
    Args:
        city (str): Name der Stadt
    Returns:
        str: Beschreibung des aktuellen Wetters (Fake-Daten)
    """
    # Hier könnte man eine echte Wetter-API anfragen
    return "Sunny, 22°C"

if __name__ == "__main__":
    # Server auf Streamable HTTP Port 3000 starten
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=3000
    )
