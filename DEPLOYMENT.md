# Phase V Deployment Guide

**Target**: Oracle Kubernetes Engine (OKE) - Always Free Tier
**Architecture**: Event-Driven Microservices with Dapr
**Version**: 2.0.0

## Overview

This guide walks through deploying the Todo application to Oracle Cloud Infrastructure (OKE) with:
- 2 replicas for high availability
- Kafka event streaming (Redpanda Cloud)
- Dapr distributed runtime
- 3 event-driven microservices
- SSL certificates via Let's Encrypt
- CI/CD with GitHub Actions

**Estimated Setup Time**: 45-60 minutes (first time)

---

## Prerequisites

### Required Tools

```bash
# Verify tools installation
kubectl version --client
helm version
dapr version
oci --version
git --version
```

### Required Accounts

1. **Oracle Cloud**: https://cloud.oracle.com (Always Free Tier)
2. **GitHub**: Repository with GHCR access
3. **Redpanda Cloud**: https://redpanda.com/try-redpanda (Serverless tier)
4. **Neon PostgreSQL**: Connection string from Phase II

### Local Environment

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/hackathon-2-todo.git
cd hackathon-2-todo

# Checkout Phase V branch
git checkout 005-phase5-cloud-event-driven
```

---

## Step 1: Create OKE Cluster

### Option A: OCI Console (Recommended)

1. Navigate to: **Developer Services → Kubernetes Clusters (OKE)**
2. Click **"Create Cluster"** → Select **"Quick Create"**
3. Configure:
   - Name: `todo-cluster`
   - Kubernetes Version: `1.28+`
   - Shape: `VM.Standard.E2.1.Micro` (Always Free)
   - Nodes: `2`
4. Click **"Create"** (takes ~10 minutes)

### Option B: OCI CLI

```bash
# Set variables
export COMP_ID=$(oci iam compartment list --query "data[?name=='hackathon-todo'].id | [0]" --raw-output)
export VCN_ID=$(oci network vcn list --compartment-id $COMP_ID --query "data[0].id" --raw-output)

# Create cluster
oci ce cluster create \
  --compartment-id $COMP_ID \
  --name todo-cluster \
  --kubernetes-version v1.28.2 \
  --vcn-id $VCN_ID \
  --wait-for-state SUCCEEDED
```

### Configure kubectl

```bash
# Get cluster OCID
export CLUSTER_ID=$(oci ce cluster list --compartment-id $COMP_ID \
  --name todo-cluster --query 'data[0].id' --raw-output)

# Generate kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_ID \
  --file $HOME/.kube/config \
  --region us-phoenix-1 \
  --token-version 2.0.0

# Test connection
kubectl get nodes
# Expected: 2 nodes in Ready state
```

---

## Step 2: Setup Redpanda Cloud (Kafka)

1. **Create Account**: https://redpanda.com/try-redpanda
2. **Create Serverless Cluster**:
   - Name: `todo-events`
   - Region: `us-west-2` (or closest to OKE)
3. **Create Topics** (via Redpanda Console):
   - `task-events` (partitions: 3, retention: 30 days)
   - `reminders` (partitions: 3, retention: 30 days)
   - `task-updates` (partitions: 3, retention: 30 days)
4. **Create Service Account**:
   - Security → Service Accounts → Create
   - Name: `todo-producer-consumer`
   - Permissions: All on all topics
   - **Save credentials** (bootstrap servers, username, password)

---

## Step 3: Install Infrastructure Components

### Install Dapr

```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=false \
  --set global.logAsJson=true

# Verify
kubectl get pods -n dapr-system
```

### Install NGINX Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer

# Wait for LoadBalancer IP (note it down!)
kubectl get svc -n ingress-nginx -w
```

### Install cert-manager

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# Apply ClusterIssuer
kubectl apply -f infra/kubernetes/cert-manager-issuer.yaml
```

### Install Redis

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami

helm install redis bitnami/redis \
  --namespace todo \
  --create-namespace \
  --set auth.enabled=false \
  --set master.persistence.enabled=false \
  --set replica.replicaCount=0 \
  --set master.resources.requests.cpu=100m \
  --set master.resources.requests.memory=256Mi
```

### Apply Dapr Components

```bash
kubectl apply -f infra/dapr/components/ -n todo
```

---

## Step 4: Configure GitHub Secrets

Navigate to: **GitHub Repo → Settings → Secrets and variables → Actions**

Add the following secrets:

| Secret Name | Value | Source |
|-------------|-------|--------|
| `OCI_CLI_USER` | User OCID | OCI Console → User Settings |
| `OCI_CLI_FINGERPRINT` | API Key Fingerprint | Generate API key |
| `OCI_CLI_KEY_CONTENT` | Private Key Content | API key .pem file |
| `OCI_CLI_TENANCY` | Tenancy OCID | OCI Console → Tenancy |
| `OCI_CLI_REGION` | `us-phoenix-1` | Your OKE region |
| `KUBECONFIG_CONTENT` | `cat ~/.kube/config` | Kubeconfig output |
| `KAFKA_BOOTSTRAP_SERVERS` | Redpanda endpoint | Redpanda Console |
| `KAFKA_USERNAME` | Service account username | Redpanda Console |
| `KAFKA_PASSWORD` | Service account password | Redpanda Console |
| `DATABASE_URL` | `postgresql://...` | Neon Console |
| `GEMINI_API_KEY` | Gemini API key | Phase III |

---

## Step 5: Run Database Migration

```bash
cd backend
export DATABASE_URL="<your-neon-postgresql-url>"
uv run alembic upgrade head
```

---

## Step 6: Update Helm Values

Edit `infra/helm/todo/values.oke.yaml`:

```yaml
global:
  domain: "LOADBALANCER_IP.nip.io"  # Replace with actual IP from Step 3

backend:
  image:
    repository: ghcr.io/YOUR_GITHUB_USERNAME/todo-backend

frontend:
  image:
    repository: ghcr.io/YOUR_GITHUB_USERNAME/todo-frontend

# Update all microservice image repositories similarly

dapr:
  kafka:
    bootstrapServers: "YOUR_REDPANDA_BOOTSTRAP_SERVERS"
    username: "YOUR_KAFKA_USERNAME"
    password: "YOUR_KAFKA_PASSWORD"
```

---

## Step 7: Build and Push Docker Images

```bash
# Set variables
export GHCR_USERNAME="YOUR_GITHUB_USERNAME"
export VERSION="v2.0.0"

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u $GHCR_USERNAME --password-stdin

# Build and push backend
docker build -f infra/docker/backend.Dockerfile \
  -t ghcr.io/$GHCR_USERNAME/todo-backend:$VERSION \
  ./backend
docker push ghcr.io/$GHCR_USERNAME/todo-backend:$VERSION

# Build and push frontend
docker build -f infra/docker/frontend.Dockerfile \
  -t ghcr.io/$GHCR_USERNAME/todo-frontend:$VERSION \
  --build-arg NEXT_PUBLIC_API_URL=https://LOADBALANCER_IP.nip.io \
  ./frontend
docker push ghcr.io/$GHCR_USERNAME/todo-frontend:$VERSION
```

---

## Step 8: Deploy with Helm

```bash
# Deploy application
helm install todo ./infra/helm/todo \
  -f ./infra/helm/todo/values.oke.yaml \
  --namespace todo \
  --create-namespace

# Wait for pods
kubectl get pods -n todo -w
# Expected: backend (2/2), frontend (1/1) - Note: backend has Dapr sidecar
```

---

## Step 9: Verify Deployment

```bash
# Check all pods running
kubectl get pods -n todo

# Check Dapr components
kubectl get components -n todo

# Get application URL
echo "https://$(kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}').nip.io"

# Check backend logs
kubectl logs -n todo -l app=backend -c backend --tail=50

# Check Dapr sidecar
kubectl logs -n todo -l app=backend -c daprd --tail=50
```

---

## Step 10: Test Application

1. **Navigate** to the URL from Step 9
2. **Create account** and login
3. **Create task** (Phase I-IV features should work)
4. **Verify** SSL certificate is valid

---

## Troubleshooting

### Pods Not Starting?

```bash
# Check pod events
kubectl describe pod <pod-name> -n todo

# Common issues:
# - ImagePullBackOff: Check image name and GHCR credentials
# - CrashLoopBackOff: Check logs for startup errors
# - Pending: Check resource limits
```

### Dapr Sidecar Not Injecting?

```bash
# Check annotations
kubectl get deployment backend -n todo -o yaml | grep dapr

# If missing, add annotations:
kubectl patch deployment backend -n todo -p '{
  "spec":{
    "template":{
      "metadata":{
        "annotations":{
          "dapr.io/enabled":"true",
          "dapr.io/app-id":"todo-backend",
          "dapr.io/app-port":"8000"
        }
      }
    }
  }
}'
```

### SSL Certificate Not Provisioning?

```bash
# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager

# Check certificate status
kubectl describe certificate todo-tls -n todo

# Common issues:
# - DNS not propagated: Wait 5-10 minutes
# - Rate limit: Let's Encrypt rate limits (wait 1 hour)
```

---

## Next Steps

- **MVP Complete**: Phase 1-3 (US1) deployed ✅
- **Implement US2**: Advanced task features (priority, tags, search)
- **Implement US3**: Event-driven microservices
- **Implement US4**: CI/CD automation
- **Implement US5**: Dapr integration

---

## Cleanup (When Done)

```bash
# Delete Helm releases
helm uninstall todo -n todo
helm uninstall redis -n todo
helm uninstall cert-manager -n cert-manager
helm uninstall nginx-ingress -n ingress-nginx
helm uninstall dapr -n dapr-system

# Delete OKE cluster
oci ce cluster delete --cluster-id $CLUSTER_ID --force

# Delete Redpanda Cloud cluster (via Console)
```

---

## Summary

**Deployment Time**: ~45 minutes
**Services Deployed**: 2 (backend, frontend) for MVP
**Infrastructure**: OKE (2 nodes), Dapr, Redis, Kafka (Redpanda), NGINX, cert-manager
**Total Cost**: $0/month (within free tiers)

**Success Criteria** (MVP):
- ✅ All pods running with Dapr sidecars
- ✅ Application accessible via HTTPS
- ✅ Phase I-IV features working
- ✅ SSL certificate valid

For Phase V full implementation (microservices, event-driven architecture), see `specs/005-phase5-cloud-event-driven/tasks.md`.
