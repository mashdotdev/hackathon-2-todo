"""Chat service for conversation persistence."""

from datetime import datetime

from sqlmodel import Session, select

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.schemas.chat import ChatHistoryResponse, StoredMessage


class ChatService:
    """Service for managing chat conversations in database.

    Provides operations for conversation management and message persistence.
    All operations are scoped to the authenticated user.
    """

    def __init__(self, db: Session) -> None:
        """Initialize the chat service with database session."""
        self.db = db

    def get_or_create_conversation(self, user_id: str) -> Conversation:
        """Get or create a conversation for a user.

        Each user has exactly one conversation (single thread per user).

        Args:
            user_id: Owner user ID

        Returns:
            The user's conversation
        """
        statement = select(Conversation).where(Conversation.user_id == user_id)
        conversation = self.db.exec(statement).first()

        if conversation is None:
            conversation = Conversation(user_id=user_id)
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

        return conversation

    def get_messages(
        self,
        conversation_id: str,
        limit: int = 20,
    ) -> list[Message]:
        """Get messages from a conversation.

        Args:
            conversation_id: The conversation identifier
            limit: Maximum number of messages to return (default 20)

        Returns:
            List of messages in chronological order
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = self.db.exec(statement).all()
        # Reverse to return in chronological order (oldest first)
        return list(reversed(messages))

    def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
    ) -> Message:
        """Add a message to a conversation.

        Args:
            conversation_id: The conversation identifier
            role: Message sender role (user or assistant)
            content: Message content

        Returns:
            The created message
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.db.add(message)

        # Update conversation timestamp
        statement = select(Conversation).where(Conversation.id == conversation_id)
        conversation = self.db.exec(statement).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.db.add(conversation)

        self.db.commit()
        self.db.refresh(message)
        return message

    def clear_history(self, user_id: str) -> bool:
        """Clear all messages in a user's conversation.

        Args:
            user_id: The owner user ID

        Returns:
            True if cleared, False if no conversation found
        """
        statement = select(Conversation).where(Conversation.user_id == user_id)
        conversation = self.db.exec(statement).first()

        if conversation is None:
            return False

        # Delete all messages in the conversation
        message_statement = select(Message).where(
            Message.conversation_id == conversation.id
        )
        messages = self.db.exec(message_statement).all()
        for message in messages:
            self.db.delete(message)

        self.db.commit()
        return True

    def get_chat_history(
        self,
        user_id: str,
        limit: int = 20,
    ) -> ChatHistoryResponse | None:
        """Get chat history for a user.

        Args:
            user_id: The owner user ID
            limit: Maximum number of messages to return

        Returns:
            Chat history response or None if no conversation
        """
        conversation = self.get_or_create_conversation(user_id)
        messages = self.get_messages(conversation.id, limit)

        stored_messages = [
            StoredMessage(
                id=msg.id,
                role=msg.role.value if isinstance(msg.role, MessageRole) else msg.role,
                content=msg.content,
                created_at=msg.created_at,
            )
            for msg in messages
        ]

        return ChatHistoryResponse(
            conversation_id=conversation.id,
            messages=stored_messages,
        )
