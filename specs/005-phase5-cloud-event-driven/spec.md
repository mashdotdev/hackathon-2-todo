# Feature Specification: Phase V - Cloud Deployment with Event-Driven Architecture

**Feature Branch**: `005-phase5-cloud-event-driven`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Phase V: Cloud Deployment with Event-Driven Architecture"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cloud-Deployed Application Access (Priority: P1)

Users access the fully cloud-deployed todo application with production-grade reliability and performance, experiencing the same features as Phase IV but now running on enterprise-grade cloud infrastructure.

**Why this priority**: Foundation for all other Phase V features. Without successful cloud deployment, no other event-driven or advanced features can be delivered. This proves the application is production-ready and scalable.

**Independent Test**: Can be fully tested by deploying to cloud Kubernetes (DOKS/AKS/GKE/OKE), accessing the application via public URL, and verifying all Phase I-IV features work identically. Delivers immediate value by making the application publicly accessible and production-ready.

**Acceptance Scenarios**:

1. **Given** the application is deployed to cloud Kubernetes, **When** a user navigates to the production URL, **Then** the application loads successfully with all features from Phases I-IV functional
2. **Given** the cloud deployment is running, **When** the cluster is restarted or a pod fails, **Then** the application automatically recovers without data loss
3. **Given** multiple users access the application simultaneously, **When** load increases to 100 concurrent users, **Then** response times remain under 2 seconds for all operations
4. **Given** the application is running in production, **When** monitoring dashboards are accessed, **Then** all health metrics, logs, and traces are visible and accurate

---

### User Story 2 - Advanced Task Management Features (Priority: P2)

Users manage tasks with intermediate and advanced features including priorities, tags, search, filtering, sorting, recurring tasks, due dates, and reminders, enabling sophisticated task organization and time management.

**Why this priority**: Elevates the application from basic CRUD to a professional task management system. These features differentiate the product from Phase I-IV and provide significant user value for real-world usage.

**Independent Test**: Can be fully tested by creating tasks with priorities/tags, searching and filtering tasks by various criteria, setting up recurring tasks and due dates, and verifying reminder notifications trigger at scheduled times. Delivers independent value even without cloud deployment or events.

**Acceptance Scenarios**:

1. **Given** a user is creating a task, **When** they set priority (High/Medium/Low), tags (work, personal, urgent), and due date, **Then** the task is saved with all metadata and displays correctly in the task list
2. **Given** a user has multiple tasks with different attributes, **When** they search by keyword or filter by priority/tag/status/date, **Then** only matching tasks are displayed with accurate results
3. **Given** a user sorts tasks by priority, due date, or creation date, **When** the sort order is changed, **Then** tasks re-order accordingly with visual indicators showing sort criteria
4. **Given** a user creates a recurring task (daily/weekly/monthly), **When** the recurrence period elapses, **Then** a new instance of the task is automatically created with updated due date
5. **Given** a user sets a due date and reminder time for a task, **When** the reminder time arrives, **Then** the user receives a notification via the notification service

---

### User Story 3 - Event-Driven Microservices Architecture (Priority: P3)

The system operates as a distributed, event-driven architecture where task operations trigger events that are consumed by specialized microservices (Notification Service, Recurring Tasks Service, Audit Service), enabling scalable, decoupled processing and real-time responsiveness.

**Why this priority**: Demonstrates mastery of modern distributed systems architecture. While not immediately user-facing, this architectural evolution enables horizontal scaling, fault isolation, and extensibility. Critical for hackathon evaluation and bonus points.

**Independent Test**: Can be fully tested by performing task operations (create/update/complete/delete), monitoring Kafka topics for published events, and verifying that each microservice consumes relevant events and performs its specialized function (sends notifications, creates recurring instances, logs audit trail). Delivers value through improved system reliability and scalability.

**Acceptance Scenarios**:

1. **Given** a user completes a task, **When** the task status changes, **Then** a "task-completed" event is published to the `task-events` Kafka topic
2. **Given** a task-completed event is published, **When** the Notification Service consumes the event, **Then** a success notification is sent to the user
3. **Given** a recurring task reaches its scheduled time, **When** the Recurring Tasks Service processes the schedule, **Then** a new task instance is created and a "task-created" event is published
4. **Given** any task operation occurs (create/update/delete/complete), **When** the Audit Service consumes the event, **Then** an immutable audit log entry is created with timestamp, user, action, and task details
5. **Given** a microservice fails temporarily, **When** events are published during the outage, **Then** Kafka retains the events and the service processes them upon recovery without data loss

---

### User Story 4 - CI/CD Automation (Priority: P2)

Code changes are automatically built, tested, and deployed to the cloud Kubernetes cluster through GitHub Actions pipelines, enabling rapid iteration and reducing manual deployment errors.

**Why this priority**: Essential for production-grade software delivery. Automates the deployment process demonstrated in Phase IV, reduces human error, and accelerates development velocity. Required for demonstrating DevOps maturity.

**Independent Test**: Can be fully tested by committing code changes to the repository, triggering the GitHub Actions pipeline, and verifying automatic build, test execution, container image creation, and deployment to cloud Kubernetes. Delivers immediate value by eliminating manual deployment steps.

**Acceptance Scenarios**:

1. **Given** a developer pushes code to the main branch, **When** the GitHub Actions workflow triggers, **Then** the code is automatically built, tested, containerized, and deployed to production within 10 minutes
2. **Given** tests fail during the CI pipeline, **When** the build process runs, **Then** deployment is blocked and the developer is notified of failures
3. **Given** a successful deployment completes, **When** the new version is live, **Then** health checks verify the application is running and monitoring confirms zero downtime deployment
4. **Given** a deployment needs to be rolled back, **When** the rollback workflow is triggered, **Then** the previous version is restored within 5 minutes

---

### User Story 5 - Dapr-Enabled Distributed Services (Priority: P3)

The application leverages Dapr (Distributed Application Runtime) for service-to-service communication, state management, pub/sub messaging, secrets management, and scheduled jobs, enabling cloud-native patterns and portability across cloud providers.

**Why this priority**: Demonstrates advanced distributed systems expertise. Dapr abstracts infrastructure concerns (service mesh, state stores, message brokers) from application code, enabling cloud-agnostic deployment and simplified microservices development.

**Independent Test**: Can be fully tested by verifying Dapr sidecars are deployed alongside application pods, observing service invocation through Dapr APIs, confirming conversation state is persisted via Dapr state management, validating secrets are retrieved from Dapr secret store, and ensuring reminder jobs are scheduled via Dapr Jobs API. Delivers value through simplified service communication and enhanced portability.

**Acceptance Scenarios**:

1. **Given** microservices need to communicate, **When** Service A invokes Service B, **Then** the call is routed through Dapr service invocation with automatic retries and circuit breaking
2. **Given** conversation state needs to be persisted, **When** the chatbot service saves state, **Then** Dapr stores it in the configured state store (Redis/PostgreSQL) and retrieves it correctly on subsequent requests
3. **Given** task events are published, **When** the main application publishes to Dapr pub/sub, **Then** Dapr forwards events to the configured Kafka broker and subscribing services receive them
4. **Given** the application requires database credentials, **When** the service starts, **Then** secrets are retrieved from Dapr's secret store (Kubernetes Secrets) without hardcoding
5. **Given** a recurring task needs scheduling, **When** the Recurring Tasks Service uses Dapr Jobs API, **Then** jobs are executed at scheduled intervals reliably

---

### Edge Cases

- **What happens when Kafka is temporarily unavailable?** Events should be buffered by Dapr and retried automatically when Kafka recovers. Services should continue operating with degraded functionality (e.g., delayed notifications).

- **How does the system handle timezone differences for reminders?** All timestamps are stored in UTC and converted to user's local timezone for display and notification scheduling.

- **What happens when a recurring task's parent is deleted?** All future instances of the recurring task are also cancelled, and a "task-deleted" event is published.

- **How does the system prevent duplicate event processing?** Each event includes a unique event ID, and consumers implement idempotency checks to avoid duplicate processing.

- **What happens when cloud infrastructure costs exceed budget?** Monitoring alerts trigger when spending approaches thresholds, and auto-scaling policies prevent runaway costs while maintaining availability.

- **How does the system handle schema evolution in event payloads?** Events use versioned schemas, and consumers are designed to handle both old and new versions gracefully during rolling updates.

- **What happens during zero-downtime deployments?** Kubernetes rolling updates ensure old pods continue serving traffic while new pods are starting. Health checks prevent traffic routing to unhealthy pods.

- **How are failed reminder notifications handled?** Failed notifications are retried with exponential backoff up to 3 times, then logged to the audit service for manual review.

## Requirements *(mandatory)*

### Functional Requirements

#### Cloud Deployment Requirements

- **FR-001**: System MUST be deployed to a production-grade cloud Kubernetes service (DigitalOcean DOKS, Azure AKS, Google GKE, or Oracle OKE)
- **FR-002**: Application MUST be accessible via a public URL with valid SSL/TLS certificate
- **FR-003**: System MUST implement automated health checks (liveness and readiness probes) for all services
- **FR-004**: Deployment MUST support zero-downtime updates using rolling deployment strategy
- **FR-005**: Infrastructure MUST be defined using Infrastructure as Code (Helm charts extended from Phase IV)

#### Advanced Task Management Requirements

- **FR-006**: Users MUST be able to assign priority levels (High, Medium, Low) to tasks
- **FR-007**: Users MUST be able to add multiple tags to tasks for categorization
- **FR-008**: Users MUST be able to search tasks by title, description, or tags
- **FR-009**: Users MUST be able to filter tasks by status, priority, tags, and due date ranges
- **FR-010**: Users MUST be able to sort tasks by priority, due date, or creation date
- **FR-011**: Users MUST be able to set due dates and times for tasks
- **FR-012**: Users MUST be able to configure recurring tasks with daily, weekly, or monthly recurrence patterns
- **FR-013**: Users MUST be able to set reminder notifications for tasks with specific lead times (e.g., 1 hour before, 1 day before)

#### Event-Driven Architecture Requirements

- **FR-014**: System MUST publish events to Kafka topics for all task lifecycle operations (create, update, complete, delete)
- **FR-015**: System MUST implement three Kafka topics: `task-events`, `reminders`, `task-updates`
- **FR-016**: Notification Service MUST consume events from Kafka and send notifications to users
- **FR-017**: Recurring Tasks Service MUST consume events and generate new task instances based on recurrence rules
- **FR-018**: Audit Service MUST consume all task events and maintain an immutable audit log
- **FR-019**: All microservices MUST implement idempotent event processing to prevent duplicate actions
- **FR-020**: System MUST use Kafka consumer groups to ensure exactly-once event processing per service

#### Dapr Integration Requirements

- **FR-021**: All microservices MUST deploy with Dapr sidecars for distributed runtime capabilities
- **FR-022**: Service-to-service communication MUST use Dapr service invocation API
- **FR-023**: Conversation state from Phase III MUST be managed via Dapr state management API
- **FR-024**: Event publishing and subscription MUST use Dapr pub/sub API with Kafka as the broker
- **FR-025**: Reminder scheduling MUST use Dapr Jobs API for reliable scheduled execution
- **FR-026**: Sensitive credentials (database passwords, API keys) MUST be retrieved via Dapr secrets management API

#### CI/CD Requirements

- **FR-027**: System MUST implement GitHub Actions workflows for automated build, test, and deployment
- **FR-028**: CI pipeline MUST run all tests (unit, integration) and block deployment on test failures
- **FR-029**: CI pipeline MUST build Docker images and push to container registry automatically
- **FR-030**: CD pipeline MUST deploy to cloud Kubernetes using Helm with automated rollback on health check failures
- **FR-031**: Deployment process MUST include automated smoke tests to verify deployment success

#### Observability Requirements

- **FR-032**: All services MUST emit structured JSON logs with correlation IDs for request tracing
- **FR-033**: System MUST expose Prometheus-compatible metrics for monitoring (request count, latency, error rate)
- **FR-034**: Cloud-native monitoring solution MUST be integrated for alerting and visualization
- **FR-035**: Distributed tracing MUST be enabled across all microservices with correlation IDs

### Key Entities

- **Task** (extended from previous phases):
  - **New attributes**: priority (High/Medium/Low), tags (array of strings), due_date (timestamp), recurrence_pattern (daily/weekly/monthly/none), reminder_lead_time (duration in minutes)
  - **Relationships**: Associated with User, generates TaskEvents, linked to RecurringTaskSchedule

- **TaskEvent**:
  - **Attributes**: event_id (unique), event_type (task-created/task-updated/task-completed/task-deleted), task_id, user_id, timestamp, payload (task data snapshot)
  - **Purpose**: Immutable event record for audit trail and microservice consumption

- **RecurringTaskSchedule**:
  - **Attributes**: schedule_id, parent_task_id, recurrence_pattern, next_execution_time, is_active
  - **Purpose**: Manages recurring task generation logic

- **Notification**:
  - **Attributes**: notification_id, user_id, task_id, notification_type (reminder/completion/created), message, sent_at, delivery_status
  - **Purpose**: Tracks notification delivery for reminders and task events

- **AuditLog**:
  - **Attributes**: audit_id, timestamp, user_id, action_type, resource_type, resource_id, event_data (JSON), correlation_id
  - **Purpose**: Immutable audit trail for compliance and debugging

- **Conversation** (from Phase III, now with Dapr state management):
  - **Attributes**: conversation_id, user_id, messages (array), state (JSON), last_updated
  - **State management**: Persisted via Dapr state store for stateless service design

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### Cloud Deployment & Reliability

- **SC-001**: Application is successfully deployed to cloud Kubernetes and accessible via public HTTPS URL with valid certificate
- **SC-002**: System maintains 99.9% uptime over a 7-day monitoring period
- **SC-003**: Zero-downtime deployments complete successfully with no user-facing errors during updates
- **SC-004**: Application supports at least 500 concurrent users without performance degradation
- **SC-005**: All health checks (liveness, readiness) respond within 500ms

#### Performance & Scalability

- **SC-006**: Task creation, update, and retrieval operations complete in under 500ms at p95
- **SC-007**: Search and filter operations return results in under 1 second for datasets up to 10,000 tasks per user
- **SC-008**: Event publishing to Kafka completes asynchronously without blocking user operations (sub-100ms overhead)
- **SC-009**: Microservices process events from Kafka within 5 seconds of publication under normal load

#### Feature Completeness

- **SC-010**: Users can successfully create tasks with priorities, tags, due dates, and recurrence patterns, with 100% data accuracy
- **SC-011**: Search and filter features return accurate results matching query criteria 100% of the time
- **SC-012**: Recurring tasks generate new instances automatically within 1 minute of scheduled time
- **SC-013**: Reminder notifications are delivered within 2 minutes of scheduled reminder time for 95% of cases
- **SC-014**: Audit logs capture 100% of task operations with complete event data and correlation IDs

#### CI/CD & Automation

- **SC-015**: Code commits trigger automated CI/CD pipeline and deploy to production within 15 minutes for passing builds
- **SC-016**: Failed tests block deployment 100% of the time, preventing broken code from reaching production
- **SC-017**: Automated rollbacks complete within 5 minutes when deployment health checks fail

#### Event-Driven Architecture

- **SC-018**: All task events are published to Kafka with 100% success rate (no lost events)
- **SC-019**: Each microservice (Notification, Recurring Tasks, Audit) processes events independently with zero cross-service dependencies
- **SC-020**: System recovers from Kafka or microservice failures gracefully with automatic retry and event replay

#### Observability

- **SC-021**: All services emit structured logs with correlation IDs enabling end-to-end request tracing
- **SC-022**: Monitoring dashboards display real-time metrics for all services with data freshness under 1 minute
- **SC-023**: Alerts trigger within 2 minutes when error rates exceed 5% or latency exceeds SLOs

#### Dapr Integration

- **SC-024**: All service-to-service communication routes through Dapr with automatic retries on transient failures
- **SC-025**: Conversation state persists and retrieves correctly via Dapr state management with zero data loss
- **SC-026**: Secrets are never hardcoded and all credentials are retrieved from Dapr secret store at runtime

## Assumptions

1. **Cloud Provider**: Any of the constitution-approved providers (DOKS/AKS/GKE/OKE) can be used. Oracle OKE is assumed for cost considerations (always-free tier).
2. **Kafka Provider**: Redpanda Cloud is assumed for managed Kafka to simplify operations, though Strimzi (self-hosted on K8s) is acceptable.
3. **Database**: Neon Serverless PostgreSQL from Phase II continues to be used; no migration to cloud-managed database required.
4. **Notification Delivery**: Notifications are in-app messages or webhook-based; email/SMS integration is out of scope for Phase V.
5. **User Timezone**: User timezone is captured during registration or inferred from browser; defaults to UTC if unavailable.
6. **Retention Policy**: Audit logs are retained indefinitely; task events in Kafka are retained for 30 days per topic configuration.
7. **SSL Certificates**: Let's Encrypt or cloud provider-managed certificates are used for HTTPS.
8. **Monitoring Stack**: Cloud-native monitoring is assumed (e.g., DigitalOcean Monitoring, Azure Monitor, GCP Cloud Monitoring); self-hosted Prometheus/Grafana is optional.
9. **Dapr Version**: Dapr 1.12+ is assumed with stable APIs for state management, pub/sub, service invocation, and jobs.
10. **Resource Limits**: Cloud Kubernetes cluster is sized for hackathon demo load (3-5 nodes, 8GB RAM per node); production scaling is out of scope.
11. **Multi-tenancy**: User isolation continues via user_id filtering; no dedicated namespaces or separate deployments per user.
12. **Event Ordering**: Events for a single task are ordered; cross-task event ordering is not guaranteed (eventual consistency model).

## Out of Scope

1. **Multi-cloud deployment**: Single cloud provider deployment only; no multi-cloud failover or federation.
2. **Advanced notification channels**: Email, SMS, push notifications via mobile apps are not implemented; in-app notifications only.
3. **Real-time collaboration**: Multiple users editing the same task simultaneously is not supported.
4. **Advanced analytics dashboard**: Business intelligence dashboards and reporting are not included.
5. **Mobile applications**: Native iOS/Android apps are out of scope; web app only.
6. **Third-party integrations**: Integrations with external services (Google Calendar, Slack, Trello) are not implemented.
7. **Custom recurrence patterns**: Only daily/weekly/monthly recurrence is supported; complex patterns (e.g., "every 2nd Tuesday") are out of scope.
8. **Task dependencies and subtasks**: Tasks cannot have prerequisites or be broken into subtasks.
9. **Team/shared task lists**: All tasks are private to individual users; team collaboration features are not included.
10. **Data migration tools**: No automated migration from other task management systems.
11. **Offline support**: Application requires internet connectivity; offline mode is not implemented.
12. **Voice commands bonus**: Deferred to future phases if time permits; not required for Phase V completion.

## Dependencies

### External Dependencies

1. **Cloud Kubernetes Service**: Active account on DOKS/AKS/GKE/OKE with appropriate quotas and billing configured.
2. **Kafka Service**: Redpanda Cloud account or Strimzi deployed on Kubernetes cluster.
3. **GitHub Actions**: GitHub repository with Actions enabled and cloud service credentials configured as secrets.
4. **Container Registry**: Docker Hub, GitHub Container Registry, or cloud provider registry for storing container images.
5. **Dapr Runtime**: Dapr 1.12+ installed on Kubernetes cluster via Helm or Dapr CLI.
6. **Neon PostgreSQL**: Continued access to Neon Serverless PostgreSQL from Phase II.
7. **SSL Certificate Provider**: Let's Encrypt (via cert-manager) or cloud provider SSL management.

### Internal Dependencies

1. **Phase IV Completion**: All Phase IV features (local Kubernetes deployment, Helm charts, Dockerfiles) must be completed and tested.
2. **Database Schema Extensions**: Database must be migrated to support new fields (priority, tags, due_date, recurrence_pattern, reminder_lead_time).
3. **Existing API Endpoints**: Phase II-III API endpoints must be functional; Phase V extends them with query parameters for filtering/sorting.
4. **Authentication System**: Better Auth from Phase II must be operational for user authentication across all services.

## Risks

1. **Cloud Cost Overruns**: Kubernetes clusters and managed Kafka can incur significant costs if not monitored. Mitigation: Use free-tier options (Oracle OKE), implement budget alerts, and auto-scaling limits.

2. **Event Ordering and Consistency**: Distributed event systems can lead to race conditions or out-of-order processing. Mitigation: Use Kafka partitioning by task_id, implement idempotency, and design for eventual consistency.

3. **Microservice Complexity**: Adding three new microservices increases operational complexity and debugging difficulty. Mitigation: Comprehensive logging with correlation IDs, distributed tracing, and robust health checks.

4. **Dapr Learning Curve**: Team may be unfamiliar with Dapr APIs and concepts. Mitigation: Follow Dapr quickstart guides, use official SDKs, and start with simple patterns (state management) before advanced features (jobs).

5. **CI/CD Pipeline Failures**: Automated deployments can fail due to configuration errors or cloud provider issues. Mitigation: Implement extensive pipeline testing, use staged rollouts, and maintain manual rollback procedures.

6. **Kafka Message Loss**: Improper Kafka configuration can lead to message loss during failures. Mitigation: Use replication factor ≥ 3, enable acks=all for producers, and configure appropriate retention policies.

7. **Timezone and Scheduling Bugs**: Recurring tasks and reminders are complex and prone to edge cases (DST, leap years). Mitigation: Use battle-tested libraries (date-fns, Luxon), comprehensive test cases for edge conditions.

8. **Monitoring Blind Spots**: Without proper observability, production issues may go undetected. Mitigation: Implement comprehensive logging, metrics, tracing, and alerting from day one.

## Definition of Done

- [ ] Application is deployed to cloud Kubernetes (DOKS/AKS/GKE/OKE) and accessible via public HTTPS URL
- [ ] All advanced task features (priorities, tags, search, filter, sort, recurring tasks, due dates, reminders) are functional
- [ ] Event-driven architecture is operational with Kafka and three microservices (Notification, Recurring Tasks, Audit)
- [ ] Dapr is integrated for pub/sub, state management, service invocation, jobs, and secrets
- [ ] CI/CD pipeline is automated via GitHub Actions with automated deployment to cloud
- [ ] All Phase I-IV features continue to work correctly in cloud deployment
- [ ] Observability is implemented (structured logging, metrics, distributed tracing, monitoring dashboards)
- [ ] Zero-downtime deployments are verified with rolling updates and automated health checks
- [ ] Load testing confirms system supports 500 concurrent users with acceptable performance
- [ ] All success criteria (SC-001 through SC-026) are met and verified
- [ ] Specification, plan, tasks, and PHR documentation are complete in `specs/005-phase5-cloud-event-driven/`
- [ ] Demo video (max 90 seconds) is recorded and uploaded
- [ ] Submission form is completed and presentation readiness confirmed
