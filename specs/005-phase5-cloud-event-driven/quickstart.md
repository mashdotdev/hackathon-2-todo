# Quickstart Guide: Phase V Deployment to Oracle Cloud (OKE)

**Feature**: Phase V - Cloud Deployment with Event-Driven Architecture
**Date**: 2025-12-30
**Target**: Oracle Kubernetes Engine (OKE) Always Free Tier

## Prerequisites

Before starting, ensure you have:

- [x] **OCI Account**: Oracle Cloud free tier account created
- [x] **Local Tools**:
  - `kubectl` (v1.28+)
  - `helm` (v3.x)
  - `dapr` CLI (v1.12+)
  - `oci` CLI configured
  - `git` client
- [x] **Accounts**:
  - GitHub account with repository access
  - Redpanda Cloud account (free tier)
- [x] **Credentials**:
  - Neon PostgreSQL connection string (from Phase II)
  - GitHub personal access token (for GHCR)

---

## Step 1: Create OKE Cluster

### Option A: Using OCI Console (Recommended for First Time)

1. **Login to OCI Console**: https://cloud.oracle.com
2. **Navigate to**: Developer Services → Kubernetes Clusters (OKE)
3. **Click "Create Cluster"** and select **"Quick Create"**
4. **Configure Cluster**:
   - **Name**: `todo-cluster`
   - **Compartment**: Select or create `hackathon-todo`
   - **Kubernetes Version**: Latest stable (1.28+)
   - **Shape**: `VM.Standard.E2.1.Micro` (Always Free)
   - **Number of Nodes**: 2
   - **VCN**: Create new or select existing
5. **Click "Create"** (takes ~10 minutes)
6. **Wait for Status**: "Active"

### Option B: Using OCI CLI

```bash
# Set variables
export COMP_ID=$(oci iam compartment list --query "data[?name=='hackathon-todo'].id | [0]" --raw-output)
export VCN_ID=$(oci network vcn list --compartment-id $COMP_ID --query "data[0].id" --raw-output)

# Create OKE cluster
oci ce cluster create \
  --compartment-id $COMP_ID \
  --name todo-cluster \
  --kubernetes-version v1.28.2 \
  --vcn-id $VCN_ID \
  --wait-for-state SUCCEEDED
```

---

## Step 2: Configure kubectl Access

```bash
# Get cluster OCID
export CLUSTER_ID=$(oci ce cluster list --compartment-id $COMP_ID \
  --name todo-cluster --query 'data[0].id' --raw-output)

# Generate kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_ID \
  --file $HOME/.kube/config \
  --region us-phoenix-1 \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT

# Test connection
kubectl get nodes
# Expected: 2 nodes in Ready state
```

---

## Step 3: Setup Redpanda Cloud (Kafka)

1. **Create Account**: https://redpanda.com/try-redpanda
2. **Create Cluster**:
   - Name: `todo-events`
   - Region: `us-west-2` (or closest to OKE)
   - Tier: **Serverless** (free)
3. **Create Topics**:
   ```bash
   # Via Redpanda Console → Topics → Create Topic
   - task-events (partitions: 3, retention: 30 days)
   - reminders (partitions: 3, retention: 30 days)
   - task-updates (partitions: 3, retention: 30 days)
   ```
4. **Create Service Account**:
   - Navigate to: Security → Service Accounts
   - Name: `todo-producer-consumer`
   - Permissions: **All** on all topics
   - **Save credentials** (bootstrap servers, username, password)

---

## Step 4: Install Dapr on OKE

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr runtime
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=false \
  --set global.logAsJson=true

# Verify installation
kubectl get pods -n dapr-system
# Expected: dapr-operator, dapr-sidecar-injector, dapr-sentry, dapr-placement (all Running)
```

---

## Step 5: Install Infrastructure Components

### Install NGINX Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer

# Wait for LoadBalancer IP
kubectl get svc -n ingress-nginx -w
# Note the EXTERNAL-IP
```

### Install cert-manager (SSL)

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

### Install Redis (Dapr State Store)

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

---

## Step 6: Configure GitHub Repository Secrets

Navigate to: GitHub Repo → Settings → Secrets and variables → Actions

**Add the following secrets**:

| Secret Name | Value | Source |
|-------------|-------|--------|
| `OCI_CLI_USER` | User OCID | OCI Console → User Settings |
| `OCI_CLI_FINGERPRINT` | API Key Fingerprint | Generate API key |
| `OCI_CLI_KEY_CONTENT` | Private Key Content | API key .pem file |
| `OCI_CLI_TENANCY` | Tenancy OCID | OCI Console → Tenancy |
| `OCI_CLI_REGION` | `us-phoenix-1` | Your OKE region |
| `KUBECONFIG_CONTENT` | `cat ~/.kube/config` | Output of kubeconfig |
| `KAFKA_BOOTSTRAP_SERVERS` | `<cluster>.redpanda.cloud:9092` | Redpanda Console |
| `KAFKA_USERNAME` | Service account username | Redpanda Console |
| `KAFKA_PASSWORD` | Service account password | Redpanda Console |
| `DATABASE_URL` | `postgresql://user:pass@host/db` | Neon Console |

---

## Step 7: Run Database Migration

```bash
# Clone repository
git clone https://github.com/<your-username>/hackathon-2-todo.git
cd hackathon-2-todo

# Checkout Phase V branch
git checkout 005-phase5-cloud-event-driven

# Run migrations locally (or via GitHub Actions)
cd backend
export DATABASE_URL="<neon-postgresql-url>"
uv run alembic upgrade head
```

---

## Step 8: Deploy Application with Helm

### Update Helm Values

Edit `infra/helm/todo/values.oke.yaml`:

```yaml
global:
  domain: "<loadbalancer-ip>.nip.io"  # Use nip.io for free DNS

backend:
  image:
    repository: ghcr.io/<your-username>/todo-backend
    tag: latest
  env:
    DATABASE_URL: "<from-secrets>"
    KAFKA_BOOTSTRAP_SERVERS: "<from-secrets>"

frontend:
  image:
    repository: ghcr.io/<your-username>/todo-frontend
    tag: latest

notificationService:
  image:
    repository: ghcr.io/<your-username>/todo-notification-service
    tag: latest

recurringTasksService:
  image:
    repository: ghcr.io/<your-username>/todo-recurring-tasks-service
    tag: latest

auditService:
  image:
    repository: ghcr.io/<your-username>/todo-audit-service
    tag: latest

dapr:
  enabled: true
  kafka:
    bootstrapServers: "<from-secrets>"
    username: "<from-secrets>"
    password: "<from-secrets>"
```

### Deploy

```bash
# From repository root
helm install todo ./infra/helm/todo \
  -f ./infra/helm/todo/values.oke.yaml \
  --namespace todo \
  --create-namespace

# Wait for pods
kubectl get pods -n todo -w
# Expected: backend, frontend, notification-service, recurring-tasks-service, audit-service (all Running)
```

---

## Step 9: Configure DNS and SSL

### Get LoadBalancer IP

```bash
kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller
# Note EXTERNAL-IP
```

### Option A: Using nip.io (Free, No DNS Setup)

Your application will be available at:
```
http://<EXTERNAL-IP>.nip.io
```

### Option B: Custom Domain

1. **Add A Record**: Point `todo.example.com` to `<EXTERNAL-IP>`
2. **Update Helm values**: Set `global.domain: "todo.example.com"`
3. **Upgrade Helm release**:
   ```bash
   helm upgrade todo ./infra/helm/todo -f ./infra/helm/todo/values.oke.yaml -n todo
   ```
4. **Wait for SSL certificate** (cert-manager auto-provisions from Let's Encrypt):
   ```bash
   kubectl get certificate -n todo
   # Wait for READY=True
   ```

---

## Step 10: Verify Deployment

### Check All Pods Running

```bash
kubectl get pods -n todo
# Expected:
# - backend-xxx (2/2 Running) - app + dapr sidecar
# - frontend-xxx (1/1 Running)
# - notification-service-xxx (2/2 Running)
# - recurring-tasks-service-xxx (2/2 Running)
# - audit-service-xxx (2/2 Running)
```

### Check Dapr Components

```bash
kubectl get components -n todo
# Expected: pubsub, statestore, secretstore
```

### Test Application

```bash
# Get application URL
echo "http://$(kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}').nip.io"

# Open in browser
# - Create an account
# - Add a task with priority and tags
# - Verify notifications appear
# - Check recurring task creates new instance
```

### Check Logs

```bash
# Backend logs
kubectl logs -n todo -l app=backend -c backend --tail=50

# Event processing (Notification Service)
kubectl logs -n todo -l app=notification-service -c notification-service --tail=50

# Kafka events (check Dapr sidecar)
kubectl logs -n todo -l app=backend -c daprd | grep pubsub
```

---

## Step 11: Enable CI/CD (Optional)

Once manual deployment works, enable automated deployments:

1. **Merge to main branch**:
   ```bash
   git checkout main
   git merge 005-phase5-cloud-event-driven
   git push origin main
   ```

2. **GitHub Actions will automatically**:
   - Build Docker images
   - Push to GitHub Container Registry
   - Deploy to OKE cluster
   - Run smoke tests

3. **Monitor deployment**:
   - GitHub Repo → Actions → deploy-oke workflow
   - Check logs for deployment status

---

## Troubleshooting

### Pods not starting?

```bash
# Check pod events
kubectl describe pod <pod-name> -n todo

# Common issues:
# - ImagePullBackOff: Check image name and GHCR credentials
# - CrashLoopBackOff: Check logs for startup errors
# - Pending: Check resource limits (may exceed free tier)
```

### Dapr sidecar not injecting?

```bash
# Check annotations
kubectl get deployment backend -n todo -o yaml | grep dapr

# Expected annotations:
# dapr.io/enabled: "true"
# dapr.io/app-id: "todo-backend"
# dapr.io/app-port: "8000"

# If missing, update deployment
kubectl patch deployment backend -n todo -p '{"spec":{"template":{"metadata":{"annotations":{"dapr.io/enabled":"true"}}}}}'
```

### Kafka connection errors?

```bash
# Test Kafka connectivity from backend pod
kubectl exec -it <backend-pod> -n todo -c backend -- sh

# Inside pod:
curl -v telnet://<kafka-bootstrap-servers>:9092
# Should connect successfully

# Check Dapr pub/sub component
kubectl get component pubsub -n todo -o yaml
```

### SSL certificate not provisioning?

```bash
# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager

# Check certificate status
kubectl describe certificate todo-tls -n todo

# Common issues:
# - DNS not propagated: Wait 5-10 minutes
# - Rate limit hit: Let's Encrypt has rate limits, wait 1 hour
```

---

## Next Steps

1. **Load Testing**: Run k6 or Locust to verify 500 concurrent users target
2. **Monitoring**: Set up Prometheus/Grafana for metrics visualization
3. **Alerting**: Configure alerts for high error rates, latency spikes
4. **Documentation**: Update README.md with production URL and demo video
5. **Demo Video**: Record 90-second demo for hackathon submission

---

## Resource Cleanup (When Done)

```bash
# Delete Helm release
helm uninstall todo -n todo
helm uninstall redis -n todo
helm uninstall cert-manager -n cert-manager
helm uninstall nginx-ingress -n ingress-nginx
helm uninstall dapr -n dapr-system

# Delete OKE cluster (via OCI Console or CLI)
oci ce cluster delete --cluster-id $CLUSTER_ID --force

# Delete Redpanda Cloud cluster (via Redpanda Console)
```

---

## Summary

**Deployment Time**: ~45 minutes (first time)
**Services Deployed**: 5 (backend, frontend, notification, recurring-tasks, audit)
**Infrastructure**: OKE (2 nodes), Dapr, Redis, Kafka (Redpanda Cloud), NGINX, cert-manager
**Total Cost**: $0/month (within free tiers)

**Success Criteria**:
- ✅ All pods running (2/2 with Dapr sidecars)
- ✅ Application accessible via HTTPS URL
- ✅ Task CRUD operations working with priority/tags/due dates
- ✅ Notifications appearing for task events
- ✅ Recurring tasks creating new instances automatically
- ✅ Audit logs capturing all operations

**Support**: For issues, check `specs/005-phase5-cloud-event-driven/research.md` or create GitHub issue.
