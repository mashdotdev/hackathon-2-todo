"""MCP Server for Todo application.

Exposes task management tools via Model Context Protocol.
"""

from mcp.server.fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("TodoServer")

# Tools will be registered via @mcp.tool() decorator in tools/ modules
