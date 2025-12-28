"""ChatKit store implementation using PostgreSQL.

Maps ChatKit's thread/item model to our Conversation/Message models.
Note: Our schema has one conversation per user (unique constraint on user_id).
ChatKit generates its own thread IDs, so we map them to the user's conversation.
"""

import uuid
from datetime import datetime

from chatkit.store import NotFoundError, Store
from chatkit.types import (
    Attachment,
    AssistantMessageContent,
    AssistantMessageItem,
    InferenceOptions,
    Page,
    ThreadItem,
    ThreadMetadata,
    UserMessageItem,
    UserMessageTextContent,
)
from sqlmodel import Session, select

from src.core.database import engine
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole


class RequestContext:
    """Request context passed to store operations."""

    def __init__(self, user_id: str):
        self.user_id = user_id


class TodoChatKitStore(Store[RequestContext]):
    """ChatKit store backed by PostgreSQL.

    Maps ChatKit threads to Conversations and items to Messages.
    Since our schema has one conversation per user, we map all ChatKit
    thread IDs to the user's single conversation.
    """

    def _get_user_conversation_id(self, db: Session, context: RequestContext) -> str | None:
        """Get the user's conversation ID, if one exists."""
        statement = select(Conversation).where(
            Conversation.user_id == context.user_id
        )
        conv = db.exec(statement).first()
        return conv.id if conv else None

    def _get_or_create_conversation(
        self, db: Session, context: RequestContext, thread_id: str
    ) -> str:
        """Get user's conversation or create one with the given thread_id."""
        statement = select(Conversation).where(
            Conversation.user_id == context.user_id
        )
        conv = db.exec(statement).first()

        if conv:
            return conv.id

        # Create new conversation
        conv = Conversation(
            id=thread_id,
            user_id=context.user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv.id

    def generate_item_id(
        self, prefix: str, thread: ThreadMetadata, context: RequestContext
    ) -> str:
        """Generate a unique item ID."""
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    async def load_thread(
        self, thread_id: str, context: RequestContext
    ) -> ThreadMetadata:
        """Load thread metadata by ID.

        Maps ChatKit thread_id to the user's conversation.
        """
        with Session(engine) as db:
            # First try to find by exact ID
            statement = select(Conversation).where(
                Conversation.id == thread_id,
                Conversation.user_id == context.user_id,
            )
            conv = db.exec(statement).first()

            # If not found, try to get user's conversation
            if conv is None:
                statement = select(Conversation).where(
                    Conversation.user_id == context.user_id
                )
                conv = db.exec(statement).first()

            if conv is None:
                raise NotFoundError(f"Thread {thread_id} not found")

            return ThreadMetadata(
                id=conv.id,
                created_at=conv.created_at,
            )

    async def save_thread(
        self, thread: ThreadMetadata, context: RequestContext
    ) -> None:
        """Persist thread metadata.

        Maps ChatKit thread to the user's single conversation.
        """
        with Session(engine) as db:
            # First check if conversation with this ID exists
            statement = select(Conversation).where(Conversation.id == thread.id)
            existing = db.exec(statement).first()

            if existing:
                existing.updated_at = datetime.utcnow()
                db.add(existing)
                db.commit()
                return

            # Check if user already has a conversation
            user_conv_statement = select(Conversation).where(
                Conversation.user_id == context.user_id
            )
            user_conv = db.exec(user_conv_statement).first()

            if user_conv:
                # User already has a conversation - just update timestamp
                user_conv.updated_at = datetime.utcnow()
                db.add(user_conv)
                db.commit()
            else:
                # Create new conversation for this user
                conv = Conversation(
                    id=thread.id,
                    user_id=context.user_id,
                    created_at=thread.created_at,
                    updated_at=datetime.utcnow(),
                )
                db.add(conv)
                db.commit()

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: RequestContext
    ) -> Page[ThreadMetadata]:
        """Load paginated threads for the user."""
        with Session(engine) as db:
            statement = select(Conversation).where(
                Conversation.user_id == context.user_id
            )

            if order == "desc":
                statement = statement.order_by(Conversation.created_at.desc())
            else:
                statement = statement.order_by(Conversation.created_at.asc())

            conversations = list(db.exec(statement).all())

            # Handle pagination
            start = 0
            if after:
                for idx, conv in enumerate(conversations):
                    if conv.id == after:
                        start = idx + 1
                        break

            data = conversations[start : start + limit]
            has_more = start + limit < len(conversations)
            next_after = data[-1].id if has_more and data else None

            thread_data = [
                ThreadMetadata(id=conv.id, created_at=conv.created_at) for conv in data
            ]
            return Page(data=thread_data, has_more=has_more, after=next_after)

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: RequestContext,
    ) -> Page[ThreadItem]:
        """Load paginated thread items (messages)."""
        with Session(engine) as db:
            # Map thread_id to user's conversation
            actual_conv_id = self._get_user_conversation_id(db, context)
            if not actual_conv_id:
                return Page(data=[], has_more=False, after=None)

            statement = select(Message).where(Message.conversation_id == actual_conv_id)

            if order == "desc":
                statement = statement.order_by(Message.created_at.desc())
            else:
                statement = statement.order_by(Message.created_at.asc())

            messages = list(db.exec(statement).all())

            # Handle pagination
            start = 0
            if after:
                for idx, msg in enumerate(messages):
                    if msg.id == after:
                        start = idx + 1
                        break

            data = messages[start : start + limit]
            has_more = start + limit < len(messages)
            next_after = data[-1].id if has_more and data else None

            items: list[ThreadItem] = []
            for msg in data:
                if msg.role == MessageRole.USER:
                    items.append(
                        UserMessageItem(
                            id=msg.id,
                            thread_id=actual_conv_id,
                            created_at=msg.created_at,
                            content=[UserMessageTextContent(text=msg.content)],
                            inference_options=InferenceOptions(),
                        )
                    )
                else:
                    items.append(
                        AssistantMessageItem(
                            id=msg.id,
                            thread_id=actual_conv_id,
                            created_at=msg.created_at,
                            content=[AssistantMessageContent(text=msg.content)],
                        )
                    )

            return Page(data=items, has_more=has_more, after=next_after)

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: RequestContext
    ) -> None:
        """Add new item to thread."""
        await self.save_item(thread_id, item, context)

    async def save_item(
        self, thread_id: str, item: ThreadItem, context: RequestContext
    ) -> None:
        """Upsert thread item by ID."""
        with Session(engine) as db:
            # Get or create user's conversation
            actual_conv_id = self._get_or_create_conversation(db, context, thread_id)

            # Determine role and content from item type
            if isinstance(item, UserMessageItem):
                role = MessageRole.USER
                content = ""
                for c in item.content:
                    if hasattr(c, "text"):
                        content = c.text
                        break
            elif isinstance(item, AssistantMessageItem):
                role = MessageRole.ASSISTANT
                content = ""
                for c in item.content:
                    if hasattr(c, "text"):
                        content = c.text
                        break
            else:
                # Skip non-message items (like tool calls)
                return

            # Skip empty content
            if not content:
                return

            # Check if message exists
            statement = select(Message).where(Message.id == item.id)
            existing = db.exec(statement).first()

            if existing:
                existing.content = content
                db.add(existing)
            else:
                msg = Message(
                    id=item.id,
                    conversation_id=actual_conv_id,
                    role=role,
                    content=content,
                    created_at=item.created_at,
                )
                db.add(msg)

            # Update conversation timestamp
            conv_statement = select(Conversation).where(Conversation.id == actual_conv_id)
            conv = db.exec(conv_statement).first()
            if conv:
                conv.updated_at = datetime.utcnow()
                db.add(conv)

            db.commit()

    async def load_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ) -> ThreadItem:
        """Load specific thread item."""
        with Session(engine) as db:
            # Map thread_id to user's conversation
            actual_conv_id = self._get_user_conversation_id(db, context)
            if not actual_conv_id:
                raise NotFoundError(f"Item {item_id} not found")

            statement = select(Message).where(
                Message.id == item_id, Message.conversation_id == actual_conv_id
            )
            msg = db.exec(statement).first()
            if msg is None:
                raise NotFoundError(f"Item {item_id} not found")

            if msg.role == MessageRole.USER:
                return UserMessageItem(
                    id=msg.id,
                    thread_id=actual_conv_id,
                    created_at=msg.created_at,
                    content=[UserMessageTextContent(text=msg.content)],
                    inference_options=InferenceOptions(),
                )
            else:
                return AssistantMessageItem(
                    id=msg.id,
                    thread_id=actual_conv_id,
                    created_at=msg.created_at,
                    content=[AssistantMessageContent(text=msg.content)],
                )

    async def delete_thread(self, thread_id: str, context: RequestContext) -> None:
        """Delete thread and all items."""
        with Session(engine) as db:
            # Get user's conversation
            actual_conv_id = self._get_user_conversation_id(db, context)
            if not actual_conv_id:
                return

            # Delete messages first
            statement = select(Message).where(Message.conversation_id == actual_conv_id)
            messages = db.exec(statement).all()
            for msg in messages:
                db.delete(msg)

            # Delete conversation
            conv_statement = select(Conversation).where(Conversation.id == actual_conv_id)
            conv = db.exec(conv_statement).first()
            if conv:
                db.delete(conv)

            db.commit()

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ) -> None:
        """Delete specific thread item."""
        with Session(engine) as db:
            # Get user's conversation
            actual_conv_id = self._get_user_conversation_id(db, context)
            if not actual_conv_id:
                return

            statement = select(Message).where(
                Message.id == item_id, Message.conversation_id == actual_conv_id
            )
            msg = db.exec(statement).first()
            if msg:
                db.delete(msg)
                db.commit()

    async def save_attachment(
        self, attachment: Attachment, context: RequestContext
    ) -> None:
        """Persist attachment metadata (not implemented)."""
        raise NotImplementedError("Attachments not supported")

    async def load_attachment(
        self, attachment_id: str, context: RequestContext
    ) -> Attachment:
        """Load attachment by ID (not implemented)."""
        raise NotImplementedError("Attachments not supported")

    async def delete_attachment(
        self, attachment_id: str, context: RequestContext
    ) -> None:
        """Delete attachment (not implemented)."""
        raise NotImplementedError("Attachments not supported")
