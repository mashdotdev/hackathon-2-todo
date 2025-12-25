# Quickstart: Phase II Full-Stack Web Application

**Feature**: 002-phase2-web
**Date**: 2025-12-25
**Spec**: [spec.md](./spec.md)

## Prerequisites

### Required Software

| Software | Version | Check Command |
|----------|---------|---------------|
| Python | 3.13+ | `python --version` |
| UV | Latest | `uv --version` |
| Node.js | 20+ LTS | `node --version` |
| npm | 10+ | `npm --version` |
| Git | Latest | `git --version` |

### Accounts Required

| Service | Purpose | Setup |
|---------|---------|-------|
| Neon | PostgreSQL database | [neon.tech](https://neon.tech) - Free tier |

## Project Structure

```
hackathon-2-todo/
├── backend/               # FastAPI application
│   ├── src/
│   │   ├── api/          # Route handlers
│   │   ├── core/         # Config, security
│   │   ├── models/       # SQLModel entities
│   │   └── services/     # Business logic
│   ├── tests/
│   ├── pyproject.toml
│   └── .env.example
├── frontend/              # Next.js application
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
│   ├── tests/
│   ├── package.json
│   └── .env.example
└── specs/002-phase2-web/  # This feature's docs
```

## Setup Instructions

### 1. Clone and Branch

```bash
git clone https://github.com/mashdotdev/hackathon-2-todo.git
cd hackathon-2-todo
git checkout 002-phase2-web
```

### 2. Set Up Neon Database

1. Go to [neon.tech](https://neon.tech) and create a free account
2. Create a new project (e.g., "hackathon-todo")
3. Copy the connection string from the dashboard
4. It looks like: `postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require`

### 3. Backend Setup

```bash
cd backend

# Create environment file
cp .env.example .env

# Edit .env with your Neon connection string
# DATABASE_URL=postgresql://...

# Install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn src.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

API docs at: http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd frontend

# Create environment file
cp .env.example .env.local

# Edit .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

### 5. Verify Setup

1. Open http://localhost:3000
2. Click "Register" and create an account
3. Log in with your credentials
4. Create a task
5. Verify task appears in the dashboard

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
```

### Frontend (.env.local)

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Environment
NODE_ENV=development
```

## Common Commands

### Backend

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Lint code
uv run ruff check src/

# Format code
uv run ruff format src/

# Type check
uv run mypy src/

# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```

### Frontend

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run typecheck

# Build for production
npm run build
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login user | No |
| POST | `/api/auth/logout` | Logout user | Yes |
| GET | `/api/auth/me` | Get current user | Yes |
| GET | `/api/tasks` | List user's tasks | Yes |
| POST | `/api/tasks` | Create task | Yes |
| GET | `/api/tasks/{id}` | Get task | Yes |
| PUT | `/api/tasks/{id}` | Update task | Yes |
| DELETE | `/api/tasks/{id}` | Delete task | Yes |
| PATCH | `/api/tasks/{id}/complete` | Toggle complete | Yes |

## Frontend Routes

| Route | Page | Auth Required |
|-------|------|---------------|
| `/` | Landing/Redirect | No |
| `/login` | Login form | No |
| `/register` | Registration form | No |
| `/dashboard` | Task list | Yes |

## Testing

### Run All Tests

```bash
# Backend
cd backend && uv run pytest

# Frontend
cd frontend && npm test
```

### Test Categories

**Backend:**
- `tests/unit/` - Service and model unit tests
- `tests/integration/` - API endpoint tests

**Frontend:**
- `tests/components/` - React component tests
- `tests/pages/` - Page integration tests

## Troubleshooting

### Database Connection Issues

```bash
# Test Neon connection
uv run python -c "from src.core.config import settings; print(settings.DATABASE_URL)"

# Check if database is accessible
uv run python -c "from sqlmodel import create_engine; create_engine('...').connect()"
```

### CORS Errors

Ensure `FRONTEND_URL` in backend `.env` matches your frontend URL exactly.

### JWT Token Issues

- Clear browser cookies/localStorage
- Check token expiration in `ACCESS_TOKEN_EXPIRE_MINUTES`
- Verify `SECRET_KEY` is consistent

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
uv run uvicorn src.main:app --port 8001
```

## Next Steps

After Phase II:
- Phase III adds AI chatbot interface with MCP
- Phase IV adds Kubernetes deployment
- Phase V adds cloud deployment with monitoring
