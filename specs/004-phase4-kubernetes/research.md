# Phase IV Research: Local Kubernetes Deployment

**Feature**: 004-phase4-kubernetes
**Date**: 2025-12-28
**Status**: Complete

## Overview

This document consolidates research findings for containerizing and deploying the Todo application to a local Kubernetes cluster using Minikube and Helm.

---

## 1. Docker Containerization

### 1.1 Backend Dockerfile Strategy

**Decision**: Multi-stage build with Python 3.13-slim base image

**Rationale**:
- Multi-stage builds minimize final image size by separating build dependencies from runtime
- Python 3.13-slim provides a minimal base (~50MB vs ~150MB for full image)
- UV package manager is faster than pip and produces reproducible builds

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Python 3.13 (full) | Larger image size (~150MB vs ~50MB) |
| Alpine-based image | Compatibility issues with some Python packages requiring glibc |
| Single-stage build | Includes build tools and dev dependencies in final image |

**Implementation Pattern**:
```dockerfile
# Stage 1: Build with UV
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
# ... install dependencies

# Stage 2: Runtime
FROM python:3.13-slim
# Copy only runtime dependencies
```

### 1.2 Frontend Dockerfile Strategy

**Decision**: Multi-stage build with Node.js 20-alpine and Next.js standalone output

**Rationale**:
- Next.js standalone output mode creates minimal production bundles
- Alpine base provides smallest Node.js image (~40MB)
- Build-time optimization with output: 'standalone' in next.config

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Node.js Debian-based | Larger image size (~350MB vs ~100MB) |
| Static export | Loses server-side features needed for auth |
| Single-stage build | Includes node_modules and build tools |

**Implementation Pattern**:
```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
# ... install deps

# Stage 2: Build
FROM node:20-alpine AS builder
# ... run next build

# Stage 3: Runtime
FROM node:20-alpine AS runner
# Copy standalone output only
```

---

## 2. Kubernetes Architecture

### 2.1 Resource Organization

**Decision**: Single namespace `todo` with separate deployments for backend and frontend

**Rationale**:
- Namespace isolation provides clean resource grouping
- Separate deployments allow independent scaling
- Service mesh not needed for this scale

**Resource Structure**:
```
todo (namespace)
├── backend-deployment
├── backend-service (ClusterIP)
├── frontend-deployment
├── frontend-service (ClusterIP)
├── ingress (NGINX)
├── configmap-backend
├── configmap-frontend
└── secret-db
```

### 2.2 Ingress Controller

**Decision**: NGINX Ingress Controller (Minikube addon)

**Rationale**:
- Built-in Minikube addon with `minikube addons enable ingress`
- Standard Kubernetes Ingress API compatibility
- Simple path-based routing for backend/frontend

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Traefik | Additional installation complexity, not needed for local dev |
| NodePort services | Less elegant routing, exposes internal ports |
| LoadBalancer | Requires additional setup (e.g., MetalLB) on Minikube |

### 2.3 Health Check Endpoints

**Decision**: Separate `/health` and `/ready` endpoints

**Rationale**:
- `/health` (liveness): Returns OK if process is running
- `/ready` (readiness): Returns OK only when database connection is verified
- Follows Kubernetes best practices for self-healing

**Backend Implementation** (already has `/health`, need `/ready`):
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    # Verify database connection
    try:
        # Execute simple query
        return {"status": "ready"}
    except:
        raise HTTPException(503, "Database not ready")
```

**Frontend Implementation**:
- Next.js provides built-in `/api/health` pattern via API routes

---

## 3. Helm Chart Design

### 3.1 Chart Structure

**Decision**: Single umbrella chart with backend and frontend as subcomponents

**Rationale**:
- Single `helm install` deploys entire stack
- Shared values for common configuration (namespace, image tags)
- Allows per-component customization via values.yaml

**Chart Structure**:
```
helm/todo/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── namespace.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── ingress.yaml
│   ├── configmap-backend.yaml
│   ├── configmap-frontend.yaml
│   └── secret-db.yaml
└── .helmignore
```

### 3.2 Values Configuration

**Decision**: Hierarchical values with component-specific overrides

**Key Values**:
```yaml
# Global settings
namespace: todo
environment: development

# Backend configuration
backend:
  replicas: 1
  image:
    repository: todo-backend
    tag: latest
  resources:
    limits:
      memory: "256Mi"
      cpu: "200m"
  config:
    logLevel: INFO

# Frontend configuration
frontend:
  replicas: 1
  image:
    repository: todo-frontend
    tag: latest
  resources:
    limits:
      memory: "128Mi"
      cpu: "100m"

# Ingress configuration
ingress:
  enabled: true
  host: todo.local
```

---

## 4. Configuration Management

### 4.1 ConfigMaps

**Decision**: Separate ConfigMaps for backend and frontend

**Backend ConfigMap**:
- `LOG_LEVEL`: Logging verbosity
- `CORS_ORIGINS`: Allowed CORS origins
- `API_VERSION`: Current API version

**Frontend ConfigMap**:
- `NEXT_PUBLIC_API_URL`: Backend API URL

### 4.2 Secrets

**Decision**: Kubernetes Secret for sensitive data

**Secret Contents**:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `OPENAI_API_KEY`: OpenAI API key for chat

**Security Notes**:
- Secrets are base64 encoded (not encrypted) by default
- For production, use external secret management (Sealed Secrets, Vault)
- Local development accepts this limitation

---

## 5. AIOps Integration

### 5.1 kubectl-ai

**Decision**: Install kubectl-ai for natural language cluster operations

**Rationale**:
- Aligns with hackathon's AI-native focus
- Reduces kubectl command memorization
- Provides learning aid for Kubernetes operations

**Installation**:
```bash
# Using Homebrew (macOS/Linux)
brew install sozercan/tap/kubectl-ai

# Using Go
go install github.com/sozercan/kubectl-ai@latest
```

**Example Queries**:
- "Show me all pods in the todo namespace"
- "Why is the backend pod restarting?"
- "Scale backend to 2 replicas"

### 5.2 Kagent (Optional)

**Decision**: Document as optional enhancement

**Rationale**:
- More complex setup than kubectl-ai
- Provides advanced cluster analysis
- Useful for production scenarios

---

## 6. Monitoring Stack (Optional)

### 6.1 Prometheus

**Decision**: Use kube-prometheus-stack Helm chart for quick setup

**Rationale**:
- Pre-configured Prometheus with Kubernetes service discovery
- Includes standard dashboards
- Simple installation via Helm

**Installation**:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

### 6.2 Application Metrics

**Decision**: Use prometheus-fastapi-instrumentator for backend metrics

**Rationale**:
- Automatic instrumentation of FastAPI endpoints
- Standard Prometheus metrics format
- Minimal code changes required

**Metrics Exposed**:
- `http_requests_total`: Request count by method, path, status
- `http_request_duration_seconds`: Request latency histogram
- `http_requests_in_progress`: Current in-flight requests

---

## 7. Development Workflow

### 7.1 Local Image Registry

**Decision**: Use Minikube's built-in Docker daemon

**Rationale**:
- No external registry needed for local development
- `eval $(minikube docker-env)` exposes Minikube's Docker
- Images built in this context are available to the cluster

**Workflow**:
```bash
# Point shell to Minikube's Docker
eval $(minikube docker-env)

# Build images (they're now in Minikube)
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Deploy with imagePullPolicy: Never
helm install todo ./helm/todo
```

### 7.2 Hot Reload During Development

**Decision**: Document volume mount pattern for development

**Rationale**:
- Development speed requires hot reload
- Separate dev-values.yaml with host volume mounts
- Not used in "production-like" local testing

---

## 8. Technical Decisions Summary

| Category | Decision | Key Benefit |
|----------|----------|-------------|
| Backend Image | Multi-stage Python 3.13-slim | ~100MB image size |
| Frontend Image | Multi-stage Node 20-alpine + standalone | ~150MB image size |
| Orchestration | Minikube with Docker driver | Easy local setup |
| Ingress | NGINX via Minikube addon | Standard API, simple routing |
| Package Manager | Helm 3 | Templating, versioned releases |
| Health Checks | /health + /ready endpoints | K8s self-healing |
| Config | ConfigMaps + Secrets | 12-factor compliance |
| AIOps | kubectl-ai | AI-assisted operations |
| Monitoring | kube-prometheus-stack (optional) | Standard observability |

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Windows compatibility | Document WSL 2 requirement clearly |
| Resource constraints | Provide minimum Minikube resource requirements |
| Image pull failures | Use local image builds, imagePullPolicy: Never |
| Database connectivity | Verify Neon allows external connections from containers |
| Port conflicts | Use Ingress instead of NodePort to avoid conflicts |

---

## 10. References

- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Kubernetes Health Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
