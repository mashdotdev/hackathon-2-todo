"""Chat routes for AI-powered task management."""

import json
import uuid

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from src.api.deps import get_current_user, get_db
from src.models.message import MessageRole
from src.models.user import User
from src.schemas.chat import ChatHistoryResponse
from src.services.agent_service import AgentService
from src.services.chat_service import ChatService

router = APIRouter()


@router.post("")
async def chat(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """Send a chat message and receive AI response.

    The AI can execute task operations via MCP tools.
    Response uses Server-Sent Events (SSE) for streaming.
    """
    data = await request.json()
    messages = data.get("messages", [])

    # Get or create conversation and save user message
    chat_service = ChatService(db)
    conversation = chat_service.get_or_create_conversation(current_user.id)

    # Get the last user message - handle both old format (content) and new format (parts/text)
    user_message = ""
    if messages:
        last_message = messages[-1]
        if last_message.get("role") == "user":
            # Try new format first (parts array with text)
            parts = last_message.get("parts", [])
            if parts:
                for part in parts:
                    if isinstance(part, dict) and part.get("type") == "text":
                        user_message = part.get("text", "")
                        break
                    elif isinstance(part, str):
                        user_message = part
                        break
            # Fall back to old format (content string)
            if not user_message:
                user_message = last_message.get("content", "")

            if user_message:
                chat_service.add_message(
                    conversation.id,
                    MessageRole.USER,
                    user_message,
                )

    async def generate():
        message_id = str(uuid.uuid4())

        if not user_message:
            response = "I didn't receive a message. How can I help you?"
            # AI SDK v5+ UI Message Stream format
            yield f'data: {json.dumps({"type": "start", "messageId": message_id})}\n\n'
            yield f'data: {json.dumps({"type": "text-start", "id": message_id})}\n\n'
            yield f'data: {json.dumps({"type": "text-delta", "id": message_id, "delta": response})}\n\n'
            yield f'data: {json.dumps({"type": "text-end", "id": message_id})}\n\n'
            yield f'data: {json.dumps({"type": "finish", "finishReason": "stop"})}\n\n'
            return

        # Create agent service with user context
        agent_service = AgentService(current_user.id)

        try:
            # Run agent and get response
            response = await agent_service.run(user_message)

            # Save assistant response to database
            chat_service.add_message(
                conversation.id,
                MessageRole.ASSISTANT,
                response,
            )

            # Stream response in AI SDK v5+ UI Message Stream format
            yield f'data: {json.dumps({"type": "start", "messageId": message_id})}\n\n'
            yield f'data: {json.dumps({"type": "text-start", "id": message_id})}\n\n'
            yield f'data: {json.dumps({"type": "text-delta", "id": message_id, "delta": response})}\n\n'
            yield f'data: {json.dumps({"type": "text-end", "id": message_id})}\n\n'
            yield f'data: {json.dumps({"type": "finish", "finishReason": "stop"})}\n\n'
        except Exception as e:
            error_msg = "I'm sorry, I encountered an issue processing your request. Please try again."
            import traceback
            print(f"Chat error: {e}")
            print(f"Error type: {type(e).__name__}")
            print(f"Traceback: {traceback.format_exc()}")
            yield f'data: {json.dumps({"type": "start", "messageId": message_id})}\n\n'
            yield f'data: {json.dumps({"type": "text-start", "id": message_id})}\n\n'
            yield f'data: {json.dumps({"type": "text-delta", "id": message_id, "delta": error_msg})}\n\n'
            yield f'data: {json.dumps({"type": "text-end", "id": message_id})}\n\n'
            yield f'data: {json.dumps({"type": "finish", "finishReason": "error"})}\n\n'
        finally:
            await agent_service.cleanup()

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Vercel-AI-UI-Message-Stream": "v1",
    }
    return StreamingResponse(generate(), media_type="text/event-stream", headers=headers)


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatHistoryResponse:
    """Get conversation history.

    Args:
        limit: Maximum number of messages to return (1-100, default 20)
    """
    # Clamp limit to valid range
    limit = max(1, min(100, limit))

    chat_service = ChatService(db)
    history = chat_service.get_chat_history(current_user.id, limit)

    if history is None:
        # Create empty conversation
        conversation = chat_service.get_or_create_conversation(current_user.id)
        return ChatHistoryResponse(conversation_id=conversation.id, messages=[])

    return history


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Clear conversation history.

    Deletes all messages in the user's conversation.
    """
    chat_service = ChatService(db)
    chat_service.clear_history(current_user.id)
