# Flashcards

Q: What is a Resource?  
A: Read-only data endpoint for LLMs.  
Code: `@mcp.resource def foo(): ...`

Q: How to secure a destructive tool?  
A: Require role checks, confirmation prompts, logging.  
Code: `@require_role("admin") @mcp.tool def delete_user(id): ...`
