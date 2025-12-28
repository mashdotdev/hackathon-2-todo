---
id: "0002"
title: "Phase 3 Implementation Planning"
stage: plan
date: 2025-12-26
surface: agent
model: claude-opus-4-5-20251101
feature: 003-phase3-ai-chatbot
branch: 003-phase3-ai-chatbot
user: developer
command: /sp.plan
labels: ["phase3", "ai-chatbot", "mcp", "planning", "architecture"]
links:
  spec: specs/003-phase3-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-phase3-ai-chatbot/plan.md
  - specs/003-phase3-ai-chatbot/research.md
  - specs/003-phase3-ai-chatbot/data-model.md
  - specs/003-phase3-ai-chatbot/quickstart.md
  - specs/003-phase3-ai-chatbot/contracts/chat-api.yaml
  - specs/003-phase3-ai-chatbot/contracts/mcp-tools.md
tests:
  - N/A (planning phase)
---

## Prompt

/sp.plan

## Response snapshot

Completed Phase 0 (Research) and Phase 1 (Design & Contracts) of the implementation planning workflow:

**Phase 0 - Research:**
- Researched OpenAI Agents SDK v0.6.4 (tool calling, guardrails, sessions)
- Researched MCP SDK (decided @function_tool is simpler for Phase III scope)
- Researched chat UI options (Vercel AI SDK chosen over ChatKit)
- Explored Phase II codebase architecture

**Phase 1 - Design:**
- Created data-model.md with Conversation and Message entities
- Created chat-api.yaml (OpenAPI spec for /api/chat endpoint)
- Created mcp-tools.md (tool contracts for 5 CRUD tools)
- Created quickstart.md (setup guide)
- Updated plan.md with full technical context and project structure

**Key Decisions:**
1. OpenAI Agents SDK with @function_tool (not standalone MCP server)
2. Vercel AI SDK useChat hook (more mature than ChatKit)
3. SSE streaming via Data Stream Protocol
4. Single conversation thread per user
5. Fuzzy matching for task identification

## Outcome

- ✅ Impact: Complete planning artifacts for Phase III implementation
- 🧪 Tests: N/A (planning phase - test strategy defined for implementation)
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, quickstart.md, chat-api.yaml, mcp-tools.md)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Architecture follows constitution principles; chose simplicity (useChat over ChatKit, @function_tool over MCP server)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check PASS (all 7 principles verified)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
