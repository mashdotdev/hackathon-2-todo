# Tasks: Phase IV Local Kubernetes Deployment

**Input**: Design documents from `/specs/004-phase4-kubernetes/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Manual verification via kubectl and Helm - no automated test tasks included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- **Infrastructure**: `infra/docker/`, `infra/helm/`, `infra/k8s/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create infrastructure directory structure and base files

- [x] T001 Create infra directory structure: `infra/docker/`, `infra/helm/todo/templates/`, `infra/k8s/`
- [x] T002 [P] Create backend/.dockerignore with Python exclusions
- [x] T003 [P] Create frontend/.dockerignore with Node.js exclusions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Docker images and health endpoints MUST be complete before ANY Kubernetes deployment

**⚠️ CRITICAL**: No Helm/K8s work can begin until Docker images and health endpoints are ready

### Docker Images

- [x] T004 Create multi-stage Dockerfile for backend in infra/docker/backend.Dockerfile
- [x] T005 [P] Create multi-stage Dockerfile for frontend in infra/docker/frontend.Dockerfile
- [x] T006 Update frontend/next.config.ts to enable standalone output mode

### Health Endpoints

- [x] T007 Add /ready endpoint to backend in backend/src/main.py with database connectivity check
- [x] T008 [P] Create frontend health endpoint in frontend/src/app/api/health/route.ts

### Helm Chart Foundation

- [x] T009 Create Chart.yaml with metadata in infra/helm/todo/Chart.yaml
- [x] T010 [P] Create _helpers.tpl with template helpers in infra/helm/todo/templates/_helpers.tpl
- [x] T011 [P] Create namespace.yaml template in infra/helm/todo/templates/namespace.yaml

**Checkpoint**: Docker images buildable, health endpoints implemented, Helm chart structure ready

---

## Phase 3: User Story 1 - Deploy Application to Local Kubernetes (Priority: P1) 🎯 MVP

**Goal**: Deploy complete Todo application (backend + frontend) to local Minikube cluster

**Independent Test**: Run `helm install todo ./infra/helm/todo` and access application via browser at http://todo.local

### Implementation for User Story 1

- [x] T012 [US1] Create values.yaml with default configuration in infra/helm/todo/values.yaml
- [x] T013 [P] [US1] Create backend-deployment.yaml template in infra/helm/todo/templates/backend-deployment.yaml
- [x] T014 [P] [US1] Create frontend-deployment.yaml template in infra/helm/todo/templates/frontend-deployment.yaml
- [x] T015 [P] [US1] Create backend-service.yaml template in infra/helm/todo/templates/backend-service.yaml
- [x] T016 [P] [US1] Create frontend-service.yaml template in infra/helm/todo/templates/frontend-service.yaml
- [x] T017 [US1] Create ingress.yaml template with path routing in infra/helm/todo/templates/ingress.yaml
- [ ] T018 [US1] Build backend Docker image and verify it runs locally
- [ ] T019 [US1] Build frontend Docker image and verify it runs locally
- [ ] T020 [US1] Deploy to Minikube and verify application is accessible

**Checkpoint**: User Story 1 complete - application deploys to Minikube and is accessible via browser

---

## Phase 4: User Story 2 - Verify Application Health (Priority: P1)

**Goal**: Kubernetes automatically monitors health and restarts unhealthy containers

**Independent Test**: Deploy application, kill backend process, observe Kubernetes restart pod automatically

### Implementation for User Story 2

- [x] T021 [US2] Configure liveness probe for backend in backend-deployment.yaml template
- [x] T022 [P] [US2] Configure readiness probe for backend in backend-deployment.yaml template
- [x] T023 [P] [US2] Configure liveness probe for frontend in frontend-deployment.yaml template
- [ ] T024 [US2] Verify health probes work by checking pod status with kubectl describe pod

**Checkpoint**: User Story 2 complete - pods restart automatically when unhealthy

---

## Phase 5: User Story 3 - Configure Application via Environment (Priority: P2)

**Goal**: Configure application using ConfigMaps and Secrets without rebuilding images

**Independent Test**: Modify ConfigMap, restart pods, verify new configuration is applied

### Implementation for User Story 3

- [x] T025 [US3] Create configmap-backend.yaml template in infra/helm/todo/templates/configmap-backend.yaml
- [x] T026 [P] [US3] Create configmap-frontend.yaml template in infra/helm/todo/templates/configmap-frontend.yaml
- [x] T027 [P] [US3] Create secret-db.yaml template in infra/helm/todo/templates/secret-db.yaml
- [x] T028 [US3] Create secrets.example.yaml with placeholder values in infra/helm/todo/secrets.example.yaml
- [x] T029 [US3] Update backend-deployment.yaml to mount ConfigMap and Secret as environment variables
- [x] T030 [US3] Update frontend-deployment.yaml to mount ConfigMap as environment variables
- [ ] T031 [US3] Verify configuration injection by checking pod environment with kubectl exec

**Checkpoint**: User Story 3 complete - configuration changes apply without image rebuilds

---

## Phase 6: User Story 4 - AI-Assisted Cluster Operations (Priority: P2)

**Goal**: Use kubectl-ai to query and manage cluster using natural language

**Independent Test**: Install kubectl-ai, run "show me all pods in todo namespace", verify correct response

### Implementation for User Story 4

- [x] T032 [US4] Add kubectl-ai installation instructions to specs/004-phase4-kubernetes/quickstart.md
- [x] T033 [P] [US4] Add example natural language queries to quickstart.md
- [x] T034 [P] [US4] Add optional kagent documentation to quickstart.md
- [ ] T035 [US4] Verify kubectl-ai works with deployed cluster

**Checkpoint**: User Story 4 complete - kubectl-ai queries work against cluster

---

## Phase 7: User Story 5 - Helm-Based Deployment Management (Priority: P2)

**Goal**: Manage deployment with Helm install, upgrade, and rollback commands

**Independent Test**: Install chart, upgrade with new replica count, rollback to previous version

### Implementation for User Story 5

- [x] T036 [US5] Add resource limits and requests to values.yaml
- [x] T037 [P] [US5] Add .helmignore file to infra/helm/todo/.helmignore
- [ ] T038 [US5] Verify helm install works with default values
- [ ] T039 [US5] Verify helm upgrade works with --set backend.replicas=2
- [ ] T040 [US5] Verify helm rollback works after upgrade

**Checkpoint**: User Story 5 complete - Helm lifecycle operations work correctly

---

## Phase 8: User Story 6 - Monitor Application Metrics (Priority: P3) (Optional)

**Goal**: View application metrics in Prometheus/Grafana dashboards

**Independent Test**: Deploy Prometheus stack, access Grafana dashboard, see metrics

### Implementation for User Story 6

- [x] T041 [US6] Add Prometheus installation instructions to quickstart.md
- [x] T042 [P] [US6] Add Grafana access instructions to quickstart.md
- [ ] T043 [US6] Optional: Add prometheus-fastapi-instrumentator to backend dependencies in backend/pyproject.toml
- [ ] T044 [US6] Optional: Integrate Prometheus metrics endpoint in backend/src/main.py
- [ ] T045 [US6] Optional: Add ServiceMonitor template in infra/helm/todo/templates/servicemonitor.yaml

**Checkpoint**: User Story 6 complete - metrics visible in dashboards (optional)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and cleanup

- [x] T046 [P] Update main README.md with Phase IV deployment instructions
- [ ] T047 [P] Validate all success criteria from spec.md
- [ ] T048 Run full quickstart.md deployment walkthrough
- [x] T049 [P] Create verification checklist in specs/004-phase4-kubernetes/checklists/deployment.md
- [ ] T050 Commit and push to 004-phase4-kubernetes branch

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Deploy) and US2 (Health) are both P1 but US2 depends on deployment from US1
  - US3, US4, US5 are P2 and can proceed in parallel after US1/US2
  - US6 is P3 (optional) and can be done last
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (Docker, Health Endpoints, Helm Base)
    ↓
Phase 3: US1 - Deploy to K8s (MVP) ← P1 CRITICAL
    ↓
Phase 4: US2 - Health Probes ← P1 (depends on US1 deployment)
    ↓ (US3, US4, US5 can run in parallel after US2)
Phase 5: US3 - ConfigMaps/Secrets ← P2
Phase 6: US4 - kubectl-ai ← P2
Phase 7: US5 - Helm Lifecycle ← P2
    ↓
Phase 8: US6 - Monitoring ← P3 (optional)
    ↓
Phase 9: Polish
```

### Within Each User Story

- Templates before deployments
- Deployments before services
- Services before ingress
- Core implementation before verification

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Templates within US1 marked [P] can be created in parallel
- ConfigMap/Secret templates in US3 marked [P] can run in parallel
- Documentation tasks in US4 marked [P] can run in parallel
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all parallel templates together:
Task: "Create backend-deployment.yaml template in infra/helm/todo/templates/backend-deployment.yaml"
Task: "Create frontend-deployment.yaml template in infra/helm/todo/templates/frontend-deployment.yaml"
Task: "Create backend-service.yaml template in infra/helm/todo/templates/backend-service.yaml"
Task: "Create frontend-service.yaml template in infra/helm/todo/templates/frontend-service.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 - Deploy to K8s
4. Complete Phase 4: User Story 2 - Health Probes
5. **STOP and VALIDATE**: Application deploys, health checks work
6. Demo if ready (MVP complete!)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test deployment → Demo (MVP!)
3. Add User Story 2 → Test health probes → Demo
4. Add User Stories 3-5 → Test each → Demo (Full P1+P2)
5. Add User Story 6 → Test monitoring → Demo (Complete with optional features)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (deployment)
   - After US1: Developer A continues with US2 (health)
3. After US2 complete:
   - Developer A: User Story 3 (ConfigMaps)
   - Developer B: User Story 4 (kubectl-ai)
   - Developer C: User Story 5 (Helm lifecycle)
4. User Story 6 (optional) after P2 stories complete

---

## Summary

| Phase | User Story | Priority | Tasks | Parallel |
|-------|------------|----------|-------|----------|
| 1 | Setup | - | 3 | 2 |
| 2 | Foundational | - | 8 | 4 |
| 3 | US1: Deploy to K8s | P1 | 9 | 4 |
| 4 | US2: Health Probes | P1 | 4 | 2 |
| 5 | US3: ConfigMaps | P2 | 7 | 2 |
| 6 | US4: kubectl-ai | P2 | 4 | 2 |
| 7 | US5: Helm Lifecycle | P2 | 5 | 1 |
| 8 | US6: Monitoring | P3 | 5 | 1 |
| 9 | Polish | - | 5 | 3 |
| **Total** | | | **50** | **21** |

**MVP Scope**: Phases 1-4 (Setup + Foundational + US1 + US2) = 24 tasks
**Full Scope**: All phases = 50 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- US6 (Monitoring) is optional per constitution
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
