"""Agent service for AI-powered task management."""

import os
from typing import AsyncIterator

from agents import Agent, Runner
from agents.mcp import MCPServerSse
from agents.extensions.models.litellm_model import LitellmModel

from src.core.config import settings

# MCP Server URL - runs alongside FastAPI
# Note: FastMCP's sse_app() creates routes at /sse internally,
# so when mounted at /mcp, the full path becomes /mcp/sse
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp/sse")


class AgentService:
    """Service for managing AI agent interactions.

    Uses OpenAI Agents SDK with MCP server for tool access.
    """

    def __init__(self, user_id: str) -> None:
        """Initialize the agent service with user context.

        Args:
            user_id: The authenticated user's ID for tool authorization
        """
        self.user_id = user_id

    def _get_instructions(self) -> str:
        """Get the agent instructions for task management."""
        return f"""You are a helpful task management assistant. You help users manage their todo list through natural language.

IMPORTANT: The user_id for all tool calls is: {self.user_id}

You have access to the following tools:
- add_task: Create a new task. Always provide user_id="{self.user_id}".
- list_tasks: Show the user's tasks. Always provide user_id="{self.user_id}". Use status="all" by default.
- complete_task: Mark a task as done. Always provide user_id="{self.user_id}".
- update_task: Change a task's title or description. Always provide user_id="{self.user_id}".
- delete_task: Remove a task (requires confirmation). Always provide user_id="{self.user_id}".

Guidelines:
1. Be concise and friendly in your responses.
2. When listing tasks, format them nicely with checkboxes.
3. When a task is created/updated/completed, confirm the action clearly.
4. If a user's intent is ambiguous, ask for clarification.
5. If multiple tasks match a name, tell the user and ask them to be more specific.
6. For delete operations, the tool will ask for confirmation - relay this to the user.
7. Keep track of context - if a user says "mark it as done" after creating a task, use that task.
8. Use emojis sparingly to make responses friendly (e.g., checkmark for completed tasks).

Example interactions:
- User: "Add a task to buy groceries" -> Create the task and confirm
- User: "Show me my tasks" -> List all tasks
- User: "I finished the groceries task" -> Mark it as complete
- User: "Delete the groceries task" -> Ask for confirmation first
"""

    async def run(self, message: str) -> str:
        """Run the agent with a user message.

        Args:
            message: The user's message

        Returns:
            The agent's response
        """
        # Create MCP server connection using async context manager
        async with MCPServerSse(
            name="todo-tools",
            params={
                "url": MCP_SERVER_URL,
            },
        ) as mcp_server:
            # Create Gemini model via LiteLLM
            model = LitellmModel(
                model=settings.GEMINI_MODEL,
                api_key=settings.GEMINI_API_KEY,
            )

            agent = Agent(
                name="Task Assistant",
                instructions=self._get_instructions(),
                model=model,
                mcp_servers=[mcp_server],
            )

            try:
                result = await Runner.run(agent, message)
                return result.final_output
            except Exception as e:
                # Log the error and return a friendly message
                import traceback
                print(f"Agent error: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                return "I'm sorry, I encountered an issue processing your request. Please try again."

    async def run_stream(self, message: str) -> AsyncIterator[str]:
        """Run the agent with streaming response.

        Args:
            message: The user's message

        Yields:
            Chunks of the agent's response
        """
        # Create MCP server connection using async context manager
        async with MCPServerSse(
            name="todo-tools",
            params={
                "url": MCP_SERVER_URL,
            },
        ) as mcp_server:
            # Create Gemini model via LiteLLM
            model = LitellmModel(
                model=settings.GEMINI_MODEL,
                api_key=settings.GEMINI_API_KEY,
            )

            agent = Agent(
                name="Task Assistant",
                instructions=self._get_instructions(),
                model=model,
                mcp_servers=[mcp_server],
            )

            try:
                async for event in Runner.run_streamed(agent, message):
                    if hasattr(event, "data") and hasattr(event.data, "delta"):
                        yield event.data.delta
            except Exception as e:
                import traceback
                print(f"Agent streaming error: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                yield "I'm sorry, I encountered an issue processing your request. Please try again."

    async def cleanup(self) -> None:
        """Cleanup agent resources (no-op, context manager handles cleanup)."""
        pass
