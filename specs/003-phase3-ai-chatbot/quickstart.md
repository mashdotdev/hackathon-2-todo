# Quickstart: Phase III AI-Powered Chatbot

**Date**: 2025-12-26
**Feature**: 003-phase3-ai-chatbot

## Prerequisites

Before starting Phase III, ensure you have:

1. **Phase II Complete**: Working backend and frontend with:
   - User authentication (register, login, logout)
   - Task CRUD operations
   - PostgreSQL database (Neon)

2. **Development Environment**:
   - Python 3.13+
   - Node.js 20+ LTS
   - UV package manager
   - Running backend on `http://localhost:8000`
   - Running frontend on `http://localhost:3000`

3. **API Keys**:
   - OpenAI API key (for Agents SDK)

---

## Step 1: Install Backend Dependencies

```bash
cd backend

# Add OpenAI Agents SDK and MCP SDK
uv add openai-agents "mcp[cli]"

# Verify installation
uv run python -c "from agents import Agent; from mcp.server.fastmcp import FastMCP; print('OK')"
```

---

## Step 2: Configure Environment

Add to `backend/.env`:

```env
# Existing Phase II variables
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
FRONTEND_URL=http://localhost:3000

# New Phase III variables
OPENAI_API_KEY=sk-your-openai-api-key
```

---

## Step 3: Create Database Migration

Create migration for new tables:

```bash
cd backend

# Generate migration
uv run alembic revision --autogenerate -m "add_conversations_and_messages"

# Apply migration
uv run alembic upgrade head
```

---

## Step 4: Install Frontend Dependencies

```bash
cd frontend

# Add Vercel AI SDK
npm install ai @ai-sdk/react @ai-sdk/openai
```

---

## Step 5: Verify Setup

### Backend Health Check

```bash
# Start backend
cd backend
uv run uvicorn src.main:app --reload

# Test existing endpoints work
curl http://localhost:8000/health
```

### Frontend Health Check

```bash
# Start frontend
cd frontend
npm run dev

# Visit http://localhost:3000 and verify login works
```

---

## Step 6: Create Chat Page (Frontend)

Create `frontend/src/app/chat/page.tsx`:

```tsx
'use client';

import { useChat } from '@ai-sdk/react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function ChatPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const { messages, input, handleInputChange, handleSubmit, isLoading: chatLoading } = useChat({
    api: `${process.env.NEXT_PUBLIC_API_URL}/api/chat`,
  });

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="flex flex-col h-screen">
      <header className="p-4 border-b">
        <h1>Task Assistant</h1>
      </header>

      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((m) => (
          <div key={m.id} className={m.role === 'user' ? 'text-right' : 'text-left'}>
            <span className="inline-block p-2 rounded-lg bg-gray-100 dark:bg-gray-800">
              {m.content}
            </span>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t">
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Try: 'Add a task to buy groceries'"
          className="w-full p-2 border rounded"
          disabled={chatLoading}
        />
      </form>
    </div>
  );
}
```

---

## Step 7: Create Chat Endpoint (Backend)

Create `backend/src/api/routes/chat.py`:

```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from ..deps import get_current_user
from ...models.user import User

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("")
async def chat(request: Request, current_user: User = Depends(get_current_user)):
    data = await request.json()
    messages = data.get("messages", [])

    async def generate():
        # Placeholder - will be replaced with actual agent logic
        response = "Hello! I'm your task assistant. Try saying 'Add a task to...'"
        yield f'0:"{response}"\n'
        yield 'd:{"finishReason":"stop"}\n'

    return StreamingResponse(generate(), media_type="text/event-stream")
```

Add to `backend/src/main.py`:

```python
from .api.routes.chat import router as chat_router
app.include_router(chat_router)
```

---

## Step 8: Test the Chat

1. Start backend: `uv run uvicorn src.main:app --reload`
2. Start frontend: `npm run dev`
3. Navigate to `http://localhost:3000/chat`
4. Send a message and verify the response appears

---

## Next Steps

After completing this quickstart:

1. **Implement MCP Tools**: Add `add_task`, `list_tasks`, etc. as `@function_tool` decorators
2. **Create Agent**: Configure the OpenAI Agent with tools and instructions
3. **Add Streaming**: Implement proper SSE streaming with agent responses
4. **Persist Conversations**: Save messages to the database
5. **Add History Loading**: Load previous conversation on page load

---

## Troubleshooting

### CORS Errors
Ensure `FRONTEND_URL` in backend `.env` matches your frontend URL.

### 401 Errors on Chat
Verify the JWT token is being sent with requests. Check `AuthContext` and cookie settings.

### OpenAI API Errors
Verify `OPENAI_API_KEY` is set correctly and has sufficient credits.

### Streaming Not Working
Check that the response `Content-Type` is `text/event-stream` and the format matches the Vercel AI SDK Data Stream Protocol.

---

## Architecture Diagram

```
┌─────────────────┐         ┌─────────────────┐
│   /chat page    │◀───────▶│  POST /api/chat │
│   (useChat)     │   SSE   │  (FastAPI)      │
└─────────────────┘         └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  OpenAI Agent   │
                            │  (Agents SDK)   │
                            └────────┬────────┘
                                     │ MCP Protocol
                                     ▼
                            ┌─────────────────┐
                            │   MCP Server    │
                            │   (FastMCP)     │
                            │                 │
                            │  @mcp.tool():   │
                            │  - add_task     │
                            │  - list_tasks   │
                            │  - complete_task│
                            │  - update_task  │
                            │  - delete_task  │
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   TaskService   │
                            │  (PostgreSQL)   │
                            └─────────────────┘
```
