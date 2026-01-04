# Implementation Tasks: Phase V - Cloud Deployment with Event-Driven Architecture

**Feature**: Phase V
**Branch**: `005-phase5-cloud-event-driven`
**Created**: 2025-12-30

## Overview

This document provides an actionable task breakdown for implementing Phase V, organized by user story to enable independent development and testing.

**Total User Stories**: 5 (US1: P1, US2: P2, US3: P3, US4: P2, US5: P3)

**Implementation Strategy**: MVP-first (User Story 1), then incremental delivery by priority.

---

## Task Summary

| Phase | User Story | Task Count | Parallelizable | Status |
|-------|-----------|------------|----------------|--------|
| Phase 1 | Setup | 12 | 8 | In Progress |
| Phase 2 | Foundational | 8 | 4 | Complete |
| Phase 3 | US1: Cloud Deployment (P1) | 15 | 6 | In Progress |
| Phase 4 | US2: Advanced Task Features (P2) | 18 | 10 | In Progress |
| Phase 5 | US3: Event-Driven Architecture (P3) | 22 | 12 | In Progress |
| Phase 6 | US4: CI/CD Automation (P2) | 10 | 5 | In Progress |
| Phase 7 | US5: Dapr Integration (P3) | 14 | 7 | Not Started |
| Phase 8 | Polish & Cross-Cutting | 8 | 4 | Not Started |
| **TOTAL** | | **107** | **56** | |

---

## Dependencies Between User Stories

```
US1 (Cloud Deployment) ← BLOCKS ALL OTHER STORIES
    ├── US2 (Advanced Features) - Independent after US1
    ├── US3 (Event-Driven) - Depends on US2 (needs extended Task model)
    ├── US4 (CI/CD) - Independent after US1
    └── US5 (Dapr) - Depends on US3 (needs event infrastructure)
```

**MVP Scope**: Complete Phase 1-3 (US1) for minimal cloud deployment
**Full Phase V**: Complete all phases

---

## Phase 1: Setup & Infrastructure (No Story Label)

**Goal**: Initialize Phase V infrastructure components (OKE cluster, Dapr, Kafka, Redis) and prepare project structure for microservices.

**Independent Test**: OKE cluster is running, kubectl can access it, Dapr is installed, Kafka topics exist.

### Tasks

- [ ] T001 Create OKE cluster on Oracle Cloud (2 nodes, 1 OCPU each, Always Free Tier) - Follow `quickstart.md` steps 1-2
- [ ] T002 Configure kubectl access to OKE cluster - Generate kubeconfig and test connection
- [ ] T003 Create Redpanda Cloud account and serverless cluster in us-west-2 region
- [ ] T004 Create Kafka topics: task-events, reminders, task-updates (3 partitions, 30-day retention)
- [ ] T005 Create Redpanda service account with permissions on all topics, save credentials
- [ ] T006 [P] Install Dapr on OKE cluster via Helm - `helm install dapr dapr/dapr --namespace dapr-system`
- [ ] T007 [P] Install NGINX Ingress Controller via Helm in ingress-nginx namespace
- [ ] T008 [P] Install cert-manager for SSL certificates via Helm in cert-manager namespace
- [ ] T009 [P] Install Redis on OKE via Bitnami Helm chart in todo namespace (no auth, no persistence)
- [ ] T010 [P] Create ClusterIssuer for Let's Encrypt in infra/kubernetes/cert-manager-issuer.yaml
- [ ] T011 [P] Create GitHub repository secrets: OCI credentials, Kafka endpoints, DATABASE_URL
- [X] T012 [P] Create services/ directory structure for 3 microservices (notification-service, recurring-tasks-service, audit-service)

---

## Phase 2: Foundational Components (No Story Label)

**Goal**: Extend database schema and create shared components needed by all user stories.

**Independent Test**: Database migrations run successfully, all new tables exist, base models compile.

### Tasks

- [X] T013 Create Alembic migration for Phase V schema in backend/alembic/versions/ - Add columns to tasks table (priority, tags, due_date, recurrence_pattern, reminder_lead_time)
- [X] T014 [P] Create TaskEvent model in backend/src/models/task_event.py per data-model.md
- [X] T015 [P] Create RecurringTaskSchedule model in backend/src/models/recurring_task_schedule.py
- [X] T016 [P] Create Notification model in backend/src/models/notification.py
- [X] T017 [P] Create AuditLog model in backend/src/models/audit_log.py
- [X] T018 Extend Task model in backend/src/models/task.py with new fields (priority enum, tags array, due_date, recurrence_pattern enum, reminder_lead_time)
- [ ] T019 Run database migration against Neon PostgreSQL - `uv run alembic upgrade head`
- [X] T020 Create Dapr components directory infra/dapr/components/ with kafka-pubsub.yaml, redis-statestore.yaml, kubernetes-secrets.yaml per research.md

---

## Phase 3: User Story 1 - Cloud Deployment (Priority: P1)

**Story Goal**: Deploy Phase I-IV application to Oracle Kubernetes Engine with Helm, accessible via public HTTPS URL.

**Independent Test**:

- Application is accessible at https://<loadbalancer-ip>.nip.io
- All Phase I-IV features work (create task, list tasks, chat with AI, mark complete)
- Pods are running with health checks passing
- SSL certificate is valid (Let's Encrypt)

### Tasks

#### Infrastructure as Code

- [X] T021 [P] [US1] Extend Helm chart Chart.yaml in infra/helm/todo/ - Bump version to 2.0.0 for Phase V
- [X] T022 [P] [US1] Create values.oke.yaml in infra/helm/todo/ with OKE-specific settings (domain, resource limits, replicas)
- [X] T023 [P] [US1] Update backend-deployment.yaml template to add Dapr annotations (dapr.io/enabled, app-id, app-port)
- [X] T024 [P] [US1] Update ingress.yaml template to support nip.io domain and cert-manager annotations
- [X] T025 [P] [US1] Create ConfigMap template for Kafka bootstrap servers in infra/helm/todo/templates/configmap.yaml
- [X] T026 [P] [US1] Create Secret template for Kafka credentials in infra/helm/todo/templates/secrets.yaml (from GitHub secrets)

#### Dockerfiles

- [X] T027 [US1] Verify backend.Dockerfile in infra/docker/ is optimized (multi-stage build, UV, minimal base image)
- [X] T028 [US1] Verify frontend.Dockerfile in infra/docker/ is optimized (Next.js standalone build)

#### Health Checks

- [X] T029 [US1] Add /health endpoint to backend in backend/src/main.py - Returns 200 OK with DB connectivity check
- [X] T030 [US1] Add /ready endpoint to backend - Returns 200 OK when app initialization complete
- [X] T031 [US1] Update backend-deployment.yaml to include liveness and readiness probes (HTTP /health and /ready)

#### Deployment

- [ ] T032 [US1] Build and push backend Docker image to ghcr.io manually - `docker build -t ghcr.io/<user>/todo-backend:v2.0.0`
- [ ] T033 [US1] Build and push frontend Docker image to ghcr.io manually
- [ ] T034 [US1] Deploy Helm chart to OKE - `helm install todo ./infra/helm/todo -f values.oke.yaml -n todo --create-namespace`
- [ ] T035 [US1] Verify all pods are running (backend, frontend) with 2/2 containers (app + dapr sidecar)

**Acceptance**: Navigate to https://<loadbalancer-ip>.nip.io, create account, add task, verify AI chat works. All Phase I-IV functionality operational.

---

## Phase 4: User Story 2 - Advanced Task Management Features (Priority: P2)

**Story Goal**: Enable users to manage tasks with priorities, tags, search, filtering, sorting, recurring tasks, due dates, and reminders.

**Independent Test**:

- Create task with priority=High, tags=["work", "urgent"], due_date="2026-01-15T10:00:00Z"
- Search for task by keyword
- Filter tasks by priority=High
- Sort tasks by due_date ascending
- Create recurring task (weekly pattern) - verify next_execution_time calculated correctly
- (Recurring instance generation tested in US3)

### Tasks

#### Backend - Extended Task API

- [X] T036 [P] [US2] Extend POST /api/{user_id}/tasks endpoint in backend/src/api/tasks.py to accept priority, tags, due_date, recurrence_pattern, reminder_lead_time
- [X] T037 [P] [US2] Add validation to Task creation - priority enum, tags max 10 items, due_date in future, recurrence_pattern enum
- [X] T038 [P] [US2] Extend GET /api/{user_id}/tasks endpoint to support query parameters: priority, tags, status, due_date_from, due_date_to, sort, order
- [X] T039 [P] [US2] Implement filter logic in backend/src/services/task_service.py - Filter tasks by priority, tags (array contains), status, due date range
- [X] T040 [P] [US2] Implement sort logic in task_service.py - Sort by priority (High>Medium>Low), due_date, created_at with asc/desc order
- [X] T041 [P] [US2] Add GET /api/{user_id}/tasks/search endpoint for full-text search - Search title and description fields using PostgreSQL ILIKE
- [X] T042 [P] [US2] Add PATCH /api/{user_id}/tasks/{task_id} endpoint for partial updates - Support updating any task field including priority, tags, due_date

#### Backend - Recurring Task Logic

- [X] T043 [US2] Implement calculate_next_execution() function in backend/src/services/recurrence_service.py - Use dateutil.relativedelta for daily/weekly/monthly patterns
- [X] T044 [US2] Create RecurringTaskSchedule entry when task with recurrence_pattern != 'none' is created - Calculate next_execution_time, set is_active=True
- [X] T045 [US2] Add DELETE cascade logic - When parent task deleted, delete associated RecurringTaskSchedule and set is_active=False

#### Backend - Notification Preparation

- [X] T046 [US2] Create NotificationService class in backend/src/services/notification_service.py with create_notification() method - Stores in database
- [X] T047 [US2] Add GET /api/{user_id}/notifications endpoint - List notifications, support unread_only filter, return unread_count
- [X] T048 [US2] Add PATCH /api/{user_id}/notifications/{notification_id}/mark_read endpoint - Update delivery_status to 'read'

#### Frontend - Advanced Task UI

- [ ] T049 [P] [US2] Extend TaskForm component in frontend/src/components/TaskForm.tsx - Add priority dropdown (High/Medium/Low), tags input (multi-select or comma-separated), due_date datetime picker
- [ ] T050 [P] [US2] Create RecurringTaskForm component in frontend/src/components/RecurringTaskForm.tsx - Recurrence pattern dropdown (none/daily/weekly/monthly), reminder_lead_time input (minutes)
- [ ] T051 [P] [US2] Extend TaskList component in frontend/src/components/TaskList.tsx - Display priority badge with color (High=red, Medium=yellow, Low=green), show tags as chips, show due date with overdue indicator
- [ ] T052 [P] [US2] Add SearchBar component in frontend/src/components/SearchBar.tsx - Input field with search icon, triggers API call on Enter or button click
- [ ] T053 [P] [US2] Add FilterControls component in frontend/src/components/FilterControls.tsx - Dropdowns for priority, tags, status, due date range pickers, Apply Filters button

**Acceptance**: Create task with priority High, tags ["work", "urgent"], due date tomorrow. Search for "urgent", filter by High priority, sort by due date. Verify all UI updates correctly.

---

## Phase 5: User Story 3 - Event-Driven Microservices Architecture (Priority: P3)

**Story Goal**: Implement Kafka event publishing from backend and 3 consuming microservices (Notification, Recurring Tasks, Audit).

**Independent Test**:

- Create a task → Verify task-created event published to Kafka task-events topic
- Update task → Verify task-updated event published
- Notification Service consumes task-created event → Creates in-app notification
- Recurring Tasks Service checks schedules due → Generates new task instances
- Audit Service consumes all events → Creates audit log entries
- Check Kafka topic via rpk CLI or Redpanda Console to see events

### Tasks

#### Backend - Event Publishing

- [X] T054 [P] [US3] Create EventPublisher service in backend/src/services/event_publisher.py - Uses Dapr pub/sub client to publish to 'task-events' topic
- [X] T055 [P] [US3] Create TaskEvent record in database when event published - Store event_id, event_type, task_id, user_id, timestamp, payload, published_to_kafka=True
- [X] T056 [US3] Integrate EventPublisher in POST /tasks endpoint - Publish task-created event after task created
- [X] T057 [US3] Integrate EventPublisher in PATCH /tasks endpoint - Publish task-updated event, or task-completed if status changed to 'completed'
- [X] T058 [US3] Integrate EventPublisher in DELETE /tasks endpoint - Publish task-deleted event before task deleted
- [X] T059 [US3] Add event partitioning logic - Partition Kafka messages by task_id to ensure ordering per task

#### Notification Service (Microservice 1)

- [X] T060 [P] [US3] Create FastAPI app in services/notification-service/src/main.py with health endpoint
- [X] T061 [P] [US3] Create pyproject.toml for notification-service with dependencies (fastapi, dapr-ext-grpc, sqlmodel, aiokafka)
- [X] T062 [P] [US3] Implement Kafka consumer in services/notification-service/src/consumers/task_event_consumer.py - Subscribe to task-events topic via Dapr
- [X] T063 [US3] Implement event handler - When task-created or task-completed event received, create Notification record in database
- [X] T064 [US3] Add idempotency check - Check event_id in processed_events set/table to prevent duplicate notifications
- [X] T065 [US3] Create Dockerfile for notification-service in infra/docker/notification-service.Dockerfile

#### Recurring Tasks Service (Microservice 2)

- [X] T066 [P] [US3] Create FastAPI app in services/recurring-tasks-service/src/main.py with health endpoint
- [X] T067 [P] [US3] Create pyproject.toml with dependencies (fastapi, dapr-ext-grpc, sqlmodel, apscheduler, python-dateutil)
- [X] T068 [P] [US3] Implement APScheduler in services/recurring-tasks-service/src/scheduler/task_scheduler.py - Run cron job every minute to check due schedules
- [X] T069 [US3] Implement recurrence logic - Query RecurringTaskSchedule where next_execution_time <= now() and is_active=True
- [X] T070 [US3] Generate new task instance - Copy parent task, update due_date based on pattern, create Task record, publish task-created event
- [X] T071 [US3] Update RecurringTaskSchedule - Set last_executed_at=now(), calculate and set next_execution_time using calculate_next_execution()
- [X] T072 [US3] Create Dockerfile for recurring-tasks-service in infra/docker/recurring-tasks-service.Dockerfile

#### Audit Service (Microservice 3)

- [X] T073 [P] [US3] Create FastAPI app in services/audit-service/src/main.py with health endpoint
- [X] T074 [P] [US3] Create pyproject.toml with dependencies (fastapi, dapr-ext-grpc, sqlmodel, aiokafka)
- [X] T075 [P] [US3] Implement Kafka consumer in services/audit-service/src/consumers/audit_event_consumer.py - Subscribe to task-events, reminders, task-updates topics

**Acceptance**: Create/update/complete/delete tasks. Use Redpanda Console or rpk CLI to verify events published to Kafka. Check notifications table for new entries. Check audit_logs table for all operations logged.

---

## Phase 6: User Story 4 - CI/CD Automation (Priority: P2)

**Story Goal**: Automate build, test, and deployment to OKE via GitHub Actions.

**Independent Test**:

- Push commit to main branch
- GitHub Actions workflow triggers automatically
- Docker images built and pushed to ghcr.io
- Helm chart deployed/upgraded on OKE
- Verify zero-downtime deployment (old pods serve traffic during rollout)

### Tasks

#### GitHub Actions Workflows

- [X] T076 [P] [US4] Create .github/workflows/build-and-test.yml - Triggers on pull_request, runs pytest for backend, npm test for frontend, linting
- [X] T077 [P] [US4] Create .github/workflows/build-images.yml - Triggers on push to main, builds all 5 Docker images (backend, frontend, 3 microservices), pushes to ghcr.io with tag 'latest' and git SHA
- [X] T078 [P] [US4] Create .github/workflows/deploy-oke.yml - Triggers after build-images.yml succeeds, authenticates to OKE using OCI credentials from secrets, runs `helm upgrade todo ./infra/helm/todo -f values.oke.yaml`
- [X] T079 [P] [US4] Create .github/workflows/rollback.yml - Manual workflow_dispatch trigger, rolls back to previous Helm release using `helm rollback todo`
- [X] T080 [US4] Add health check validation step in deploy-oke.yml - After deployment, curl /health endpoint, fail workflow if not 200 OK

#### Helm Updates for CI/CD

- [X] T081 [US4] Update Helm deployment templates to use image tags from environment variable - `image: {{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}`
- [X] T082 [US4] Add rolling update strategy in deployment templates - `strategy: type: RollingUpdate, maxUnavailable: 0, maxSurge: 1`
- [X] T083 [US4] Configure pod disruption budgets in infra/helm/todo/templates/pdb.yaml - Ensure at least 1 replica always available during updates

#### Documentation

- [ ] T084 [US4] Update README.md with CI/CD badge from GitHub Actions
- [ ] T085 [US4] Document rollback procedure in README.md - How to trigger manual rollback workflow

**Acceptance**: Make trivial code change (e.g., update version in package.json), commit to main. Verify GitHub Actions completes successfully, new images pushed, Helm upgrade runs, pods updated with zero downtime.

---

## Phase 7: User Story 5 - Dapr Integration (Priority: P3)

**Story Goal**: Migrate event publishing to Dapr pub/sub, conversation state to Dapr state store, and secrets to Dapr secret store.

**Independent Test**:

- Backend publishes events via Dapr pub/sub (not direct Kafka client)
- Microservices subscribe via Dapr
- Conversation state saved/retrieved from Redis via Dapr state API
- Database URL retrieved from Dapr secret store (Kubernetes Secret)
- Verify Dapr sidecar logs show pub/sub and state operations

### Tasks

#### Dapr Pub/Sub

- [ ] T086 [P] [US5] Update EventPublisher in backend/src/services/event_publisher.py to use DaprClient.publish_event() instead of direct Kafka client
- [ ] T087 [P] [US5] Update NotificationService consumer to use @dapr_app.subscribe() decorator for topic subscription
- [ ] T088 [P] [US5] Update AuditService consumer to use @dapr_app.subscribe() decorator
- [ ] T089 [US5] Deploy Dapr kafka-pubsub.yaml component from infra/dapr/components/ to OKE - `kubectl apply -f infra/dapr/components/kafka-pubsub.yaml -n todo`
- [ ] T090 [US5] Verify events flow through Dapr - Check dapr sidecar logs for pub/sub operations

#### Dapr State Management

- [ ] T091 [P] [US5] Migrate conversation state in backend/src/chatkit/ to use DaprClient.save_state() and get_state() for Redis state store
- [ ] T092 [US5] Deploy Dapr redis-statestore.yaml component - `kubectl apply -f infra/dapr/components/redis-statestore.yaml -n todo`
- [ ] T093 [US5] Test conversation state persistence - Start chat, save state, restart pod, verify state retrieved from Redis

#### Dapr Secrets Management

- [ ] T094 [P] [US5] Create Kubernetes Secret for DATABASE_URL - `kubectl create secret generic db-credentials --from-literal=DATABASE_URL=<neon-url> -n todo`
- [ ] T095 [P] [US5] Update backend to retrieve DATABASE_URL from Dapr secrets API using DaprClient.get_secret()
- [ ] T096 [US5] Deploy Dapr kubernetes-secrets.yaml component - `kubectl apply -f infra/dapr/components/kubernetes-secrets.yaml -n todo`
- [ ] T097 [US5] Remove DATABASE_URL from Helm ConfigMap - Ensure secret retrieval from Dapr works

#### Dapr Service Invocation

- [ ] T098 [US5] Implement service-to-service call from backend to recurring-tasks-service using DaprClient.invoke_method() - Example: Create schedule endpoint
- [ ] T099 [US5] Add retry and circuit breaker configuration in infra/dapr/config/dapr-config.yaml per research.md

**Acceptance**: All events published/consumed via Dapr (check sidecar logs), conversation state in Redis (check Redis keys), DATABASE_URL retrieved from Dapr secrets (no hardcoded env var).

---

## Phase 8: Polish & Cross-Cutting Concerns (No Story Label)

**Goal**: Add observability, documentation, and final touches for production readiness.

**Independent Test**: All polishing items checked off, demo video recorded, README updated with production URL.

### Tasks

#### Observability

- [ ] T100 [P] Add structured JSON logging to all services - Use Python logging with JSON formatter, include correlation_id in all log messages
- [ ] T101 [P] Configure Prometheus metrics export in all FastAPI apps - Use prometheus_client library, expose /metrics endpoint
- [ ] T102 [P] Deploy Zipkin for distributed tracing (optional) - Follow research.md Zipkin setup, configure Dapr to send traces
- [ ] T103 Add correlation ID middleware in backend/src/main.py and all microservices - Generate X-Correlation-ID header, propagate across services

#### Documentation

- [ ] T104 Update README.md with Phase V section - Add OKE deployment instructions, link to quickstart.md, production URL
- [ ] T105 Create demo video (max 90 seconds) - Show: Cloud deployment, create task with priority/tags, search/filter, recurring task creates instance, notification appears, audit log entry
- [ ] T106 Update CLAUDE.md with Phase V technologies - Add Kafka, Dapr, OKE, APScheduler to Active Technologies section

#### Testing & Validation

- [ ] T107 [P] Run load test with k6 or Locust - Verify 500 concurrent users target, measure p95 latency < 500ms
- [ ] T108 Submit Phase V to hackathon - Fill out form at <https://forms.gle/KMKEKaFUD6ZX4UtY8>, upload demo video, provide GitHub repo link and production URL

---

## Parallel Execution Opportunities

### Phase 1 (Setup) - Can run in parallel

- T006-T012: All infrastructure installations (Dapr, NGINX, cert-manager, Redis, ClusterIssuer, GitHub secrets, services/ dir)

### Phase 2 (Foundational) - Can run in parallel

- T014-T017: All 4 new model files (TaskEvent, RecurringTaskSchedule, Notification, AuditLog)

### Phase 3 (US1) - Can run in parallel

- T021-T026: All Helm chart updates (Chart.yaml, values.oke.yaml, deployment annotations, ingress, configmap, secrets)

### Phase 4 (US2) - Can run in parallel

- T036-T042: All backend API endpoint extensions (different routes/files)
- T049-T053: All frontend component updates (different .tsx files)

### Phase 5 (US3) - Can run in parallel

- T054-T055: Event publishing service
- T060-T065: Notification service (separate microservice)
- T066-T072: Recurring tasks service (separate microservice)
- T073-T075: Audit service (separate microservice)

### Phase 6 (US4) - Can run in parallel

- T076-T079: All 4 GitHub Actions workflow files

### Phase 7 (US5) - Can run in parallel

- T086-T088: Dapr pub/sub migrations (backend and 2 consumers)
- T091, T094-T095: Dapr state and secrets (different concerns)

### Phase 8 (Polish) - Can run in parallel

- T100-T102: Observability features (logging, metrics, tracing)

---

## Implementation Strategy

### MVP (Minimum Viable Product)

**Scope**: Phase 1-3 (US1: Cloud Deployment)
**Outcome**: Phase I-IV app running on OKE with HTTPS
**Deliverable**: Public URL, health checks, Dapr sidecars
**Timeline**: Complete US1 first to unlock cloud environment

### Incremental Delivery

1. **Iteration 1** (MVP): US1 - Deploy to cloud
2. **Iteration 2**: US2 - Add advanced task features (priority, tags, search)
3. **Iteration 3**: US3 - Implement event-driven architecture (3 microservices)
4. **Iteration 4**: US4 - Automate CI/CD
5. **Iteration 5**: US5 - Migrate to Dapr fully
6. **Iteration 6**: Polish & submit

### Testing Strategy

- **Per User Story**: Each story has independent acceptance criteria
- **Integration Tests**: Run after each story completion
- **E2E Tests**: Run after US1 (cloud) and US2 (features) to verify full user flows
- **Load Tests**: Run during Polish phase (Phase 8)

---

## Validation Checklist

Before considering Phase V complete, verify:

- [ ] All 107 tasks checked off
- [ ] All 5 user stories meet their acceptance criteria
- [ ] Application deployed to OKE and accessible via public HTTPS URL
- [ ] All Phase I-IV features work identically in cloud deployment
- [ ] Advanced features functional: priority, tags, search, filter, sort, recurring tasks, reminders
- [ ] 3 microservices running and consuming events from Kafka
- [ ] CI/CD pipeline deploys automatically on push to main
- [ ] Dapr sidecars injected and operational (pub/sub, state, secrets)
- [ ] Observability implemented (logs, metrics, traces, correlation IDs)
- [ ] Demo video recorded (max 90 seconds)
- [ ] README.md updated with production URL and deployment instructions
- [ ] Hackathon submission form completed

---

## Notes

- **[P] marker**: Indicates parallelizable tasks (can be worked on simultaneously)
- **[US#] label**: Links task to specific user story for traceability
- **File paths**: Exact paths provided for each task
- **No test tasks**: Tests not explicitly requested in specification, integration testing via acceptance criteria
- **Constitution compliance**: All tasks align with SDD, no manual coding, cloud-native, event-driven, security-first, observability, simplicity principles

**Ready for implementation**: Use `/sp.implement` command or implement tasks manually following this breakdown.
