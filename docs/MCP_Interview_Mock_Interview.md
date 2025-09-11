# Mock Interview Script

I: What problem does MCP solve?  
C: MCP standardizes LLM-safe access to data and actions via resources, tools, and prompts.

I: How to secure delete_user?  
C: Use RBAC + confirmation prompts + logging.
Code: `@require_role("admin") @mcp.tool def delete_user(id): ...`
