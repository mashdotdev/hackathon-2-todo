"""ChatKit server implementation with OpenAI Agents SDK and MCP.

Integrates ChatKit with the Agents SDK, using MCP tools for task management.
"""

import os
from collections.abc import AsyncIterator
from datetime import datetime

from agents import Agent, Runner
from agents.mcp import MCPServerSse
from chatkit.agents import AgentContext, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    ThreadItemDoneEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
)

from src.chatkit.store import RequestContext, TodoChatKitStore
from src.core.config import settings

# MCP Server URL
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp/sse")


def get_agent_instructions(user_id: str) -> str:
    """Get the agent instructions for task management."""
    return f"""You are a helpful task management assistant. You help users manage their todo list through natural language.

IMPORTANT: The user_id for all tool calls is: {user_id}

You have access to the following tools:
- add_task: Create a new task. Always provide user_id="{user_id}".
- list_tasks: Show the user's tasks. Always provide user_id="{user_id}". Use status="all" by default.
- complete_task: Mark a task as done. Always provide user_id="{user_id}".
- update_task: Change a task's title or description. Always provide user_id="{user_id}".
- delete_task: Remove a task. Always provide user_id="{user_id}".

Guidelines:
1. Be concise and friendly in your responses.
2. When listing tasks, format them nicely with checkboxes.
3. When a task is created/updated/completed, confirm the action clearly.
4. If a user's intent is ambiguous, ask for clarification.
5. If multiple tasks match a name, tell the user and ask them to be more specific.
6. Keep track of context - if a user says "mark it as done" after creating a task, use that task.
7. Use emojis sparingly to make responses friendly (e.g., checkmark for completed tasks).

Example interactions:
- User: "Add a task to buy groceries" -> Create the task and confirm
- User: "Show me my tasks" -> List all tasks
- User: "I finished the groceries task" -> Mark it as complete
- User: "Delete the groceries task" -> Delete it
"""


class TodoChatKitServer(ChatKitServer[RequestContext]):
    """ChatKit server for todo management.

    Integrates with OpenAI Agents SDK and MCP tools.
    """

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Generate assistant response for user message.

        Uses Agents SDK with MCP tools to process the user's request.
        """
        # Extract user message text
        user_text = ""
        if input_user_message and input_user_message.content:
            for part in input_user_message.content:
                if hasattr(part, "text"):
                    user_text = part.text
                    break

        if not user_text:
            # No message, return a prompt
            msg_id = self.store.generate_item_id("message", thread, context)
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    id=msg_id,
                    thread_id=thread.id,
                    created_at=datetime.utcnow(),
                    content=[
                        AssistantMessageContent(
                            text="Hello! How can I help you manage your tasks today?"
                        )
                    ],
                ),
            )
            return

        # Create agent context for streaming
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
            previous_response_id=None,
        )

        try:
            # Connect to MCP server and run agent
            async with MCPServerSse(
                name="todo-tools",
                params={"url": MCP_SERVER_URL},
            ) as mcp_server:
                # Create agent with Gemini model via LiteLLM
                from agents.extensions.models.litellm_model import LitellmModel

                model = LitellmModel(
                    model=settings.GEMINI_MODEL,
                    api_key=settings.GEMINI_API_KEY,
                )

                agent = Agent(
                    name="Task Assistant",
                    instructions=get_agent_instructions(context.user_id),
                    model=model,
                    mcp_servers=[mcp_server],
                )

                # Run agent with streaming
                result = Runner.run_streamed(agent, user_text, context=agent_context)

                # Stream the response using ChatKit's stream_agent_response
                async for event in stream_agent_response(agent_context, result):
                    yield event

        except Exception as e:
            # Return error message
            import traceback

            print(f"ChatKit agent error: {e}")
            print(f"Traceback: {traceback.format_exc()}")

            # Detect rate limit errors and provide helpful message
            error_str = str(e).lower()
            if "rate" in error_str or "quota" in error_str or "429" in error_str:
                error_message = (
                    "⏳ The AI service is temporarily rate-limited. "
                    "Please wait a moment and try again. "
                    "(Free tier has limited requests per minute)"
                )
            elif "api_key" in error_str or "authentication" in error_str:
                error_message = (
                    "🔑 AI service authentication failed. "
                    "Please check the API key configuration."
                )
            else:
                error_message = (
                    "I'm sorry, I encountered an issue processing your request. "
                    "Please try again."
                )

            msg_id = self.store.generate_item_id("message", thread, context)
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    id=msg_id,
                    thread_id=thread.id,
                    created_at=datetime.utcnow(),
                    content=[
                        AssistantMessageContent(text=error_message)
                    ],
                ),
            )


# Create the server instance
chatkit_store = TodoChatKitStore()
chatkit_server = TodoChatKitServer(store=chatkit_store)
