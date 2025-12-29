# Todo Application - Hackathon Project

A full-stack todo application built with modern technologies, featuring AI-powered task assistance and Kubernetes deployment.

## Phases

| Phase | Description | Status |
|-------|-------------|--------|
| I | Python Console App | Complete |
| II | Full-Stack Web App (FastAPI + Next.js) | Complete |
| III | AI-Powered Chatbot with MCP | Complete |
| IV | Local Kubernetes Deployment | Complete |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Kubernetes                        │
│  ┌─────────────┐    ┌─────────────┐                │
│  │  Frontend   │    │   Backend   │                │
│  │  (Next.js)  │────│  (FastAPI)  │────────────────│──► Neon PostgreSQL
│  └─────────────┘    └─────────────┘                │
│         │                  │                        │
│         └────────┬─────────┘                       │
│                  ▼                                  │
│           ┌───────────┐                            │
│           │  Ingress  │                            │
│           │  (nginx)  │                            │
│           └───────────┘                            │
└─────────────────────────────────────────────────────┘
                   │
                   ▼
              http://todo.local
```

## Quick Start (Phase IV)

### Prerequisites

- Docker Desktop
- Minikube
- kubectl
- Helm 3.x

### Deployment

```bash
# Start Minikube
minikube start --driver=docker --memory=4096 --cpus=2
minikube addons enable ingress

# Build images
eval $(minikube docker-env)
docker build -t todo-backend:latest -f infra/docker/backend.Dockerfile ./backend
docker build -t todo-frontend:latest -f infra/docker/frontend.Dockerfile ./frontend

# Deploy with Helm
cp infra/helm/todo/secrets.example.yaml infra/helm/todo/secrets.yaml
# Edit secrets.yaml with your values
helm install todo ./infra/helm/todo -f ./infra/helm/todo/secrets.yaml

# Access
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
open http://todo.local
```

For detailed instructions, see [Phase IV Quickstart](specs/004-phase4-kubernetes/quickstart.md).

## Project Structure

```
hackathon-2-todo/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── main.py            # API entry point
│   │   ├── api/               # API routes
│   │   ├── core/              # Database, config
│   │   ├── models/            # SQLModel models
│   │   └── chatkit/           # AI chatbot (MCP)
│   └── pyproject.toml
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # App router
│   │   ├── components/        # React components
│   │   └── lib/               # Utilities
│   └── package.json
├── infra/                      # Infrastructure (Phase IV)
│   ├── docker/                # Dockerfiles
│   └── helm/todo/             # Helm chart
└── specs/                      # SDD specifications
    ├── 001-phase1-console/
    ├── 002-phase2-web/
    ├── 003-phase3-ai-chatbot/
    └── 004-phase4-kubernetes/
```

## Development

### Backend (FastAPI)

```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (Neon) |
| `SECRET_KEY` | JWT signing key |
| `OPENAI_API_KEY` | OpenAI API key for AI features |

## Technologies

- **Backend**: Python 3.13+, FastAPI, SQLModel, UV
- **Frontend**: TypeScript 5.x, Next.js 15, React 19, Tailwind CSS
- **Database**: PostgreSQL (Neon Serverless)
- **AI**: OpenAI GPT, Model Context Protocol (MCP)
- **Infrastructure**: Docker, Kubernetes (Minikube), Helm

## AIOps

Use kubectl-ai for natural language cluster operations:

```bash
brew install sozercan/tap/kubectl-ai
export OPENAI_API_KEY="your-key"
kubectl-ai "show me all pods in the todo namespace"
```

## License

MIT
