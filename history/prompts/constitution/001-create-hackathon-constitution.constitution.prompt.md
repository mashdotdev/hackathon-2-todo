---
id: 001
title: Create Hackathon Constitution
stage: constitution
date: 2025-12-25
surface: agent
model: claude-opus-4-5
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "hackathon", "spec-driven-development", "setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

read this whole google doc and created a detailed constitution for this project https://docs.google.com/document/d/1KHxeDNnqG9uew-rEabQc5H8u3VmEN3OaJ_A1ZVVr9vY/edit?tab=t.0

User provided the full content of the "Hackathon II - Todo Spec-Driven Development" document after the Google Doc was inaccessible via direct URL fetch. The document describes a 5-phase hackathon project to build a Todo application that evolves from a console app to a cloud-native AI chatbot.

Key requirements from the document:
- Must use Spec-Driven Development with Claude Code and Spec-Kit Plus
- No manual coding allowed - must refine specs until Claude Code generates correct output
- 5 phases: Console App → Full-Stack Web → AI Chatbot → Local K8s → Cloud Deployment
- Technology stack: Python, FastAPI, Next.js, SQLModel, Neon DB, OpenAI Agents SDK, MCP SDK, Docker, Kubernetes, Kafka, Dapr
- Feature progression: Basic → Intermediate → Advanced

## Response snapshot

Created a comprehensive constitution for the "Evolution of Todo" hackathon project with:

**6 Core Principles:**
1. Spec-Driven Development (NON-NEGOTIABLE)
2. No Manual Coding (NON-NEGOTIABLE)
3. Test-First Development
4. AI-Native Architecture
5. Cloud-Native Deployment
6. Progressive Enhancement

**3 Additional Sections:**
1. Technology Stack Requirements (per phase)
2. Development Workflow (monorepo structure, commands, API/DB standards)
3. Governance (amendment procedure, versioning, compliance)

Constitution version: 1.0.0
All dependent templates verified for consistency.

## Outcome

- Impact: Created foundational constitution document that governs all development for the hackathon project
- Tests: N/A - constitution document
- Files: `.specify/memory/constitution.md` (created)
- Next prompts: `/sp.specify` for Phase I console app feature, create CLAUDE.md root file
- Reflection: Google Doc fetch required user copy-paste workaround; extracted all key principles and requirements successfully

## Evaluation notes (flywheel)

- Failure modes observed: WebFetch unable to access Google Docs due to JavaScript rendering and authentication requirements
- Graders run and results (PASS/FAIL): N/A - document creation
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): For future Google Doc access, immediately request copy-paste from user
