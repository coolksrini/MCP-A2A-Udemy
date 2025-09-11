# MCP Cheat Sheet

- Resources = read-only data (example):
```python
@mcp.resource
def get_profile(id): return {"id": id}
```
- Tools = actions (example):
```python
@mcp.tool
def add(a,b): return a+b
```
- Prompts = templates (example):
```python
@mcp.prompt("greet") def greet(name): return f"Hi {name}"
```
- Client: enforces auth, logs, rate limits.
- Server: hosts logic, must be versioned and monitored.
