#!/usr/bin/env python3
import asyncio
from fastmcp import FastMCP, Context

# Eine Klasse, die eine Methode bereitstellt, die wir dynamisch als Tool hinzufügen wollen
class DynamicToolProvider:
    @classmethod
    def dynamic_method(cls, text: str) -> str:
        """Ein dynamisch hinzugefügtes Tool."""
        return f"Dynamisches Tool verarbeitet: {text.upper()}"

# FastMCP Instanz
mcp = FastMCP(
    name="ProgressDemoServer",
)

@mcp.tool(
    name="process_items",
    description="Verarbeitet eine Liste von Items mit Fortschrittsanzeige und dynamischer Tool-Modifikation"
)
async def process_items(items: list[str], ctx: Context) -> list[str]:
    """Gibt für jedes Item nach einer kleinen Verzögerung das Uppercase zurück.
    Fügt danach dynamisch ein Tool hinzu und entfernt es wieder."""
    total = len(items)
    results: list[str] = []
    await ctx.info(f"Starte Verarbeitung von {total} Items.")
    for i, item in enumerate(items, start=1):
        await ctx.info(f"Verarbeite Item {i}/{total}: {item}")
        await ctx.report_progress(progress=i, total=total)
        await asyncio.sleep(0.5)  # Simuliere Arbeit
        results.append(item.upper())
    
    await ctx.info("Item-Verarbeitung abgeschlossen.")
    await asyncio.sleep(1) # Kurze Pause

    # Dynamisches Tool hinzufügen
    tool_name_dynamic = "dynamic_tool_on_the_fly"
    await ctx.info(f"Füge dynamisches Tool hinzu: '{tool_name_dynamic}'")
    # add_tool ist auf der FastMCP-Instanz verfügbar, die wir über ctx.fastmcp erreichen
    ctx.fastmcp.add_tool(DynamicToolProvider.dynamic_method, name=tool_name_dynamic)
    # FastMCP sendet hier automatisch eine notifications/tools/list_changed

    await asyncio.sleep(3) # Zeit für den Client, die Notification zu empfangen und zu loggen

    # Dynamisches Tool entfernen
    # HINWEIS: mcp.remove_tool() ist laut Dokumentation seit FastMCP v2.3.4 verfügbar.
    # Wenn ein AttributeError auftritt, überprüfe deine FastMCP-Version.
    # Für ältere Versionen oder zur reinen Demo des Hinzufügens kann die folgende Zeile auskommentiert werden.
    await ctx.info(f"Versuche, dynamisches Tool zu entfernen: '{tool_name_dynamic}'")
    try:
        ctx.fastmcp.remove_tool(tool_name_dynamic)
        await ctx.info(f"Dynamisches Tool '{tool_name_dynamic}' erfolgreich entfernt.")
        # FastMCP sendet hier automatisch eine notifications/tools/list_changed
    except AttributeError:
        await ctx.error(f"Fehler: 'remove_tool' ist in dieser FastMCP-Version nicht verfügbar. Bitte FastMCP >= 2.3.4 verwenden.")
    except Exception as e:
        await ctx.error(f"Unerwarteter Fehler beim Entfernen des Tools '{tool_name_dynamic}': {e}")
        
    return results

if __name__ == "__main__":
    # Startet Uvicorn, mountet Streamable-HTTP auf /mcp
    mcp.run(transport="streamable-http", port=8000)