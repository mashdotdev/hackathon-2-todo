# Phase III Research: AI-Powered Chatbot with MCP

**Date**: 2025-12-26
**Feature**: 003-phase3-ai-chatbot

## Executive Summary

This document consolidates research findings for implementing the Phase III AI chatbot. The recommended architecture uses **OpenAI Agents SDK** for agent logic with `@function_tool` decorators, **Vercel AI SDK** (`useChat`) for the frontend chat UI, and optionally **MCP SDK** for standardized tool exposure.

---

## 1. OpenAI Agents SDK

### Decision
Use OpenAI Agents SDK v0.6.4 as the primary agent framework.

### Rationale
- Native tool calling via `@function_tool` decorator
- Built-in guardrails for input/output validation
- Session management for conversation history
- Direct integration with OpenAI models
- MCP integration available if needed

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| LangChain | More complex, heavier dependency |
| Custom OpenAI API | Would require building tool calling manually |
| Anthropic Claude SDK | Constitution specifies OpenAI Agents SDK |

### Key APIs

```python
from agents import Agent, Runner, function_tool

@function_tool
async def add_task(title: str, description: str = "") -> dict:
    """Add a new task to the user's task list."""
    return {"id": "uuid", "title": title, "status": "pending"}

agent = Agent(
    name="Task Assistant",
    instructions="You help users manage their todo list.",
    tools=[add_task, list_tasks, complete_task, update_task, delete_task]
)

result = await Runner.run(agent, user_message)
```

### Installation
```bash
pip install openai-agents
```

### Documentation
- https://openai.github.io/openai-agents-python/
- https://openai.github.io/openai-agents-python/tools/

---

## 2. Model Context Protocol (MCP) SDK

### Decision
Use **MCP SDK (FastMCP)** for tool implementation - this is a **hackathon requirement**.

### Rationale
- Constitution explicitly states: "Tool exposure MUST follow MCP (Model Context Protocol) standards"
- Constitution requires: "MCP servers MUST expose stateless tools that interact with the database"
- OpenAI Agents SDK has native MCP integration via `HostedMCPTool` and `MCPServerStreamableHttp`
- FastMCP provides simple decorator-based tool definition

### Implementation

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TodoServer")

@mcp.tool()
def add_task(title: str, user_id: str) -> dict:
    """Add a task for the user."""
    return {"id": "uuid", "title": title, "status": "pending"}

# Mount alongside FastAPI
app.mount("/mcp", mcp.streamable_http_app())
```

### MCP + OpenAI Agents SDK Integration

The OpenAI Agents SDK natively supports MCP servers:

```python
from agents import Agent
from agents.mcp import MCPServerStreamableHttp

# Connect agent to MCP server
mcp_server = MCPServerStreamableHttp(
    url="http://localhost:8001/mcp",
    name="todo-tools"
)

agent = Agent(
    name="Task Assistant",
    instructions="You help users manage their todo list using the available tools.",
    mcp_servers=[mcp_server]
)
```

### Architecture: MCP Server + Agent

```
┌─────────────────┐         ┌─────────────────┐
│  OpenAI Agent   │◀───────▶│   MCP Server    │
│  (Agents SDK)   │  HTTP   │   (FastMCP)     │
│                 │         │                 │
│  - Understands  │         │  @mcp.tool()    │
│    NL intent    │         │  - add_task     │
│  - Calls tools  │         │  - list_tasks   │
│  - Streams resp │         │  - complete_task│
└─────────────────┘         │  - update_task  │
                            │  - delete_task  │
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   TaskService   │
                            │  (PostgreSQL)   │
                            └─────────────────┘
```

### Documentation
- https://github.com/modelcontextprotocol/python-sdk
- https://modelcontextprotocol.io/docs/sdk
- https://openai.github.io/openai-agents-python/mcp/

---

## 3. Chat UI Framework

### Decision
Use **Vercel AI SDK** with `useChat` hook for the frontend.

### Rationale
- Mature ecosystem with excellent Next.js integration
- Simple `useChat` hook handles streaming, state, and UI
- Works with any backend via Data Stream Protocol
- More flexible than ChatKit for custom UI designs

### Alternatives Considered
| Alternative | Why Not Selected |
|-------------|------------------|
| OpenAI ChatKit | Newer, less documentation, more opinionated |
| Custom WebSocket | Would require building streaming from scratch |
| REST polling | Poor UX, no real-time streaming |

### Frontend Pattern

```tsx
'use client';
import { useChat } from '@ai-sdk/react';

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
  });

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((m) => (
          <div key={m.id} className={m.role === 'user' ? 'text-right' : ''}>
            {m.content}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} disabled={isLoading} />
      </form>
    </div>
  );
}
```

### Installation
```bash
npm install ai @ai-sdk/react @ai-sdk/openai
```

### Documentation
- https://ai-sdk.dev/docs/introduction
- https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol

---

## 4. Backend Streaming Protocol

### Decision
Implement Vercel AI SDK Data Stream Protocol for SSE responses.

### Rationale
- Compatible with `useChat` hook out of the box
- Standard SSE format
- Supports text streaming and tool calls

### FastAPI Implementation

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])

    async def generate():
        yield f'0:{json.dumps(response_text)}\n'  # Text delta
        yield f'd:{json.dumps({"finishReason": "stop"})}\n'  # Finish

    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## 5. Database Schema Extension

### Decision
Add `conversations` and `messages` tables to existing schema.

### Rationale
- Conversation history must persist (FR-003, FR-024, FR-025)
- Single conversation per user (out of scope: multiple threads)
- Messages reference both user and conversation

### New Tables

```sql
-- conversations table
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    UNIQUE(user_id)  -- Single conversation per user
);

-- messages table
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id),
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);
```

---

## 6. Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│                 Next.js Frontend                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  /chat page with useChat hook                     │  │
│  │  - Message list display                           │  │
│  │  - Input form                                     │  │
│  │  - Loading states                                 │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
                           │ SSE Stream
                           ▼
┌────────────────────────────────────────────────────────┐
│                 FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  POST /api/chat                                   │  │
│  │  - Receives messages + JWT auth                   │  │
│  │  - Runs OpenAI Agent                              │  │
│  │  - Streams response via SSE                       │  │
│  └──────────────────────────────────────────────────┘  │
│                           │                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  OpenAI Agents SDK                                │  │
│  │  - Task Assistant Agent                           │  │
│  │  - Connected to MCP Server                        │  │
│  │  - Guardrails for validation                      │  │
│  └──────────────────────────────────────────────────┘  │
│                           │                             │
│                           ▼ MCP Protocol (HTTP)         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  MCP Server (FastMCP)                             │  │
│  │  - @mcp.tool() add_task                           │  │
│  │  - @mcp.tool() list_tasks                         │  │
│  │  - @mcp.tool() complete_task                      │  │
│  │  - @mcp.tool() update_task                        │  │
│  │  - @mcp.tool() delete_task                        │  │
│  │  - Mounted at /mcp endpoint                       │  │
│  └──────────────────────────────────────────────────┘  │
│                           │                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Existing Services                                │  │
│  │  - TaskService (CRUD)                             │  │
│  │  - AuthService (JWT validation)                   │  │
│  │  - PostgreSQL (Neon)                              │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 7. Security Considerations

### User Isolation
- All MCP/function tools require `user_id` parameter
- User ID extracted from JWT token on backend
- Tools only query/modify user's own tasks

### Input Validation
- Guardrails for content filtering
- Message length limits (1000 chars)
- Rate limiting on chat endpoint

### Token Handling
- Reuse existing JWT authentication
- Token passed via cookie, extracted by backend
- No API keys exposed to frontend

---

## 8. Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `openai-agents` | 0.6.4 | Agent framework with MCP support |
| `mcp[cli]` | 1.9+ | **MCP SDK (required)** - FastMCP for tool server |
| `ai` | 5.x | Frontend chat hook |
| `@ai-sdk/react` | 5.x | React integration |
| `@ai-sdk/openai` | 5.x | OpenAI provider |

---

## 9. Environment Variables

### Backend (new)
```env
OPENAI_API_KEY=sk-...  # Required for Agents SDK
```

### Frontend (existing)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OpenAI API rate limits | Implement retry with exponential backoff |
| Streaming failures | Graceful error handling, retry button |
| Large conversation context | Limit to last 20 messages |
| Ambiguous user intent | Agent asks clarifying questions |
| Tool execution failures | Return user-friendly error messages |

---

## References

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Vercel AI SDK](https://ai-sdk.dev/docs/introduction)
- [AI SDK Stream Protocol](https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol)
