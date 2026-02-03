# Todo API

FastAPI backend for the Todo application.

## Features

- RESTful API for task management
- PostgreSQL database with SQLModel ORM
- AI-powered chatbot with MCP integration
- JWT authentication
- Health check endpoints

## Development

```bash
# Install dependencies
uv sync

# Run development server
uv run python -m uvicorn src.main:app --reload

# Run tests
uv run pytest
```

## API Endpoints

- `GET /health` - Liveness check
- `GET /ready` - Readiness check with database connectivity
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create a task
- `GET /api/tasks/{id}` - Get a task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `OPENAI_API_KEY` | OpenAI API key for AI features |
