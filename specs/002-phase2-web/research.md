# Research: Phase II Full-Stack Web Application

**Feature**: 002-phase2-web
**Date**: 2025-12-25
**Spec**: [spec.md](./spec.md)

## Overview

This document consolidates research findings for Phase II technology decisions. All technologies are prescribed by the constitution; this research validates integration patterns and best practices.

---

## 1. Better Auth Integration with Next.js and FastAPI

### Decision
Use Better Auth as the authentication library with JWT tokens for session management.

### Rationale
- Constitution mandates Better Auth with JWT (Principle VII)
- Better Auth provides Next.js integration out of the box
- JWT tokens work well for stateless API authentication
- Supports email/password authentication required by spec

### Integration Pattern
```
Frontend (Next.js) ←→ Better Auth ←→ Backend (FastAPI)
                          ↓
                    Neon PostgreSQL
```

**Flow**:
1. User registers/logs in via Next.js frontend
2. Better Auth handles credential validation and JWT issuance
3. JWT stored in httpOnly cookie (secure)
4. Frontend sends JWT with API requests
5. FastAPI validates JWT on protected endpoints

### Alternatives Considered
| Alternative | Why Not Chosen |
|-------------|----------------|
| NextAuth.js | Constitution specifies Better Auth |
| Clerk | External service, not in constitution |
| Custom JWT | Better Auth provides tested implementation |

---

## 2. SQLModel with Neon PostgreSQL

### Decision
Use SQLModel ORM connected to Neon Serverless PostgreSQL.

### Rationale
- Constitution mandates SQLModel and Neon (Phase II stack)
- SQLModel combines Pydantic + SQLAlchemy (FastAPI native)
- Neon provides serverless PostgreSQL with free tier
- User already confirmed Neon as unified database choice

### Connection Pattern
```python
# Neon connection string format
DATABASE_URL = "postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"
```

**Best Practices**:
- Use connection pooling (Neon has built-in pooler)
- SSL required for all connections
- Use async SQLModel for FastAPI async endpoints
- Run Alembic migrations for schema changes

### Alternatives Considered
| Alternative | Why Not Chosen |
|-------------|----------------|
| SQLite | Not scalable, user chose Neon |
| Raw SQL | SQLModel provides type safety |
| Prisma | Not Python-native |

---

## 3. Next.js 16+ App Router Structure

### Decision
Use Next.js App Router with server components and client-side interactivity.

### Rationale
- Constitution specifies Next.js 16+ with App Router
- App Router provides better performance and SEO
- Server components reduce JavaScript bundle size
- Works well with Tailwind CSS

### Route Structure
```
frontend/src/app/
├── (auth)/
│   ├── login/page.tsx
│   └── register/page.tsx
├── dashboard/
│   └── page.tsx
├── layout.tsx
└── page.tsx (landing/redirect)
```

**Best Practices**:
- Use route groups `(auth)` for layout organization
- Server components for data fetching
- Client components for interactivity (forms, toggles)
- API routes for BFF pattern if needed

### Alternatives Considered
| Alternative | Why Not Chosen |
|-------------|----------------|
| Pages Router | Constitution specifies App Router |
| React SPA | Next.js provides better DX |
| Remix | Constitution specifies Next.js |

---

## 4. FastAPI Backend Structure

### Decision
Use FastAPI with layered architecture: routers, services, models.

### Rationale
- Constitution mandates FastAPI for backend
- FastAPI provides automatic OpenAPI docs (FR-016)
- Native async support for Neon connections
- Pydantic validation aligns with SQLModel

### API Structure
```
backend/src/
├── api/
│   ├── routes/
│   │   ├── auth.py
│   │   └── tasks.py
│   └── deps.py (dependencies)
├── models/
│   ├── user.py
│   └── task.py
├── services/
│   ├── auth_service.py
│   └── task_service.py
└── core/
    ├── config.py
    └── security.py
```

**Best Practices**:
- Use dependency injection for services
- Separate route handlers from business logic
- Use Pydantic schemas for request/response
- JWT validation as middleware/dependency

### Alternatives Considered
| Alternative | Why Not Chosen |
|-------------|----------------|
| Flask | Constitution specifies FastAPI |
| Django | Overkill for API-only backend |
| Express.js | Constitution specifies Python |

---

## 5. Frontend-Backend Communication

### Decision
Direct API calls from Next.js to FastAPI with JWT in Authorization header.

### Rationale
- Simple and clear separation of concerns
- JWT in cookie set by Better Auth
- CORS configured on FastAPI for frontend origin
- No BFF needed for this scope

### API Pattern
```
POST /api/auth/register     → Register new user
POST /api/auth/login        → Login, receive JWT
POST /api/auth/logout       → Invalidate session
GET  /api/tasks             → List user's tasks
POST /api/tasks             → Create task
GET  /api/tasks/{id}        → Get task details
PUT  /api/tasks/{id}        → Update task
DELETE /api/tasks/{id}      → Delete task
PATCH /api/tasks/{id}/complete → Toggle complete
```

### Alternatives Considered
| Alternative | Why Not Chosen |
|-------------|----------------|
| GraphQL | REST is simpler for CRUD |
| tRPC | Adds complexity, not in constitution |
| BFF pattern | Unnecessary for this scope |

---

## 6. Testing Strategy

### Decision
- Backend: pytest with pytest-asyncio for async tests
- Frontend: Jest/Vitest with React Testing Library

### Rationale
- Constitution specifies pytest for backend
- Constitution allows Jest or Vitest for frontend
- Integration tests for API contracts
- Unit tests for business logic

### Test Structure
```
backend/tests/
├── unit/
│   ├── test_task_service.py
│   └── test_auth_service.py
├── integration/
│   ├── test_tasks_api.py
│   └── test_auth_api.py
└── conftest.py

frontend/tests/
├── components/
│   └── TaskList.test.tsx
└── pages/
    └── dashboard.test.tsx
```

---

## 7. Deployment Considerations (for local dev)

### Decision
Use docker-compose for local development with hot reload.

### Rationale
- Matches Phase IV containerization requirement
- Consistent environment across developers
- Easy to add services later (Phase III+)

### Local Setup
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: ${DATABASE_URL}
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
```

**Note**: Neon is cloud-hosted; no local PostgreSQL needed.

---

## Summary of Technology Decisions

| Component | Technology | Source |
|-----------|------------|--------|
| Frontend | Next.js 16+ (App Router) | Constitution |
| Styling | Tailwind CSS | Constitution |
| Backend | Python FastAPI | Constitution |
| ORM | SQLModel | Constitution |
| Database | Neon PostgreSQL | Constitution + User |
| Auth | Better Auth + JWT | Constitution |
| Backend Tests | pytest | Constitution |
| Frontend Tests | Vitest | Constitution |
| Package Manager (Python) | UV | Constitution |
| Package Manager (Node) | npm/pnpm | Standard |

All NEEDS CLARIFICATION items resolved. Ready for Phase 1 design.
