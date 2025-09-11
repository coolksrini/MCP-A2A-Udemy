# MCP + Vector DB + A2A Cheat Sheet

**Generated:** 2025-09-11 07:00 UTC

---

## MCP Basics
- Resources = read-only data
```
@mcp.resource
def get_profile(id): return {"id": id}
```
- Tools = actions
```
@mcp.tool
def add(a,b): return a+b
```
- Prompts = reusable templates
```
@mcp.prompt("greet")
def greet(name): return f"Hi {name}"
```
- Client enforces auth/logs; Server hosts logic.

---

## Vector Databases
- Store embeddings + enable ANN search (semantic similarity).
- Common: FAISS, Pinecone, Milvus, Chroma.
- Example resource:
```
@mcp.resource
def search_knowledge(q): return vector_index.search(embed(q))
```
- Challenges: embedding drift, cost, latency, PII redaction.

---

## Google A2A (Agent-to-Agent)
- Agents discover, negotiate, and delegate tasks.
- Example registry:
```
class AgentRegistry: ...
```
- Flow: [Agent A] → [Registry] → [Agent B] → [Task].
- Challenges: trust, schema interoperability, failures.
