# Research & Technology Decisions: Phase V

**Feature**: Phase V - Cloud Deployment with Event-Driven Architecture
**Date**: 2025-12-30
**Status**: Complete

## Overview

This document captures all technology research, decisions, and setup procedures for Phase V deployment to Oracle Cloud Infrastructure (OKE) with event-driven architecture using Kafka and Dapr.

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Cloud Provider** | Oracle Cloud (OKE) | Always Free Tier, cost-effective |
| **Kubernetes** | Oracle Kubernetes Engine | 2 nodes, 1 OCPU each, free tier |
| **Event Streaming** | Redpanda Cloud | Managed Kafka, free tier <1GB/month |
| **Distributed Runtime** | Dapr 1.12+ | Pub/sub, state, secrets abstraction |
| **State Store** | Redis on OKE | Fast in-memory, Dapr-supported |
| **Container Registry** | GitHub Container Registry | Free, GitHub Actions integration |
| **CI/CD** | GitHub Actions | Free for public repos |
| **Ingress** | NGINX Ingress Controller | Battle-tested, free SSL |
| **SSL Certificates** | cert-manager + Let's Encrypt | Free automated certificates |
| **Scheduling** | APScheduler | Lightweight Python cron |
| **Notifications** | In-app (database) | Simplest, no external deps |

---

## 1. Oracle Kubernetes Engine (OKE) Configuration

### Decision

Use **OKE Always Free Tier** with 2 compute nodes (1 OCPU, 6GB RAM each).

### Setup Procedure

**Option A: OCI Console (GUI)**

1. **Create Compartment** (if needed):
   - Navigate to: Identity & Security > Compartments
   - Create compartment: `hackathon-todo`

2. **Create VCN (Virtual Cloud Network)**:
   - Navigate to: Networking > Virtual Cloud Networks
   - Click "Start VCN Wizard"
   - Select "Create VCN with Internet Connectivity"
   - VCN Name: `todo-vcn`
   - CIDR Block: `10.0.0.0/16`
   - Public Subnet CIDR: `10.0.0.0/24`
   - Private Subnet CIDR: `10.0.1.0/24`

3. **Create OKE Cluster**:
   - Navigate to: Developer Services > Kubernetes Clusters (OKE)
   - Click "Create Cluster"
   - Select "Quick Create" workflow
   - **Cluster Configuration**:
     - Name: `todo-cluster`
     - Compartment: `hackathon-todo`
     - Kubernetes Version: Latest stable (1.28+)
     - Visibility Type: Public Endpoint
     - Shape: VM.Standard.E2.1.Micro (Always Free)
     - Node Pool: 2 nodes
     - VCN: Select `todo-vcn` created above
   - Click "Next" and review
   - Click "Create Cluster" (takes ~10 minutes)

4. **Configure kubectl Access**:
   - After cluster is Active, click "Access Cluster"
   - Follow instructions to download kubeconfig:
     ```bash
     oci ce cluster create-kubeconfig \
       --cluster-id <cluster-ocid> \
       --file $HOME/.kube/config \
       --region us-phoenix-1 \
       --token-version 2.0.0
     ```
   - Test connection: `kubectl get nodes`

**Option B: Terraform (Infrastructure as Code)**

See `infra/terraform/oke/` for automated cluster creation (to be generated during implementation).

### Resource Limits (Always Free Tier)

- **Nodes**: 2 max
- **OCPU**: 1 per node (2 total)
- **RAM**: 6GB per node (12GB total)
- **Storage**: 100GB block volume (total, not per node)
- **Bandwidth**: 10TB outbound/month

**Pod Resource Allocation Strategy**:
```yaml
# Per pod (5 services: backend, frontend, notification, recurring-tasks, audit)
resources:
  requests:
    cpu: 100m      # 0.1 OCPU
    memory: 512Mi  # 512MB RAM
  limits:
    cpu: 500m      # 0.5 OCPU max burst
    memory: 1Gi    # 1GB RAM max
```

**Calculation**: 5 services × 512MB = 2.5GB baseline (leaves ~9.5GB for Dapr sidecars, Redis, system pods)

### Alternative Cloud Providers (Rejected)

| Provider | Cost | Reason Rejected |
|----------|------|----------------|
| DigitalOcean DOKS | $12/month | Not free, but better docs |
| Azure AKS | $70/month | Expensive for 2-node cluster |
| GCP GKE | $75/month | User specified Oracle Cloud |

---

## 2. Kafka Provider: Redpanda Cloud

### Decision

Use **Redpanda Cloud Serverless Tier** (Kafka-compatible, free for <1GB/month).

### Setup Procedure

1. **Create Account**:
   - Navigate to: https://redpanda.com/try-redpanda
   - Sign up with GitHub account
   - Select "Serverless" tier (free)

2. **Create Cluster**:
   - Cluster Name: `todo-events`
   - Region: **us-west-2** (match OKE region for latency)
   - Click "Create cluster"

3. **Create Topics**:
   ```bash
   # Via Redpanda Console (GUI) or rpk CLI
   rpk topic create task-events --partitions 3 --retention 2592000000  # 30 days
   rpk topic create reminders --partitions 3 --retention 2592000000
   rpk topic create task-updates --partitions 3 --retention 2592000000
   ```

4. **Create Service Account**:
   - Navigate to: Security > Service Accounts
   - Create account: `todo-producer-consumer`
   - Grant permissions: **All** on topics `task-events`, `reminders`, `task-updates`
   - Download credentials:
     - Bootstrap servers: `<cluster-id>.us-west-2.redpanda.cloud:9092`
     - SASL mechanism: SCRAM-SHA-256
     - Username: `<service-account-name>`
     - Password: `<generated-password>`

5. **Test Connection**:
   ```bash
   rpk topic produce task-events \
     --brokers=<bootstrap-servers> \
     --user=<username> \
     --password=<password> \
     --sasl-mechanism=SCRAM-SHA-256
   ```

### Kafka Topic Configuration

| Topic | Partitions | Retention | Purpose |
|-------|-----------|-----------|---------|
| `task-events` | 3 | 30 days | All task lifecycle events |
| `reminders` | 3 | 30 days | Reminder scheduled/triggered |
| `task-updates` | 3 | 30 days | Task metadata changes |

**Partitioning Strategy**: Partition by `task_id` (ensures event ordering per task).

### Alternative Kafka Providers (Rejected)

| Provider | Cost | Reason Rejected |
|----------|------|----------------|
| Strimzi (self-hosted) | Free | Complex ops, requires 3+ pods for HA |
| Confluent Cloud | $100+/month | Expensive |
| AWS MSK | $150+/month | Not on Oracle Cloud |

---

## 3. Dapr State Store: Redis

### Decision

Deploy **Redis** on OKE as a single pod (sufficient for demo scale).

### Setup Procedure

**Helm Chart Deployment** (recommended):

```bash
# Add Bitnami Helm repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Redis
helm install redis bitnami/redis \
  --namespace todo \
  --set auth.enabled=false \
  --set master.persistence.enabled=false \
  --set replica.replicaCount=0 \
  --set master.resources.requests.cpu=100m \
  --set master.resources.requests.memory=256Mi
```

**Dapr State Store Component** (see `infra/dapr/components/redis-statestore.yaml`):

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-master.todo.svc.cluster.local:6379
  - name: redisPassword
    value: ""
```

### Alternative State Stores (Rejected)

| Provider | Reason Rejected |
|----------|----------------|
| PostgreSQL | Slower than Redis, not ideal for conversation state |
| Cosmos DB | Expensive, Azure-specific |
| In-memory (no persistence) | Data loss on pod restart |

---

## 4. CI/CD: GitHub Actions

### Decision

Use **GitHub Actions** for automated build, test, and deployment to OKE.

### Setup Procedure

1. **Create OCI Service Account** (for GitHub Actions):
   ```bash
   # On local machine with OCI CLI configured
   oci iam user create \
     --name github-actions-deployer \
     --description "Service account for GitHub Actions CI/CD"

   # Generate API key
   oci iam user api-key upload \
     --user-id <user-ocid> \
     --key-file ~/.oci/github_actions_key.pem
   ```

2. **Create GitHub Repository Secrets**:
   Navigate to: GitHub Repo > Settings > Secrets and variables > Actions

   Add secrets:
   - `OCI_CLI_USER`: `<user-ocid>`
   - `OCI_CLI_FINGERPRINT`: `<key-fingerprint>`
   - `OCI_CLI_KEY_CONTENT`: `<contents of github_actions_key.pem>`
   - `OCI_CLI_TENANCY`: `<tenancy-ocid>`
   - `OCI_CLI_REGION`: `us-phoenix-1`
   - `KUBECONFIG_CONTENT`: `<contents of ~/.kube/config>`
   - `KAFKA_BOOTSTRAP_SERVERS`: `<redpanda-bootstrap-servers>`
   - `KAFKA_USERNAME`: `<service-account-username>`
   - `KAFKA_PASSWORD`: `<service-account-password>`
   - `DATABASE_URL`: `<neon-postgresql-url>`

3. **GitHub Actions Workflows** (see `.github/workflows/`):
   - `build-and-test.yml`: CI pipeline (runs on PR)
   - `deploy-oke.yml`: CD pipeline (runs on merge to main)
   - `build-images.yml`: Build Docker images, push to ghcr.io
   - `rollback.yml`: Manual rollback workflow

### Workflow Triggers

- **build-and-test.yml**: On `pull_request` to `main` or `005-phase5-cloud-event-driven`
- **deploy-oke.yml**: On `push` to `main` branch
- **build-images.yml**: On tag push (`v*.*.*`)
- **rollback.yml**: Manual trigger (`workflow_dispatch`)

### Alternative CI/CD (Rejected)

| Provider | Reason Rejected |
|----------|----------------|
| GitLab CI | Requires GitLab migration |
| Jenkins | Requires hosting, operational overhead |
| OCI DevOps | Less mature, limited docs |

---

## 5. Container Registry: GitHub Container Registry

### Decision

Use **GitHub Container Registry (ghcr.io)** for Docker images.

### Setup Procedure

1. **Authenticate GitHub Actions**:
   ```yaml
   # Already built-in to GitHub Actions
   - name: Login to GitHub Container Registry
     uses: docker/login-action@v2
     with:
       registry: ghcr.io
       username: ${{ github.actor }}
       password: ${{ secrets.GITHUB_TOKEN }}
   ```

2. **Image Naming Convention**:
   ```
   ghcr.io/<username>/todo-backend:latest
   ghcr.io/<username>/todo-frontend:latest
   ghcr.io/<username>/todo-notification-service:latest
   ghcr.io/<username>/todo-recurring-tasks-service:latest
   ghcr.io/<username>/todo-audit-service:latest
   ```

3. **Image Visibility**: Set to `public` for hackathon demo

### Alternative Registries (Rejected)

| Provider | Reason Rejected |
|----------|----------------|
| OCI Registry (OCIR) | Requires tenancy setup, complex auth |
| Docker Hub | Rate limits (100 pulls/6 hours) |

---

## 6. Ingress and SSL Certificates

### Decision

Use **NGINX Ingress Controller** with **cert-manager** for Let's Encrypt certificates.

### Setup Procedure

**Install NGINX Ingress Controller**:

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer
```

**Install cert-manager**:

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

**Create Let's Encrypt ClusterIssuer** (see `infra/kubernetes/cert-manager-issuer.yaml`):

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com  # Change to actual email
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

**Ingress Resource** (see `infra/helm/todo/templates/ingress.yaml`):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - todo.example.com
    secretName: todo-tls
  rules:
  - host: todo.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
```

**DNS Configuration**:
1. Get LoadBalancer IP: `kubectl get svc -n ingress-nginx`
2. Create A record: `todo.example.com` → `<LoadBalancer-IP>`

### Alternative Ingress (Rejected)

| Provider | Reason Rejected |
|----------|----------------|
| OCI Load Balancer | Paid service |
| Traefik | Less familiar, smaller community |

---

## 7. Recurring Task Scheduling: APScheduler

### Decision

Use **APScheduler** library for Python-based cron job scheduling.

### Implementation Pattern

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

# Daily recurrence: every day at midnight UTC
scheduler.add_job(
    generate_daily_tasks,
    trigger=CronTrigger(hour=0, minute=0),
    id='daily_tasks',
    replace_existing=True
)

# Weekly recurrence: every Monday at midnight UTC
scheduler.add_job(
    generate_weekly_tasks,
    trigger=CronTrigger(day_of_week='mon', hour=0, minute=0),
    id='weekly_tasks',
    replace_existing=True
)

# Monthly recurrence: first day of month at midnight UTC
scheduler.add_job(
    generate_monthly_tasks,
    trigger=CronTrigger(day=1, hour=0, minute=0),
    id='monthly_tasks',
    replace_existing=True
)

scheduler.start()
```

### Configuration

- **Job Store**: In-memory (MemoryJobStore) for demo
- **Executor**: ThreadPoolExecutor with 10 workers
- **Timezone**: UTC (convert user's due dates to UTC)
- **Misfire Grace Time**: 300 seconds (5 minutes)

### Production Considerations (Future)

For production, use persistent job store:
```python
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobstores = {
    'default': SQLAlchemyJobStore(url='postgresql://...')
}
scheduler = BackgroundScheduler(jobstores=jobstores)
```

### Alternative Schedulers (Rejected)

| Provider | Reason Rejected |
|----------|----------------|
| Dapr Jobs API | Alpha status, breaking changes likely |
| Celery Beat | Heavyweight, requires Redis/RabbitMQ |
| Kubernetes CronJobs | Coarse-grained, creates pods per job |

---

## 8. Notification Delivery: In-App Notifications

### Decision

Implement **in-app notifications** stored in PostgreSQL, displayed in UI badge.

### Database Schema

```sql
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    task_id UUID REFERENCES tasks(task_id),
    notification_type VARCHAR(50) NOT NULL,  -- 'reminder', 'completion', 'created'
    message TEXT NOT NULL,
    sent_at TIMESTAMP NOT NULL DEFAULT NOW(),
    delivery_status VARCHAR(20) DEFAULT 'sent',  -- 'sent', 'read', 'failed'
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_status ON notifications(user_id, delivery_status);
```

### API Endpoints

```
GET    /api/{user_id}/notifications?unread_only=true
PATCH  /api/{user_id}/notifications/{notification_id}/mark_read
```

### UI Implementation

- **Badge**: Display unread count in navigation bar
- **Panel**: Dropdown or sidebar showing recent notifications
- **Polling**: Frontend polls `/api/{user_id}/notifications?unread_only=true` every 30 seconds

### Alternative Notification Methods (Rejected)

| Method | Reason Rejected |
|--------|----------------|
| Email | Requires SMTP, deliverability issues, user verification |
| SMS | Expensive (Twilio ~$0.0075/SMS), requires phone numbers |
| WebSocket push | Complex, persistent connections, scaling challenges |

---

## 9. Database Schema Migration: Alembic

### Decision

Use **Alembic** for database schema migrations (extends existing Neon PostgreSQL).

### Setup Procedure

**Initialize Alembic** (if not already initialized):

```bash
cd backend
uv run alembic init alembic
```

**Configure** (`backend/alembic/env.py`):

```python
from src.core.database import DATABASE_URL
from src.models import Task, User, TaskEvent, RecurringTaskSchedule, Notification, AuditLog

config.set_main_option('sqlalchemy.url', DATABASE_URL)
target_metadata = Base.metadata  # Import from models
```

### Migration for Phase V

**Create migration**:

```bash
uv run alembic revision --autogenerate -m "phase5_event_driven_schema"
```

**Migration will add**:
- New columns to `tasks` table: `priority`, `tags`, `due_date`, `recurrence_pattern`, `reminder_lead_time`
- New tables: `task_events`, `recurring_task_schedules`, `notifications`, `audit_logs`
- Indexes for performance: `idx_tasks_priority`, `idx_tasks_tags`, `idx_tasks_due_date`

**Apply migration**:

```bash
# Local development
uv run alembic upgrade head

# Production (via GitHub Actions)
kubectl exec -it <backend-pod> -- uv run alembic upgrade head
```

### Backward Compatibility

All new columns are nullable or have defaults:
```python
priority: Optional[str] = Field(default="Medium")
tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
due_date: Optional[datetime] = None
recurrence_pattern: str = Field(default="none")
reminder_lead_time: Optional[int] = None  # minutes
```

Old API clients can continue using existing endpoints; new fields ignored if not provided.

---

## 10. Dapr Installation on OKE

### Decision

Install **Dapr 1.12+** on OKE cluster via Helm chart.

### Setup Procedure

**Install Dapr CLI** (local development):

```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash

# Windows
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

**Install Dapr on OKE**:

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=false \
  --set global.logAsJson=true \
  --set global.metrics.enabled=true
```

**Verify installation**:

```bash
kubectl get pods -n dapr-system
# Should see: dapr-operator, dapr-sidecar-injector, dapr-sentry, dapr-placement
```

### Dapr Components

**Pub/Sub (Kafka)** - `infra/dapr/components/kafka-pubsub.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: todo
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "<redpanda-bootstrap-servers>"
  - name: authType
    value: "password"
  - name: saslUsername
    secretKeyRef:
      name: kafka-credentials
      key: username
  - name: saslPassword
    secretKeyRef:
      name: kafka-credentials
      key: password
  - name: saslMechanism
    value: "SCRAM-SHA-256"
```

**State Store (Redis)** - `infra/dapr/components/redis-statestore.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-master.todo.svc.cluster.local:6379
```

**Secrets Store (Kubernetes)** - `infra/dapr/components/kubernetes-secrets.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
  namespace: todo
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

### Dapr Sidecar Injection

**Enable via annotation** (`infra/helm/todo/templates/backend-deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
      - name: backend
        image: ghcr.io/<username>/todo-backend:latest
```

### Dapr Observability

**Enable Zipkin tracing** (`infra/dapr/config/dapr-config.yaml`):

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing
  namespace: todo
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
  metric:
    enabled: true
```

---

## 11. Inter-Service Communication Patterns

### Decision

Use **Dapr service invocation** for synchronous calls, **Dapr pub/sub** for asynchronous events.

### Patterns

**Synchronous (Service Invocation)**:

```python
# Backend calls Recurring Tasks Service
from dapr.clients import DaprClient

with DaprClient() as client:
    resp = client.invoke_method(
        app_id='recurring-tasks-service',
        method_name='schedules',
        data=json.dumps({'task_id': task_id, 'pattern': 'daily'}),
        http_verb='POST'
    )
```

**Asynchronous (Pub/Sub)**:

```python
# Backend publishes task-created event
from dapr.clients import DaprClient

event = {
    'event_id': str(uuid.uuid4()),
    'event_type': 'task-created',
    'task_id': task.task_id,
    'user_id': task.user_id,
    'timestamp': datetime.utcnow().isoformat(),
    'payload': task.dict()
}

with DaprClient() as client:
    client.publish_event(
        pubsub_name='pubsub',
        topic_name='task-events',
        data=json.dumps(event)
    )
```

**Subscribing to Events**:

```python
# Notification Service subscribes to task-events
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub='pubsub', topic='task-events')
async def handle_task_event(event_data: dict):
    # Process event, create notification
    await notification_service.create_notification(event_data)
```

### Retry and Circuit Breaking

Dapr provides automatic retries (default: 3 attempts) and circuit breaking. Configure via Resiliency spec:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: resiliency
spec:
  policies:
    retries:
      DefaultRetryPolicy:
        policy: constant
        duration: 1s
        maxRetries: 3
    circuitBreakers:
      DefaultCircuitBreakerPolicy:
        maxRequests: 5
        timeout: 10s
        trip: consecutiveFailures >= 3
```

---

## 12. Distributed Tracing Setup

### Decision

Use **Zipkin** for distributed tracing (Dapr-integrated).

### Setup Procedure

**Install Zipkin**:

```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zipkin
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: zipkin
  template:
    metadata:
      labels:
        app: zipkin
    spec:
      containers:
      - name: zipkin
        image: openzipkin/zipkin:latest
        ports:
        - containerPort: 9411
---
apiVersion: v1
kind: Service
metadata:
  name: zipkin
  namespace: default
spec:
  selector:
    app: zipkin
  ports:
  - port: 9411
    targetPort: 9411
  type: LoadBalancer
EOF
```

**Configure Dapr to use Zipkin** (see section 10 above).

**Access Zipkin UI**:

```bash
kubectl port-forward svc/zipkin 9411:9411
# Open browser: http://localhost:9411
```

### Correlation IDs

All services generate correlation IDs for request tracing:

```python
import uuid
from contextvars import ContextVar

correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default=None)

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
    correlation_id_var.set(correlation_id)

    response = await call_next(request)
    response.headers['X-Correlation-ID'] = correlation_id
    return response
```

Log correlation ID in all structured logs:

```python
logger.info("Processing task event", extra={
    'correlation_id': correlation_id_var.get(),
    'event_type': event['event_type'],
    'task_id': event['task_id']
})
```

---

## Summary

All technology decisions are finalized and setup procedures documented. Ready for implementation phase.

**Key Takeaways**:
- **Cost-optimized**: OCI Always Free Tier + Redpanda Cloud free tier = $0/month
- **Managed services**: Redpanda, GitHub Actions, GitHub Container Registry reduce operational overhead
- **Cloud-agnostic**: Dapr abstraction allows migration to other cloud providers with minimal code changes
- **Production-ready patterns**: Distributed tracing, correlation IDs, health checks, observability
- **Simple where possible**: In-app notifications, APScheduler, Redis (no complex external integrations)

**Next Steps**: Proceed to data-model.md, contracts/, and quickstart.md generation, then `/sp.tasks` for implementation task breakdown.
