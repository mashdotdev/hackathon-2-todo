# Tasks: Phase III AI-Powered Chatbot with MCP

**Input**: Design documents from `/specs/003-phase3-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - minimal tests included for critical MCP tools only.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure) ✅

**Purpose**: Install dependencies and configure environment for Phase III

- [x] T001 Install backend dependencies: `uv add openai-agents "mcp[cli]"` in backend/
- [x] T002 Install frontend dependencies: `npm install ai @ai-sdk/react` in frontend/
- [x] T003 [P] Add OPENAI_API_KEY to backend/.env.example and document in README
- [x] T004 [P] Create backend/src/mcp/__init__.py package structure
- [x] T005 [P] Create backend/src/mcp/tools/__init__.py package structure

---

## Phase 2: Foundational (Blocking Prerequisites) ✅

**Purpose**: Database models and MCP server infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models & Migration

- [x] T006 Create Conversation model in backend/src/models/conversation.py per data-model.md
- [x] T007 Create Message model in backend/src/models/message.py per data-model.md
- [x] T008 Create MessageRole enum in backend/src/models/message.py
- [x] T009 Update User model relationship in backend/src/models/user.py (add conversation relationship)
- [x] T010 Export new models from backend/src/models/__init__.py
- [x] T011 Generate Alembic migration: `alembic revision --autogenerate -m "add_conversations_and_messages"`
- [x] T012 Apply migration: `alembic upgrade head`

### Chat Schemas

- [x] T013 [P] Create ChatRequest schema in backend/src/schemas/chat.py per chat-api.yaml
- [x] T014 [P] Create ChatMessage schema in backend/src/schemas/chat.py
- [x] T015 [P] Create ChatHistoryResponse schema in backend/src/schemas/chat.py
- [x] T016 [P] Create StoredMessage schema in backend/src/schemas/chat.py

### Chat Service (Conversation Persistence)

- [x] T017 Create ChatService class in backend/src/services/chat_service.py
- [x] T018 Implement get_or_create_conversation() in backend/src/services/chat_service.py
- [x] T019 Implement get_messages() with limit in backend/src/services/chat_service.py
- [x] T020 Implement add_message() in backend/src/services/chat_service.py
- [x] T021 Implement clear_history() in backend/src/services/chat_service.py

### MCP Server Setup

- [x] T022 Create FastMCP server instance in backend/src/mcp/server.py
- [x] T023 Configure MCP server with Streamable HTTP transport in backend/src/mcp/server.py
- [x] T024 Mount MCP server at /mcp endpoint in backend/src/main.py

**Checkpoint**: Foundation ready - MCP server running, database models created

---

## Phase 3: User Story 7 - Chat Interface and Message History (Priority: P1) 🎯 MVP ✅

**Goal**: Logged-in users can access a chat interface with message history persistence

**Independent Test**: Navigate to /chat, send a message, verify it appears and persists across page refresh

### Backend: Chat API Endpoints

- [x] T025 [US7] Create chat router in backend/src/api/routes/chat.py
- [x] T026 [US7] Implement POST /api/chat endpoint skeleton (placeholder response) in backend/src/api/routes/chat.py
- [x] T027 [US7] Implement GET /api/chat/history endpoint in backend/src/api/routes/chat.py
- [x] T028 [US7] Implement DELETE /api/chat/history endpoint in backend/src/api/routes/chat.py
- [x] T029 [US7] Register chat router in backend/src/main.py
- [x] T030 [US7] Add JWT authentication dependency to chat endpoints in backend/src/api/routes/chat.py

### Frontend: Chat Page

- [x] T031 [P] [US7] Create ChatMessage component in frontend/src/components/ChatMessage.tsx
- [x] T032 [P] [US7] Create ChatInput component in frontend/src/components/ChatInput.tsx
- [x] T033 [US7] Create chat page with useChat hook in frontend/src/app/chat/page.tsx
- [x] T034 [US7] Add authentication guard to chat page in frontend/src/app/chat/page.tsx
- [x] T035 [US7] Implement message history loading on page mount in frontend/src/app/chat/page.tsx
- [x] T036 [US7] Add loading indicator while assistant responds in frontend/src/app/chat/page.tsx
- [x] T037 [US7] Add chat API methods to frontend/src/lib/api.ts (getChatHistory, clearChatHistory)
- [x] T038 [US7] Add navigation link to chat from dashboard in frontend/src/app/dashboard/page.tsx

**Checkpoint**: Chat UI functional with message persistence - can send/receive messages (placeholder responses)

---

## Phase 4: User Story 1 - Natural Language Task Creation (Priority: P1) ✅

**Goal**: Users can create tasks via natural language commands like "Add a task to buy groceries"

**Independent Test**: Send "Add a task to buy groceries" in chat, verify task appears in task list

### MCP Tool: add_task

- [x] T039 [US1] Create add_task tool in backend/src/mcp/tools/add_task.py per mcp-tools.md contract
- [x] T040 [US1] Implement task creation logic using TaskService in backend/src/mcp/tools/add_task.py
- [x] T041 [US1] Add user_id parameter validation in backend/src/mcp/tools/add_task.py
- [x] T042 [US1] Return structured JSON response per contract in backend/src/mcp/tools/add_task.py
- [x] T043 [US1] Register add_task tool in backend/src/mcp/server.py

**Checkpoint**: Can create tasks via add_task MCP tool

---

## Phase 5: User Story 2 - View Tasks via Conversation (Priority: P1) ✅

**Goal**: Users can view their tasks via natural language queries like "Show me my tasks"

**Independent Test**: Send "Show me my tasks" in chat, verify response lists all user tasks

### MCP Tool: list_tasks

- [x] T044 [US2] Create list_tasks tool in backend/src/mcp/tools/list_tasks.py per mcp-tools.md contract
- [x] T045 [US2] Implement task retrieval with optional status filter in backend/src/mcp/tools/list_tasks.py
- [x] T046 [US2] Add user_id parameter validation in backend/src/mcp/tools/list_tasks.py
- [x] T047 [US2] Return structured JSON response with task list and count in backend/src/mcp/tools/list_tasks.py
- [x] T048 [US2] Register list_tasks tool in backend/src/mcp/server.py

**Checkpoint**: Can view tasks via list_tasks MCP tool

---

## Phase 6: Agent Integration (Connects US1 + US2) ✅

**Goal**: Connect OpenAI Agent to MCP server so natural language commands work end-to-end

**Independent Test**: Full flow - "Add task buy milk" then "Show my tasks" - both work via chat

### Agent Service

- [x] T049 Create AgentService class in backend/src/services/agent_service.py
- [x] T050 Initialize OpenAI Agent with MCP server connection in backend/src/services/agent_service.py
- [x] T051 Configure agent instructions for task management in backend/src/services/agent_service.py
- [x] T052 Implement run_agent() method with user context in backend/src/services/agent_service.py
- [x] T053 Implement streaming response generation in backend/src/services/agent_service.py

### Update Chat Endpoint

- [x] T054 Integrate AgentService into POST /api/chat in backend/src/api/routes/chat.py
- [x] T055 Implement SSE streaming response per Data Stream Protocol in backend/src/api/routes/chat.py
- [x] T056 Save user message to database before agent call in backend/src/api/routes/chat.py
- [x] T057 Save assistant response to database after completion in backend/src/api/routes/chat.py
- [x] T058 Pass user_id to agent for MCP tool calls in backend/src/api/routes/chat.py

**Checkpoint**: Full conversational task creation and viewing working end-to-end

---

## Phase 7: User Story 3 - Mark Task Complete (Priority: P2) ✅

**Goal**: Users can mark tasks complete via natural language like "I finished buying groceries"

**Independent Test**: Create task, then say "Mark it as done", verify status changes to completed

### MCP Tool: complete_task

- [x] T059 [US3] Create complete_task tool in backend/src/mcp/tools/complete_task.py per mcp-tools.md contract
- [x] T060 [US3] Implement fuzzy task matching by title in backend/src/mcp/tools/complete_task.py
- [x] T061 [US3] Handle TASK_NOT_FOUND and AMBIGUOUS_TASK errors in backend/src/mcp/tools/complete_task.py
- [x] T062 [US3] Return structured JSON response in backend/src/mcp/tools/complete_task.py
- [x] T063 [US3] Register complete_task tool in backend/src/mcp/server.py

**Checkpoint**: Can complete tasks via natural language

---

## Phase 8: User Story 4 - Update Task (Priority: P2) ✅

**Goal**: Users can update tasks via natural language like "Change 'Buy groceries' to 'Buy organic groceries'"

**Independent Test**: Create task, say "Rename it to X", verify title changes

### MCP Tool: update_task

- [x] T064 [US4] Create update_task tool in backend/src/mcp/tools/update_task.py per mcp-tools.md contract
- [x] T065 [US4] Implement fuzzy task matching by title in backend/src/mcp/tools/update_task.py
- [x] T066 [US4] Support updating title and/or description in backend/src/mcp/tools/update_task.py
- [x] T067 [US4] Handle TASK_NOT_FOUND error in backend/src/mcp/tools/update_task.py
- [x] T068 [US4] Register update_task tool in backend/src/mcp/server.py

**Checkpoint**: Can update tasks via natural language

---

## Phase 9: User Story 5 - Delete Task (Priority: P2) ✅

**Goal**: Users can delete tasks via natural language with confirmation like "Delete the groceries task"

**Independent Test**: Create task, say "Delete it", confirm, verify task removed

### MCP Tool: delete_task

- [x] T069 [US5] Create delete_task tool in backend/src/mcp/tools/delete_task.py per mcp-tools.md contract
- [x] T070 [US5] Implement fuzzy task matching by title in backend/src/mcp/tools/delete_task.py
- [x] T071 [US5] Implement confirmation flow (requires_confirmation flag) in backend/src/mcp/tools/delete_task.py
- [x] T072 [US5] Handle confirmed deletion in backend/src/mcp/tools/delete_task.py
- [x] T073 [US5] Register delete_task tool in backend/src/mcp/server.py

**Checkpoint**: Can delete tasks via natural language with confirmation

---

## Phase 10: User Story 6 - Conversational Context (Priority: P3)

**Goal**: Assistant maintains context for follow-up commands like "Actually, mark it as done"

**Independent Test**: Create task, then say "mark it as done" without naming it - should complete the just-created task

### Context Enhancement

- [ ] T074 [US6] Enhance agent instructions for context awareness in backend/src/services/agent_service.py
- [ ] T075 [US6] Pass conversation history to agent for context in backend/src/services/agent_service.py
- [ ] T076 [US6] Limit conversation history to last 20 messages in backend/src/services/agent_service.py
- [ ] T077 [US6] Handle "undo" requests with helpful response in agent instructions

**Checkpoint**: Conversational context working - follow-ups understood

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, and refinements

- [x] T078 [P] Add error handling for AI service unavailability in backend/src/api/routes/chat.py
- [ ] T079 [P] Add rate limiting consideration for chat endpoint in backend/src/api/routes/chat.py
- [x] T080 [P] Add message length validation (max 1000 chars) in backend/src/schemas/chat.py
- [x] T081 [P] Add loading state styling in frontend/src/components/ChatInput.tsx
- [x] T082 [P] Add error display component for failed messages in frontend/src/app/chat/page.tsx
- [x] T083 Export all MCP tools from backend/src/mcp/tools/__init__.py
- [ ] T084 Add structured logging for agent calls in backend/src/services/agent_service.py
- [ ] T085 Run quickstart.md validation - verify all setup steps work

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──────────────────────────────────┐
                                                  ▼
Phase 2 (Foundational) ───────────────────────────┤ BLOCKS ALL
                                                  ▼
Phase 3 (US7: Chat UI) ───────────────────────────┤ MVP Foundation
                                                  ▼
Phase 4 (US1: Add Task) ──┬───────────────────────┤
Phase 5 (US2: List Tasks) ┘                       │ P1 Stories
                                                  ▼
Phase 6 (Agent Integration) ──────────────────────┤ Connects P1 Stories
                                                  ▼
Phase 7 (US3: Complete) ──┬───────────────────────┤
Phase 8 (US4: Update) ────┤                       │ P2 Stories (parallel OK)
Phase 9 (US5: Delete) ────┘                       │
                                                  ▼
Phase 10 (US6: Context) ──────────────────────────┤ P3 Story
                                                  ▼
Phase 11 (Polish) ────────────────────────────────┘
```

### User Story Dependencies

- **US7 (Chat UI)**: Can start after Phase 2 - Foundation for all other stories
- **US1 (Add Task)**: Can start after Phase 2 - No dependencies on other stories
- **US2 (List Tasks)**: Can start after Phase 2 - No dependencies on other stories
- **US3 (Complete)**: Can start after Phase 6 - Needs agent integration
- **US4 (Update)**: Can start after Phase 6 - Needs agent integration
- **US5 (Delete)**: Can start after Phase 6 - Needs agent integration
- **US6 (Context)**: Can start after Phase 9 - Needs all tools available

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T003 (env docs) || T004 (mcp package) || T005 (tools package)
```

**Phase 2 (Foundational)**:
```
T013 (ChatRequest) || T014 (ChatMessage) || T015 (ChatHistoryResponse) || T016 (StoredMessage)
```

**Phase 3 (US7)**:
```
T031 (ChatMessage component) || T032 (ChatInput component)
```

**Phase 4-5 (US1 + US2)** - Can run in parallel:
```
T039-T043 (add_task) || T044-T048 (list_tasks)
```

**Phase 7-9 (US3 + US4 + US5)** - Can run in parallel:
```
T059-T063 (complete_task) || T064-T068 (update_task) || T069-T073 (delete_task)
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: US7 Chat UI
4. Complete Phase 4-5: US1 + US2 (can parallel)
5. Complete Phase 6: Agent Integration
6. **STOP and VALIDATE**: Test full add/list flow end-to-end
7. Deploy/demo MVP

### Full Feature Delivery

After MVP validation:
1. Add Phase 7-9: US3 + US4 + US5 (can parallel)
2. Add Phase 10: US6 (context awareness)
3. Complete Phase 11: Polish
4. Final validation against all acceptance scenarios

---

## Task Summary

| Phase | Tasks | Parallel | Description |
|-------|-------|----------|-------------|
| 1 | T001-T005 | 3 | Setup |
| 2 | T006-T024 | 4 | Foundational |
| 3 | T025-T038 | 2 | US7: Chat UI |
| 4 | T039-T043 | 0 | US1: Add Task |
| 5 | T044-T048 | 0 | US2: List Tasks |
| 6 | T049-T058 | 0 | Agent Integration |
| 7 | T059-T063 | 0 | US3: Complete Task |
| 8 | T064-T068 | 0 | US4: Update Task |
| 9 | T069-T073 | 0 | US5: Delete Task |
| 10 | T074-T077 | 0 | US6: Context |
| 11 | T078-T085 | 5 | Polish |
| **Total** | **85** | **14** | |

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [US#] label maps task to specific user story
- Each user story checkpoint allows independent testing
- Constitution requires MCP SDK - all tools use @mcp.tool() decorator
- Commit after each task or logical group
- Stop at any checkpoint to validate progress
