# Implementation Plan: Phase V - Cloud Deployment with Event-Driven Architecture

**Branch**: `005-phase5-cloud-event-driven` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-phase5-cloud-event-driven/spec.md`
**Cloud Provider**: Oracle Cloud Infrastructure (OCI) - Oracle Kubernetes Engine (OKE)

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Phase V transforms the todo application from a local Kubernetes deployment (Phase IV) into a production-ready, cloud-native system deployed on Oracle Cloud Infrastructure (OKE). The implementation introduces event-driven architecture with Kafka for asynchronous processing, three specialized microservices (Notification, Recurring Tasks, Audit), Dapr for distributed runtime capabilities, advanced task management features (priorities, tags, search, filters, recurring tasks, reminders), and CI/CD automation via GitHub Actions. All existing Phase I-IV features are preserved while adding enterprise-grade capabilities for scalability, reliability, and observability.

**Primary Requirement**: Deploy to OKE with event-driven microservices architecture using Kafka and Dapr

**Technical Approach**:
1. Extend Phase IV Helm charts for OKE deployment with Dapr sidecars
2. Implement event publishing system using Dapr pub/sub with Kafka broker
3. Create three new microservices (Notification, Recurring Tasks, Audit) as separate Python FastAPI apps
4. Extend Task model and API endpoints with advanced features (priority, tags, due_date, recurrence_pattern, reminders)
5. Implement GitHub Actions CI/CD pipeline for automated build, test, and deployment to OKE
6. Configure cloud-native monitoring using OCI Monitoring and Logging services
7. Use Redpanda Cloud for managed Kafka to simplify operations

## Technical Context

**Language/Version**:
- **Backend**: Python 3.13+ (existing FastAPI app + 3 new microservices)
- **Frontend**: TypeScript 5.x, Next.js 15 (existing, extended with advanced task UI)

**Primary Dependencies**:
- **Existing**: FastAPI, SQLModel, Neon PostgreSQL, OpenAI Agents SDK, MCP SDK, Next.js, React 19
- **New for Phase V**:
  - **Dapr SDK**: `dapr-ext-grpc` for Python (pub/sub, state management, service invocation, jobs)
  - **Kafka Client**: `aiokafka` for Python (event publishing/consuming)
  - **Scheduling**: `APScheduler` for recurring tasks cron jobs
  - **Date/Time**: `python-dateutil` for timezone handling and recurrence logic
  - **Helm**: Helm 3.x for Kubernetes package management (extended from Phase IV)
  - **OCI SDK**: Oracle Cloud SDK for infrastructure automation (optional)

**Storage**:
- **Primary Database**: Neon Serverless PostgreSQL (existing, extended schema)
- **Event Store**: Kafka topics via Redpanda Cloud (task-events, reminders, task-updates)
- **State Store**: Dapr state management backed by Redis (for conversation state) or PostgreSQL
- **Secrets**: Kubernetes Secrets accessed via Dapr secrets API

**Testing**:
- **Backend**: pytest (existing, extended for new microservices and features)
- **Frontend**: Jest/Vitest (existing, extended for advanced task UI)
- **Contract Testing**: Pact or OpenAPI validation for inter-service contracts
- **E2E Testing**: Playwright for critical user flows in cloud environment
- **Load Testing**: k6 or Locust for performance validation (500 concurrent users target)

**Target Platform**:
- **Cloud**: Oracle Cloud Infrastructure (OCI)
- **Kubernetes**: Oracle Kubernetes Engine (OKE) - Always Free Tier (2 nodes, 1 OCPU each)
- **Container Registry**: OCI Container Registry (OCIR) or GitHub Container Registry
- **DNS/Ingress**: OCI Load Balancer + NGINX Ingress Controller with cert-manager (Let's Encrypt)

**Project Type**: Web application (monorepo with backend services + frontend)

**Performance Goals**:
- **API Latency**: p95 < 500ms for task CRUD operations
- **Search/Filter**: Results in < 1 second for up to 10,000 tasks per user
- **Event Processing**: Kafka events processed within 5 seconds under normal load
- **Concurrent Users**: Support 500 concurrent users without degradation
- **Event Throughput**: Handle 1000 events/second across all topics

**Constraints**:
- **Uptime**: 99.9% availability target (43 minutes downtime per month max)
- **Cost**: Stay within OCI Always Free Tier limits where possible
- **Zero Downtime**: Rolling deployments with no user-facing errors
- **Event Delivery**: At-least-once delivery guarantees for Kafka events
- **Database Connections**: Reuse Neon PostgreSQL, no migration to OCI DB

**Scale/Scope**:
- **Users**: 100-500 concurrent users (hackathon demo scale)
- **Tasks**: 10,000 tasks per user (search/filter performance target)
- **Microservices**: 3 new services + existing backend/frontend (5 total deployments)
- **Kafka Topics**: 3 topics with 3 partitions each, 30-day retention
- **Infrastructure**: 2-node OKE cluster (free tier), 3-5 pods per service

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅
- [x] Specification created and validated (`specs/005-phase5-cloud-event-driven/spec.md`)
- [x] Implementation plan being generated via `/sp.plan` command
- [x] Tasks will be generated via `/sp.tasks` command
- [x] PHR records created for all stages
- **Status**: PASS

### Principle II: No Manual Coding ✅
- [x] All implementation will be generated by Claude Code
- [x] Configuration files (Helm values, GitHub Actions, Dapr components) will be specified then generated
- [x] Manual edits limited to environment-specific values (OCI credentials, endpoints)
- **Status**: PASS

### Principle III: Test-First Development ✅
- [x] Tests required for: API contract changes (advanced task endpoints), database schema migrations, inter-service communication (Kafka events), Dapr state management
- [x] Integration tests for microservices event processing
- [x] E2E tests for critical user flows (create recurring task, receive reminder)
- **Status**: PASS

### Principle IV: AI-Native Architecture ✅
- [x] Existing OpenAI ChatKit UI preserved
- [x] Existing OpenAI Agents SDK and MCP tools preserved
- [x] Conversation state migrated to Dapr state management (stateless design)
- [x] All CRUD tools continue to work via natural language
- **Status**: PASS

### Principle V: Cloud-Native Deployment ✅
- [x] Oracle Kubernetes Engine (OKE) selected as cloud provider
- [x] Dapr integration for pub/sub, state, service invocation, jobs, secrets
- [x] Kafka (Redpanda Cloud) for event streaming
- [x] Helm charts for deployment (extended from Phase IV)
- [x] AIOps tools: kubectl-ai for cluster operations
- **Status**: PASS

### Principle VI: Progressive Enhancement ✅
- [x] All Phase I-IV features preserved and functional
- [x] Intermediate features added: Priorities, Tags, Search, Filter, Sort
- [x] Advanced features added: Recurring Tasks, Due Dates, Reminders
- [x] Event-driven architecture enables future extensibility
- **Status**: PASS

### Principle VII: Security-First ✅
- [x] Existing JWT authentication continues (Better Auth)
- [x] User isolation via user_id filtering in all queries
- [x] Secrets management via Dapr secrets store (Kubernetes Secrets)
- [x] Input validation for new fields (priority, tags, due_date, recurrence_pattern)
- [x] Parameterized queries via SQLModel (prevents SQL injection)
- **Status**: PASS

### Principle VIII: Observability ✅
- [x] Structured JSON logging with correlation IDs across all services
- [x] Prometheus metrics exposed from all services
- [x] Distributed tracing via Dapr observability (Zipkin/Jaeger compatible)
- [x] OCI Monitoring and Logging for cloud-native visibility
- [x] Health checks (/health, /ready) for all services
- **Status**: PASS

### Principle IX: Simplicity & YAGNI ✅
- [x] Start with simplest viable microservices (3 services, single responsibility each)
- [x] Use managed Kafka (Redpanda Cloud) to avoid operational complexity
- [x] Leverage Dapr to abstract infrastructure concerns
- [x] No over-engineering: daily/weekly/monthly recurrence only (not complex cron patterns)
- **Status**: PASS

**Overall Constitution Check**: ✅ **PASS** - All 9 principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/005-phase5-cloud-event-driven/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── task-api.openapi.yaml
│   ├── notification-service.openapi.yaml
│   ├── recurring-tasks-service.openapi.yaml
│   ├── audit-service.openapi.yaml
│   └── kafka-events.schema.json
├── checklists/
│   └── requirements.md  # Specification quality checklist (existing)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
hackathon-2-todo/
├── backend/                          # Main FastAPI app (existing, extended)
│   ├── src/
│   │   ├── main.py                  # API entry point (extended with advanced endpoints)
│   │   ├── api/
│   │   │   ├── tasks.py             # Extended: priority, tags, search, filter, sort
│   │   │   └── chat.py              # Existing MCP chat integration
│   │   ├── core/
│   │   │   ├── database.py          # Existing Neon PostgreSQL connection
│   │   │   ├── dapr_client.py       # NEW: Dapr client for pub/sub, state, invocation
│   │   │   └── kafka_producer.py    # NEW: Kafka event publisher
│   │   ├── models/
│   │   │   ├── task.py              # Extended: priority, tags, due_date, recurrence_pattern
│   │   │   ├── task_event.py        # NEW: Event model
│   │   │   ├── notification.py      # NEW: Notification model
│   │   │   └── audit_log.py         # NEW: Audit log model
│   │   ├── services/
│   │   │   ├── task_service.py      # Extended: search, filter, sort logic
│   │   │   └── event_publisher.py   # NEW: Event publishing service
│   │   └── chatkit/                 # Existing MCP tools (preserved)
│   └── tests/
│       ├── unit/
│       ├── integration/
│       │   └── test_task_events.py  # NEW: Event publishing tests
│       └── contract/
│           └── test_task_api.py     # NEW: Contract tests
│
├── services/                         # NEW: Microservices directory
│   ├── notification-service/        # NEW: Notification microservice
│   │   ├── src/
│   │   │   ├── main.py              # FastAPI app
│   │   │   ├── consumers/
│   │   │   │   └── task_event_consumer.py  # Kafka consumer
│   │   │   ├── services/
│   │   │   │   └── notification_service.py  # Notification logic
│   │   │   └── models/
│   │   │       └── notification.py
│   │   ├── pyproject.toml
│   │   └── tests/
│   │
│   ├── recurring-tasks-service/     # NEW: Recurring tasks microservice
│   │   ├── src/
│   │   │   ├── main.py              # FastAPI app
│   │   │   ├── scheduler/
│   │   │   │   └── task_scheduler.py  # APScheduler cron jobs
│   │   │   ├── services/
│   │   │   │   └── recurrence_service.py  # Recurrence logic
│   │   │   └── models/
│   │   │       └── recurring_schedule.py
│   │   ├── pyproject.toml
│   │   └── tests/
│   │
│   └── audit-service/               # NEW: Audit microservice
│       ├── src/
│       │   ├── main.py              # FastAPI app
│       │   ├── consumers/
│       │   │   └── audit_event_consumer.py  # Kafka consumer
│       │   ├── services/
│       │   │   └── audit_service.py  # Audit logging
│       │   └── models/
│       │       └── audit_log.py
│       ├── pyproject.toml
│       └── tests/
│
├── frontend/                         # Next.js app (existing, extended)
│   ├── src/
│   │   ├── app/
│   │   │   └── tasks/
│   │   │       └── page.tsx         # Extended: priority, tags, search UI
│   │   ├── components/
│   │   │   ├── TaskList.tsx         # Extended: filter, sort controls
│   │   │   ├── TaskForm.tsx         # Extended: priority, tags, due_date inputs
│   │   │   ├── RecurringTaskForm.tsx  # NEW: Recurrence pattern selector
│   │   │   └── NotificationBadge.tsx  # NEW: Notification display
│   │   └── lib/
│   │       └── api.ts               # Extended: new API endpoints
│   └── tests/
│
├── infra/                           # Infrastructure (existing, extended)
│   ├── docker/
│   │   ├── backend.Dockerfile       # Existing
│   │   ├── frontend.Dockerfile      # Existing
│   │   ├── notification-service.Dockerfile  # NEW
│   │   ├── recurring-tasks-service.Dockerfile  # NEW
│   │   └── audit-service.Dockerfile  # NEW
│   │
│   ├── helm/todo/                   # Helm chart (existing, extended)
│   │   ├── Chart.yaml               # Updated version
│   │   ├── values.yaml              # Extended: new services, Dapr config
│   │   ├── values.oke.yaml          # NEW: OKE-specific values
│   │   ├── templates/
│   │   │   ├── backend-deployment.yaml       # Extended: Dapr annotations
│   │   │   ├── frontend-deployment.yaml      # Existing
│   │   │   ├── notification-deployment.yaml  # NEW
│   │   │   ├── recurring-tasks-deployment.yaml  # NEW
│   │   │   ├── audit-deployment.yaml        # NEW
│   │   │   ├── dapr-components/             # NEW: Dapr configurations
│   │   │   │   ├── pubsub.yaml              # Kafka pub/sub component
│   │   │   │   ├── statestore.yaml          # Redis/PostgreSQL state store
│   │   │   │   └── secretstore.yaml         # Kubernetes secrets
│   │   │   ├── ingress.yaml                 # Extended: new routes
│   │   │   └── configmap.yaml               # Extended: Kafka endpoints
│   │   └── secrets.example.yaml     # Extended: OCI/Kafka credentials
│   │
│   ├── dapr/                        # NEW: Dapr configuration
│   │   ├── components/
│   │   │   ├── kafka-pubsub.yaml
│   │   │   ├── redis-statestore.yaml
│   │   │   └── kubernetes-secrets.yaml
│   │   └── config/
│   │       └── dapr-config.yaml     # Tracing, metrics configuration
│   │
│   └── kubernetes/                  # NEW: Additional K8s manifests
│       ├── namespace.yaml           # todo namespace
│       ├── redis-deployment.yaml    # Redis for Dapr state store
│       └── monitoring/
│           ├── prometheus-config.yaml
│           └── grafana-dashboard.json
│
├── .github/workflows/               # NEW: CI/CD pipelines
│   ├── build-and-test.yml          # CI: Build, test, lint
│   ├── deploy-oke.yml              # CD: Deploy to OKE
│   ├── build-images.yml            # Build and push Docker images
│   └── rollback.yml                # Rollback workflow
│
├── scripts/                         # NEW: Automation scripts
│   ├── setup-oke.sh                # OKE cluster setup
│   ├── install-dapr.sh             # Dapr installation
│   ├── setup-kafka.sh              # Redpanda Cloud setup
│   └── migrate-db.sh               # Database migration runner
│
├── specs/                           # SDD specifications
│   ├── 001-phase1-console/
│   ├── 002-phase2-web/
│   ├── 003-phase3-ai-chatbot/
│   ├── 004-phase4-kubernetes/
│   └── 005-phase5-cloud-event-driven/  # This feature
│
├── history/prompts/                 # PHR records
│   └── 005-phase5-cloud-event-driven/
│
├── CLAUDE.md                        # Root agent instructions (updated)
└── README.md                        # Updated with Phase V quickstart
```

**Structure Decision**: Extended web application monorepo structure from Phase IV. Added `services/` directory for three new microservices (Notification, Recurring Tasks, Audit), each as standalone FastAPI apps with their own pyproject.toml and tests. Existing `backend/` and `frontend/` directories extended with new features (advanced task management, event publishing, Dapr integration). New `infra/dapr/` and `.github/workflows/` directories for cloud-native infrastructure and CI/CD automation. This structure maintains Phase IV compatibility while cleanly separating event-driven microservices.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected. All complexity is justified by Phase V requirements:

- **Three new microservices**: Required by constitution for event-driven architecture (Notification, Recurring Tasks, Audit)
- **Dapr integration**: Required by constitution Principle V for distributed runtime capabilities
- **Kafka event streaming**: Required by constitution for Phase V event-driven architecture
- **CI/CD automation**: Required by specification for production-grade deployment
- **Advanced task features**: Required by constitution Progressive Enhancement (Intermediate and Advanced features)

No additional complexity beyond requirements. All choices align with YAGNI principle.

---

## Phase 0: Research & Technology Decisions

**Status**: Completed during plan generation
**Output**: research.md (to be generated)

### Research Tasks Identified

Based on Technical Context, the following research areas require investigation:

1. **Oracle Kubernetes Engine (OKE) Configuration**
   - Decision: Use OKE Always Free Tier (2 nodes, 1 OCPU each, 6GB RAM per node)
   - Rationale: Cost-effective for hackathon demo, sufficient for 500 concurrent users target
   - Alternatives considered: DigitalOcean DOKS ($12/month), Azure AKS ($70/month), GCP GKE ($75/month)

2. **Kafka Provider Selection**
   - Decision: Redpanda Cloud (Serverless tier, $0 for <1GB/month)
   - Rationale: Managed Kafka reduces operational complexity, Kafka-compatible API, generous free tier
   - Alternatives considered: Strimzi on OKE (self-hosted, complex), Confluent Cloud ($100+/month)

3. **Dapr State Store Backend**
   - Decision: Redis deployed on OKE (single pod for demo)
   - Rationale: Fast in-memory state store, widely supported by Dapr, simple deployment
   - Alternatives considered: PostgreSQL (slower, more durable), Cosmos DB (expensive)

4. **CI/CD Pipeline Architecture**
   - Decision: GitHub Actions with OCI credentials as secrets
   - Rationale: Native GitHub integration, free for public repos, mature ecosystem
   - Alternatives considered: GitLab CI (requires migration), Jenkins (operational overhead)

5. **Container Registry**
   - Decision: GitHub Container Registry (ghcr.io)
   - Rationale: Free, integrated with GitHub Actions, no OCI setup required
   - Alternatives considered: OCI Registry (OCIR, requires tenancy setup), Docker Hub (rate limits)

6. **Ingress and SSL Certificates**
   - Decision: NGINX Ingress Controller + cert-manager (Let's Encrypt)
   - Rationale: Battle-tested, free SSL certificates, widely documented
   - Alternatives considered: OCI Load Balancer (paid), Traefik (less familiar)

7. **Recurring Task Scheduling Strategy**
   - Decision: APScheduler with in-memory job store
   - Rationale: Lightweight, Python-native, sufficient for demo scale
   - Alternatives considered: Dapr Jobs API (alpha status), Celery (heavyweight)

8. **Notification Delivery Mechanism**
   - Decision: In-app notifications stored in database
   - Rationale: Simplest approach, no external dependencies (email/SMS)
   - Alternatives considered: WebSocket push (complex), Email (requires SMTP setup)

### Technologies Requiring Research Documentation

The following will be documented in `research.md`:

- **OKE Cluster Setup**: Terraform or OCI CLI steps, node pool configuration
- **Dapr Installation on OKE**: Helm chart deployment, sidecar injection
- **Redpanda Cloud Setup**: Account creation, topic configuration, connection strings
- **GitHub Actions OCI Authentication**: Service account creation, kubeconfig setup
- **Database Schema Migration**: Alembic migration for new fields (priority, tags, due_date, etc.)
- **Dapr Pub/Sub with Kafka**: Component configuration, topic subscription patterns
- **Inter-Service Communication Patterns**: Dapr service invocation vs direct HTTP
- **Distributed Tracing Setup**: Zipkin/Jaeger integration with Dapr

---

## Phase 1: Design Artifacts

**Status**: To be generated
**Output**: data-model.md, contracts/, quickstart.md

### Data Model Extensions (data-model.md)

**New Entities**:
1. **Task** (extended):
   - New fields: `priority` (enum: High/Medium/Low), `tags` (array), `due_date` (timestamp), `recurrence_pattern` (enum: none/daily/weekly/monthly), `reminder_lead_time` (integer minutes)
   - Relationships: One-to-many with TaskEvent, one-to-one with RecurringTaskSchedule (if recurring)

2. **TaskEvent** (new):
   - Fields: `event_id`, `event_type`, `task_id`, `user_id`, `timestamp`, `payload` (JSON)
   - Purpose: Immutable event log published to Kafka

3. **RecurringTaskSchedule** (new):
   - Fields: `schedule_id`, `parent_task_id`, `recurrence_pattern`, `next_execution_time`, `is_active`
   - Purpose: Tracks recurring task generation state

4. **Notification** (new):
   - Fields: `notification_id`, `user_id`, `task_id`, `notification_type`, `message`, `sent_at`, `delivery_status`
   - Purpose: In-app notifications for reminders and task events

5. **AuditLog** (new):
   - Fields: `audit_id`, `timestamp`, `user_id`, `action_type`, `resource_type`, `resource_id`, `event_data` (JSON), `correlation_id`
   - Purpose: Immutable audit trail for compliance

### API Contracts (contracts/)

**Extended Task API** (`contracts/task-api.openapi.yaml`):
- `GET /api/{user_id}/tasks?priority=High&tags=work&status=pending&sort=due_date`
- `POST /api/{user_id}/tasks` (extended body: priority, tags, due_date, recurrence_pattern, reminder_lead_time)
- `PATCH /api/{user_id}/tasks/{task_id}` (partial update)
- `GET /api/{user_id}/tasks/search?q=keyword`

**Notification Service** (`contracts/notification-service.openapi.yaml`):
- `GET /api/{user_id}/notifications?unread_only=true`
- `POST /internal/notifications` (Kafka consumer creates notifications)
- `PATCH /api/{user_id}/notifications/{notification_id}/mark_read`

**Recurring Tasks Service** (`contracts/recurring-tasks-service.openapi.yaml`):
- `POST /internal/schedules` (create recurring schedule)
- `GET /internal/schedules/due` (fetch schedules needing execution)

**Audit Service** (`contracts/audit-service.openapi.yaml`):
- `GET /api/{user_id}/audit_logs?resource_id={task_id}`
- `POST /internal/audit_logs` (Kafka consumer creates audit logs)

**Kafka Event Schemas** (`contracts/kafka-events.schema.json`):
- `TaskCreatedEvent`, `TaskUpdatedEvent`, `TaskCompletedEvent`, `TaskDeletedEvent`
- `ReminderScheduledEvent`, `ReminderTriggeredEvent`

### Quickstart Guide (quickstart.md)

**OKE Deployment Steps**:
1. Prerequisites: OCI account, kubectl, Helm, Dapr CLI, GitHub account
2. OKE cluster creation (via OCI Console or Terraform)
3. Redpanda Cloud setup and topic creation
4. GitHub repository secrets configuration (OCI credentials, Kafka endpoints, database URL)
5. Dapr installation on OKE cluster
6. Database migration (Alembic upgrade)
7. Helm deployment: `helm install todo ./infra/helm/todo -f ./infra/helm/todo/values.oke.yaml`
8. DNS configuration (OCI Load Balancer IP → domain)
9. Verification: Access application, trigger events, observe microservices logs

---

## Phase 2: Implementation Tasks

**Status**: NOT STARTED (awaiting `/sp.tasks` command)
**Output**: tasks.md (generated by `/sp.tasks`)

This section is intentionally blank. The `/sp.tasks` command will generate `tasks.md` based on this plan and the specification, breaking down implementation into testable, dependency-ordered tasks.

---

## Architectural Decisions

### AD-1: Event-Driven Architecture with Kafka

**Context**: Phase V requires asynchronous processing for notifications, recurring tasks, and audit logging.

**Decision**: Use Kafka (via Redpanda Cloud) for event streaming with Dapr pub/sub abstraction.

**Rationale**:
- Decouples microservices (Notification, Recurring Tasks, Audit can scale independently)
- At-least-once delivery guarantees prevent event loss
- Dapr pub/sub allows swapping Kafka for other brokers without code changes
- Redpanda Cloud eliminates operational overhead (managed topics, scaling, durability)

**Consequences**:
- Eventual consistency model (events processed asynchronously)
- Requires idempotency in consumers (duplicate event handling)
- Adds external dependency (Redpanda Cloud availability)
- Monitoring complexity (need to track event lag, consumer health)

**Alternatives Rejected**:
- Direct HTTP calls between services: Tight coupling, synchronous failures cascade
- Database polling: Inefficient, high latency, scales poorly
- RabbitMQ: Less suited for event streaming, lower throughput

---

### AD-2: Dapr for Distributed Runtime

**Context**: Phase V constitution requires Dapr integration for pub/sub, state management, service invocation, jobs, and secrets.

**Decision**: Deploy Dapr sidecars alongside all pods, use Dapr APIs for cross-cutting concerns.

**Rationale**:
- Abstracts infrastructure (can swap Redis state store for PostgreSQL without code changes)
- Built-in observability (distributed tracing, metrics)
- Service invocation with retries, circuit breaking, mTLS
- Secrets management via Kubernetes Secrets (no hardcoded credentials)
- Cloud-agnostic (same code runs on OKE, AKS, GKE, local Minikube)

**Consequences**:
- Additional resource overhead (Dapr sidecar per pod)
- Learning curve for Dapr component configuration
- Debugging complexity (two processes per pod)
- Alpha/beta APIs (Jobs API may change)

**Alternatives Rejected**:
- Native Kubernetes features only: Requires custom code for state, pub/sub, service mesh
- Istio service mesh: Heavyweight, operational complexity for hackathon scale
- Custom SDK: Reinvents the wheel, lacks community support

---

### AD-3: Microservices for Event Consumers

**Context**: Phase V requires Notification, Recurring Tasks, and Audit services consuming Kafka events.

**Decision**: Implement as separate Python FastAPI applications deployed as independent Kubernetes pods.

**Rationale**:
- Single Responsibility Principle (each service does one thing well)
- Independent scaling (Notification service can scale separately from Audit)
- Fault isolation (Audit service failure doesn't affect Notifications)
- Technology flexibility (future services can use different languages)

**Consequences**:
- Increased deployment complexity (5 services vs 2 in Phase IV)
- More Docker images to build and manage
- Inter-service communication requires Dapr/HTTP (network calls)
- Debugging distributed flows requires correlation IDs and tracing

**Alternatives Rejected**:
- Monolith with background workers: Tight coupling, difficult to scale consumers independently
- Serverless functions (OCI Functions): Cold start latency, harder to test locally
- Single consumer service: Violates SRP, harder to reason about failures

---

### AD-4: Oracle Cloud Infrastructure (OKE) as Cloud Provider

**Context**: User specified "we will use oracle cloud" for Phase V deployment.

**Decision**: Deploy to Oracle Kubernetes Engine (OKE) using Always Free Tier.

**Rationale**:
- **Cost**: Always Free Tier provides 2 nodes (1 OCPU each, 6GB RAM) indefinitely
- **Sufficient for demo**: Handles 500 concurrent users target with proper resource limits
- **Full Kubernetes compatibility**: Standard K8s APIs, works with Helm, Dapr, kubectl
- **Learning value**: Experience with OCI platform (different from AWS/Azure/GCP)

**Consequences**:
- OCI-specific setup (tenancy, compartments, VCN configuration)
- Less community documentation compared to GKE/EKS/AKS
- Free tier limits (2 nodes, limited bandwidth, no auto-scaling beyond 2 nodes)
- Potential migration effort if scaling beyond free tier

**Alternatives Rejected**:
- DigitalOcean DOKS: Better documentation, but $12/month minimum cost
- Azure AKS: Familiar to many, but expensive for 2-node cluster
- GCP GKE: Excellent free tier, but user specified Oracle Cloud

---

### AD-5: GitHub Actions for CI/CD

**Context**: Phase V requires automated CI/CD pipeline for cloud deployment.

**Decision**: Use GitHub Actions workflows for build, test, and deployment to OKE.

**Rationale**:
- Native GitHub integration (already using GitHub for source control)
- Free for public repositories (unlimited minutes)
- Marketplace actions for Docker build, Kubernetes deploy, Helm
- Secrets management built-in (OCI credentials, Kafka endpoints)
- Workflow as code (YAML in `.github/workflows/`)

**Consequences**:
- Vendor lock-in to GitHub (migration to GitLab CI requires rewrite)
- Public repos expose workflow logic (not secrets, but structure)
- Debugging workflows requires push commits (no local execution)

**Alternatives Rejected**:
- GitLab CI: Would require migrating to GitLab, less familiar
- Jenkins: Requires hosting, operational overhead, complex setup
- OCI DevOps: Less mature, limited documentation

---

### AD-6: In-App Notifications (No Email/SMS)

**Context**: Phase V requires reminder notifications for tasks.

**Decision**: Implement in-app notifications stored in database, displayed in UI badge.

**Rationale**:
- Simplest approach (no external dependencies like SendGrid, Twilio)
- Sufficient for hackathon demo (judges can see notifications in UI)
- No privacy concerns (email/SMS requires user consent, phone numbers)
- Aligns with YAGNI principle (email/SMS out of scope per spec)

**Consequences**:
- Users must be logged in to see notifications (no offline notifications)
- Limited reach (no notifications if user doesn't open app)
- Future enhancement needed for production (email/push notifications)

**Alternatives Rejected**:
- Email notifications: Requires SMTP setup, deliverability issues, user email verification
- SMS notifications: Expensive (Twilio costs), requires phone number collection
- WebSocket push notifications: Complex, requires persistent connections

---

### AD-7: APScheduler for Recurring Tasks

**Context**: Recurring Tasks Service needs to execute daily/weekly/monthly task generation.

**Decision**: Use APScheduler library with cron-style job scheduling.

**Rationale**:
- Lightweight Python library (no external dependencies)
- Cron expression support for daily/weekly/monthly patterns
- In-memory job store sufficient for demo scale (persistent store optional)
- Well-documented, mature library

**Consequences**:
- Jobs lost on pod restart (need persistent job store for production)
- Single instance only (no distributed job coordination)
- Manual monitoring of job execution (need to add observability)

**Alternatives Rejected**:
- Dapr Jobs API: Alpha status, limited documentation, breaking changes likely
- Celery Beat: Heavyweight (requires Redis/RabbitMQ), overkill for simple scheduling
- Kubernetes CronJobs: Coarse-grained (creates pods), not suitable for per-task scheduling

---

## Risk Mitigation

### Risk 1: OCI Always Free Tier Limitations

**Risk**: Free tier provides only 2 nodes (1 OCPU each), may be insufficient under load.

**Mitigation**:
- Set aggressive resource limits (CPU/memory) per pod to maximize density
- Implement horizontal pod autoscaling (HPA) to scale replicas within node capacity
- Load test early to validate 500 concurrent users target
- Fallback: Upgrade to paid OKE cluster if free tier insufficient (document cost in spec)

### Risk 2: Kafka Event Ordering and Idempotency

**Risk**: Kafka guarantees order within partition, but consumers may process events out of order or duplicates.

**Mitigation**:
- Partition Kafka topics by `task_id` (all events for same task go to same partition)
- Implement idempotency tokens in event payloads (`event_id` as unique key)
- Consumers check if event already processed before taking action (database query)
- Log duplicate events for monitoring

### Risk 3: Dapr Learning Curve

**Risk**: Team unfamiliar with Dapr configuration, component manifests, sidecar injection.

**Mitigation**:
- Start with Dapr quickstart tutorials before implementation
- Use official Dapr Helm charts (don't write custom manifests)
- Leverage Dapr documentation and community support
- Prototype locally with `dapr run` before deploying to OKE

### Risk 4: CI/CD Pipeline Failures

**Risk**: GitHub Actions workflow may fail due to OCI authentication, Helm errors, or environment issues.

**Mitigation**:
- Test pipeline in separate staging environment before production
- Implement comprehensive error handling and rollback workflows
- Use Helm test hooks to validate deployment health
- Manual deployment procedure documented as fallback

### Risk 5: Database Schema Migration Risks

**Risk**: Alembic migration may fail or cause downtime during deployment.

**Mitigation**:
- Test migrations on staging database first
- Use backward-compatible migrations (add columns, don't drop)
- Implement blue-green deployment (old version runs during migration)
- Database backup before migration (Neon automatic backups)

### Risk 6: Monitoring Blind Spots

**Risk**: Distributed system with 5 services may have undetected failures.

**Mitigation**:
- Implement health checks (/health, /ready) on all services
- Use correlation IDs for request tracing across services
- Configure Prometheus alerts for high error rates, latency spikes
- Dapr observability integration (Zipkin tracing)
- OCI Monitoring dashboards for cluster health

---

## Open Questions

1. **OCI Tenancy Setup**: Is OCI account already created, or does this need to be done? (Assume yes for planning)
2. **Domain Name**: What domain will be used for the production URL? (Assume `todo.example.com` or OCI-provided IP)
3. **Neon PostgreSQL Compatibility**: Will Neon work from OCI region, or are there network latency concerns? (Assume global accessibility)
4. **Redpanda Cloud Region**: Which region should Redpanda cluster be created in (match OKE region)? (Assume US-West or closest to OKE)
5. **SSL Certificate Email**: What email address for Let's Encrypt certificate notifications? (Assume admin email)

**Resolution**: These questions will be answered during implementation. Reasonable defaults assumed for planning purposes per constitution assumptions section.

---

## Next Steps

1. **Generate research.md**: Document OKE setup, Dapr installation, Redpanda configuration, CI/CD authentication
2. **Generate data-model.md**: Define extended Task schema, new entities (TaskEvent, RecurringTaskSchedule, Notification, AuditLog)
3. **Generate API contracts**: OpenAPI specs for extended Task API, Notification/Recurring/Audit services, Kafka event schemas
4. **Generate quickstart.md**: Step-by-step OKE deployment guide for Phase V
5. **Update agent context**: Add new technologies (Dapr, Kafka, OKE, APScheduler) to CLAUDE.md
6. **Run `/sp.tasks`**: Generate tasks.md with dependency-ordered, testable implementation tasks
7. **Begin implementation**: Follow tasks.md using `/sp.implement` command
