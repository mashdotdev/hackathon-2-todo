# MCP Server Package
# Phase III AI-Powered Chatbot with Model Context Protocol

from .server import mcp

# Import tools to register them with the MCP server
from . import tools  # noqa: F401

__all__ = ["mcp"]
