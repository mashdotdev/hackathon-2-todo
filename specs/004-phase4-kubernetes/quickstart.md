# Phase IV Quickstart: Local Kubernetes Deployment

**Feature**: 004-phase4-kubernetes
**Date**: 2025-12-28

## Prerequisites

Ensure the following tools are installed:

| Tool | Version | Installation |
|------|---------|--------------|
| Docker Desktop | Latest | [docker.com/products/docker-desktop](https://docker.com/products/docker-desktop) |
| Minikube | Latest | `brew install minikube` or [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | Latest | `brew install kubectl` or included with Docker Desktop |
| Helm | 3.x | `brew install helm` or [helm.sh](https://helm.sh/docs/intro/install/) |

**Windows Users**: Must use WSL 2 for all commands.

---

## Quick Start (5 Minutes)

### 1. Start Minikube

```bash
# Start Minikube with Docker driver (recommended)
minikube start --driver=docker --memory=4096 --cpus=2

# Enable ingress addon
minikube addons enable ingress

# Verify cluster is running
kubectl cluster-info
```

### 2. Build Docker Images

```bash
# Point shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend image
docker build -t todo-backend:latest -f infra/docker/backend.Dockerfile ./backend

# Build frontend image
docker build -t todo-frontend:latest -f infra/docker/frontend.Dockerfile ./frontend

# Verify images exist
docker images | grep todo
```

### 3. Configure Secrets

```bash
# Create secrets file from template
cp infra/helm/todo/secrets.example.yaml infra/helm/todo/secrets.yaml

# Edit with your values (base64 encoded)
# DATABASE_URL, SECRET_KEY, OPENAI_API_KEY
```

**Encoding values**:
```bash
echo -n "your-database-url" | base64
echo -n "your-secret-key" | base64
echo -n "your-openai-api-key" | base64
```

### 4. Deploy with Helm

```bash
# Install the application
helm install todo ./infra/helm/todo -f ./infra/helm/todo/secrets.yaml

# Watch pods start
kubectl get pods -n todo -w

# Wait for all pods to be Ready
kubectl wait --for=condition=ready pod -l app=todo-backend -n todo --timeout=120s
kubectl wait --for=condition=ready pod -l app=todo-frontend -n todo --timeout=120s
```

### 5. Access the Application

```bash
# Add host entry (run once)
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Open in browser
open http://todo.local
# Or on Linux: xdg-open http://todo.local
```

---

## Common Operations

### View Logs

```bash
# Backend logs
kubectl logs -l app=todo-backend -n todo -f

# Frontend logs
kubectl logs -l app=todo-frontend -n todo -f
```

### Scale Deployment

```bash
# Scale backend to 2 replicas
helm upgrade todo ./infra/helm/todo --set backend.replicas=2

# Verify scaling
kubectl get pods -n todo
```

### Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap backend-config -n todo

# Restart pods to pick up changes
kubectl rollout restart deployment todo-backend -n todo
```

### Rollback

```bash
# View history
helm history todo

# Rollback to previous version
helm rollback todo 1
```

### Uninstall

```bash
# Remove application
helm uninstall todo

# Stop Minikube
minikube stop
```

---

## AIOps with kubectl-ai

### Installation

```bash
# macOS/Linux
brew install sozercan/tap/kubectl-ai

# Or using Go
go install github.com/sozercan/kubectl-ai@latest

# Set OpenAI API key
export OPENAI_API_KEY="your-api-key"
```

### Example Queries

```bash
# List all pods
kubectl-ai "show me all pods in the todo namespace"

# Check pod health
kubectl-ai "why is the backend pod not ready?"

# Get resource usage
kubectl-ai "what pods are using the most memory?"

# Scale deployment
kubectl-ai "scale the backend deployment to 3 replicas"
```

### Optional: kagent (Alternative)

kagent is another AI-powered Kubernetes assistant that can be used as an alternative to kubectl-ai.

```bash
# Install kagent
pip install kagent

# Set up authentication
kagent auth configure

# Example usage
kagent "show me the status of my todo application"
kagent "why is the backend pod restarting?"
kagent "help me debug the ingress configuration"
```

For more information, see the [kagent documentation](https://github.com/kagent-ai/kagent).

---

## Monitoring (Optional)

### Install Prometheus Stack

```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3001:80 -n monitoring
# Open http://localhost:3001 (admin/prom-operator)
```

---

## Troubleshooting

### Pods stuck in Pending

```bash
# Check events
kubectl describe pod <pod-name> -n todo

# Common causes:
# - Insufficient resources: increase Minikube memory/cpu
# - Image pull errors: verify images exist with `docker images`
```

### ImagePullBackOff

```bash
# Ensure Minikube's Docker is used
eval $(minikube docker-env)

# Rebuild images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Set imagePullPolicy to Never in values.yaml
```

### Connection Refused to Database

```bash
# Check secret is mounted
kubectl exec -it <backend-pod> -n todo -- env | grep DATABASE

# Verify Neon allows external connections
# Check Neon dashboard for IP allowlisting
```

### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n todo

# Verify addon is enabled
minikube addons enable ingress

# Check ingress controller pods
kubectl get pods -n ingress-nginx
```

---

## Project Structure

```
infra/
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── helm/
│   └── todo/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── secrets.example.yaml
│       └── templates/
│           ├── _helpers.tpl
│           ├── namespace.yaml
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── ingress.yaml
│           ├── configmap-backend.yaml
│           ├── configmap-frontend.yaml
│           └── secret-db.yaml
└── k8s/
    └── (raw manifests for reference)
```

---

## Environment Variables

### Backend

| Variable | Source | Description |
|----------|--------|-------------|
| DATABASE_URL | Secret | PostgreSQL connection string |
| SECRET_KEY | Secret | JWT signing key |
| OPENAI_API_KEY | Secret | OpenAI API key |
| LOG_LEVEL | ConfigMap | Logging verbosity |
| CORS_ORIGINS | ConfigMap | Allowed CORS origins |

### Frontend

| Variable | Source | Description |
|----------|--------|-------------|
| NEXT_PUBLIC_API_URL | ConfigMap | Backend API URL |

---

## Success Criteria Verification

```bash
# SC-001: Deployment completes in <5 minutes
time helm install todo ./infra/helm/todo

# SC-002: Pods ready in <2 minutes
kubectl wait --for=condition=ready pod -l app=todo-backend -n todo --timeout=120s

# SC-003: Zero data loss on restart
kubectl rollout restart deployment todo-backend -n todo
# Verify tasks persist

# SC-004: Upgrade/rollback in <1 minute
time helm upgrade todo ./infra/helm/todo --set backend.replicas=2
time helm rollback todo 1

# SC-005: kubectl-ai works
kubectl-ai "show me backend pod logs"

# SC-008: Image sizes
docker images | grep todo
# backend: <500MB, frontend: <200MB
```
