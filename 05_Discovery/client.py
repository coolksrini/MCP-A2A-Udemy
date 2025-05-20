import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.logging import LogMessage
import mcp.types as types

async def message_handler(msg: types.ServerNotification):
    specific_notification = msg.root 

    if isinstance(specific_notification, types.ProgressNotification):
        p = specific_notification.params
        progress_val = p.progress if isinstance(p.progress, (int, float)) else 0
        total_val = p.total if isinstance(p.total, (int, float)) else '?'
        if isinstance(total_val, (int,float)) and total_val > 0 :
             print(f"[Progress] {progress_val:.0f}/{total_val:.0f}")
        else:
             print(f"[Progress] {progress_val:.0f}/{total_val}")

    elif isinstance(specific_notification, types.ToolListChangedNotification):
        print("[Notification] Werkzeugliste hat sich geändert!")
    

async def log_handler(params: LogMessage):
    level = params.level.upper()
    data_str = str(params.data) if params.data is not None else ""
    print(f"[Log – {level}] {data_str}")

async def main():
    transport = StreamableHttpTransport(url="http://127.0.0.1:8000/mcp")
    
    client = Client(
        transport,
        message_handler=message_handler,
        log_handler=log_handler
    )
    
    async with client:
        print("Verbinde mit Server...")
        await asyncio.sleep(0.1) 
        
        initial_tools_list = []
        try:
            tools = await client.list_tools()
            initial_tools_list = [t.name for t in tools]
            print("→ Verfügbare Werkzeuge zu Beginn:", initial_tools_list)

            print("\n→ Rufe 'process_items' auf…")
            items = ["eins", "zwei", "drei"]
            result = await client.call_tool("process_items", {"items": items})
            processed = [c.text for c in result if hasattr(c, 'text')]
            print("→ Ergebnis von 'process_items':", processed)

            print("\n→ Client bleibt für 7 Sekunden aktiv, um weitere Notifications zu empfangen...")
            await asyncio.sleep(7)

            if client.is_connected():
                print("\n→ Überprüfe Werkzeuge nach Notifications:")
                final_tools = await client.list_tools()
                final_tools_list = [t.name for t in final_tools]
                print("→ Verfügbare Werkzeuge am Ende:", final_tools_list)
                
                added_tool_name = "dynamic_tool_on_the_fly"
                if added_tool_name in final_tools_list and added_tool_name not in initial_tools_list:
                    print(f"INFO: '{added_tool_name}' wurde erfolgreich erkannt (noch vorhanden).")
                elif added_tool_name not in final_tools_list and added_tool_name in initial_tools_list :
                     print(f"INFO: '{added_tool_name}' wurde erfolgreich als entfernt erkannt.")
                elif added_tool_name not in final_tools_list and added_tool_name not in initial_tools_list :
                    print(f"INFO: '{added_tool_name}' wurde hinzugefügt und erfolgreich wieder entfernt (wie erwartet, wenn remove_tool funktioniert).")


            else:
                print("→ Client am Ende nicht mehr verbunden.")

        except Exception as e:
            print(f"Ein Fehler ist während der Client-Ausführung aufgetreten: {e}")
        finally:
            print("→ Client wird beendet.")


if __name__ == "__main__":
    asyncio.run(main())