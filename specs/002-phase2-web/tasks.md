# Tasks: Phase II Full-Stack Web Application

**Input**: Design documents from `/specs/002-phase2-web/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: Tests are included per constitution (Principle III: Test-First Development).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency configuration

- [ ] T001 Upgrade backend from Typer CLI to FastAPI structure in backend/src/main.py
- [ ] T002 [P] Add FastAPI dependencies to backend/pyproject.toml (fastapi, uvicorn, sqlmodel, python-jose, passlib, bcrypt)
- [ ] T003 [P] Create backend/.env.example with DATABASE_URL, SECRET_KEY, FRONTEND_URL
- [ ] T004 [P] Initialize Next.js 16+ project in frontend/ with App Router
- [ ] T005 [P] Configure Tailwind CSS in frontend/tailwind.config.ts
- [ ] T006 [P] Add frontend dependencies to frontend/package.json (better-auth, axios)
- [ ] T007 [P] Create frontend/.env.example with NEXT_PUBLIC_API_URL
- [ ] T008 [P] Configure backend ruff and mypy in backend/pyproject.toml
- [ ] T009 [P] Configure frontend ESLint and Prettier in frontend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 Create backend/src/core/config.py with Settings class (DATABASE_URL, SECRET_KEY, etc.)
- [ ] T011 [P] Create backend/src/core/security.py with JWT utilities (create_token, verify_token)
- [ ] T012 [P] Create backend/src/core/database.py with SQLModel engine and session
- [ ] T013 Setup Alembic in backend/alembic/ with initial configuration
- [ ] T014 Create User SQLModel in backend/src/models/user.py per data-model.md
- [ ] T015 [P] Create Task SQLModel in backend/src/models/task.py per data-model.md
- [ ] T016 Create Pydantic schemas in backend/src/schemas/user.py (UserCreate, UserLogin, UserResponse, AuthResponse)
- [ ] T017 [P] Create Pydantic schemas in backend/src/schemas/task.py (TaskCreate, TaskUpdate, TaskResponse)
- [ ] T018 [P] Create Pydantic schemas in backend/src/schemas/error.py (ErrorResponse)
- [ ] T019 Generate Alembic migration for users and tasks tables
- [ ] T020 Create backend/src/api/deps.py with get_db and get_current_user dependencies
- [ ] T021 [P] Create frontend/src/lib/api.ts with axios client and auth interceptor
- [ ] T022 [P] Create frontend/src/lib/auth.ts with Better Auth integration
- [ ] T023 Create frontend/src/app/layout.tsx with providers and global styles
- [ ] T024 Configure CORS middleware in backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration (Priority: P1)

**Goal**: New users can create an account with email and password

**Independent Test**: Complete registration flow, verify account created, auto-login to dashboard

### Tests for User Story 1

- [ ] T025 [P] [US1] Unit test for auth_service.register in backend/tests/unit/test_auth_service.py
- [ ] T026 [P] [US1] Integration test for POST /api/auth/register in backend/tests/integration/test_auth_api.py

### Implementation for User Story 1

- [ ] T027 [US1] Create AuthService.register in backend/src/services/auth_service.py
- [ ] T028 [US1] Implement POST /api/auth/register in backend/src/api/routes/auth.py
- [ ] T029 [US1] Create AuthForm component in frontend/src/components/AuthForm.tsx
- [ ] T030 [US1] Create registration page in frontend/src/app/(auth)/register/page.tsx
- [ ] T031 [US1] Add form validation (email format, password min 8 chars) in AuthForm
- [ ] T032 [US1] Handle registration errors (duplicate email, validation) with user feedback

**Checkpoint**: User Story 1 complete - users can register accounts

---

## Phase 4: User Story 2 - User Login and Logout (Priority: P1)

**Goal**: Registered users can log in, stay logged in across refreshes, and log out

**Independent Test**: Login with valid credentials, verify dashboard access, logout, verify redirect

### Tests for User Story 2

- [ ] T033 [P] [US2] Unit test for auth_service.login in backend/tests/unit/test_auth_service.py
- [ ] T034 [P] [US2] Integration test for POST /api/auth/login in backend/tests/integration/test_auth_api.py
- [ ] T035 [P] [US2] Integration test for POST /api/auth/logout in backend/tests/integration/test_auth_api.py

### Implementation for User Story 2

- [ ] T036 [US2] Create AuthService.login in backend/src/services/auth_service.py
- [ ] T037 [US2] Create AuthService.logout in backend/src/services/auth_service.py
- [ ] T038 [US2] Implement POST /api/auth/login in backend/src/api/routes/auth.py
- [ ] T039 [US2] Implement POST /api/auth/logout in backend/src/api/routes/auth.py
- [ ] T040 [US2] Implement GET /api/auth/me in backend/src/api/routes/auth.py
- [ ] T041 [US2] Create login page in frontend/src/app/(auth)/login/page.tsx
- [ ] T042 [US2] Add JWT token storage and auto-refresh in frontend/src/lib/auth.ts
- [ ] T043 [US2] Add logout button and functionality to frontend layout
- [ ] T044 [US2] Add auth redirect middleware in frontend (protect /dashboard)

**Checkpoint**: User Story 2 complete - users can login/logout

---

## Phase 5: User Story 3 - View Task Dashboard (Priority: P1)

**Goal**: Logged-in users see their personal task dashboard with all tasks

**Independent Test**: Login, view dashboard, verify empty state message, verify task list display

### Tests for User Story 3

- [ ] T045 [P] [US3] Unit test for task_service.list_tasks in backend/tests/unit/test_task_service.py
- [ ] T046 [P] [US3] Integration test for GET /api/tasks in backend/tests/integration/test_tasks_api.py

### Implementation for User Story 3

- [ ] T047 [US3] Create TaskService.list_tasks in backend/src/services/task_service.py
- [ ] T048 [US3] Implement GET /api/tasks in backend/src/api/routes/tasks.py
- [ ] T049 [US3] Create TaskList component in frontend/src/components/TaskList.tsx
- [ ] T050 [US3] Create TaskItem component in frontend/src/components/TaskItem.tsx
- [ ] T051 [US3] Create dashboard page in frontend/src/app/dashboard/page.tsx
- [ ] T052 [US3] Add empty state message "No tasks yet. Create your first task!"
- [ ] T053 [US3] Add status indicators (checkbox for pending, checkmark for completed)

**Checkpoint**: User Story 3 complete - users can view their task list

---

## Phase 6: User Story 4 - Add New Task (Priority: P1)

**Goal**: Logged-in users can create tasks with title and optional description

**Independent Test**: Create task, verify it appears in list with correct data and pending status

### Tests for User Story 4

- [ ] T054 [P] [US4] Unit test for task_service.create_task in backend/tests/unit/test_task_service.py
- [ ] T055 [P] [US4] Integration test for POST /api/tasks in backend/tests/integration/test_tasks_api.py

### Implementation for User Story 4

- [ ] T056 [US4] Create TaskService.create_task in backend/src/services/task_service.py
- [ ] T057 [US4] Implement POST /api/tasks in backend/src/api/routes/tasks.py
- [ ] T058 [US4] Create TaskForm component in frontend/src/components/TaskForm.tsx
- [ ] T059 [US4] Add "Add Task" button and form to dashboard page
- [ ] T060 [US4] Add title validation (required, max 200 chars) in TaskForm
- [ ] T061 [US4] Add description validation (max 1000 chars) in TaskForm
- [ ] T062 [US4] Refresh task list after successful creation

**Checkpoint**: User Story 4 complete - users can create tasks (MVP COMPLETE)

---

## Phase 7: User Story 5 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Users can toggle task status between complete and incomplete

**Independent Test**: Click checkbox, verify status changes, refresh page, verify persisted

### Tests for User Story 5

- [ ] T063 [P] [US5] Unit test for task_service.toggle_complete in backend/tests/unit/test_task_service.py
- [ ] T064 [P] [US5] Integration test for PATCH /api/tasks/{id}/complete in backend/tests/integration/test_tasks_api.py

### Implementation for User Story 5

- [ ] T065 [US5] Create TaskService.toggle_complete in backend/src/services/task_service.py
- [ ] T066 [US5] Implement PATCH /api/tasks/{id}/complete in backend/src/api/routes/tasks.py
- [ ] T067 [US5] Add click handler to TaskItem checkbox in frontend/src/components/TaskItem.tsx
- [ ] T068 [US5] Update TaskItem visual state on toggle (immediate feedback)
- [ ] T069 [US5] Handle toggle errors with user feedback

**Checkpoint**: User Story 5 complete - users can toggle task completion

---

## Phase 8: User Story 6 - Update Task (Priority: P2)

**Goal**: Users can edit task title and description

**Independent Test**: Click edit, modify title, save, verify updated display, refresh to confirm

### Tests for User Story 6

- [ ] T070 [P] [US6] Unit test for task_service.update_task in backend/tests/unit/test_task_service.py
- [ ] T071 [P] [US6] Integration test for PUT /api/tasks/{id} in backend/tests/integration/test_tasks_api.py

### Implementation for User Story 6

- [ ] T072 [US6] Create TaskService.update_task in backend/src/services/task_service.py
- [ ] T073 [US6] Implement PUT /api/tasks/{id} in backend/src/api/routes/tasks.py
- [ ] T074 [US6] Add edit mode to TaskItem component in frontend/src/components/TaskItem.tsx
- [ ] T075 [US6] Add inline edit form with save/cancel buttons
- [ ] T076 [US6] Add validation for empty title on save
- [ ] T077 [US6] Handle update errors with user feedback

**Checkpoint**: User Story 6 complete - users can edit tasks

---

## Phase 9: User Story 7 - Delete Task (Priority: P2)

**Goal**: Users can delete tasks with confirmation dialog

**Independent Test**: Click delete, confirm, verify removed from list, refresh to confirm gone

### Tests for User Story 7

- [ ] T078 [P] [US7] Unit test for task_service.delete_task in backend/tests/unit/test_task_service.py
- [ ] T079 [P] [US7] Integration test for DELETE /api/tasks/{id} in backend/tests/integration/test_tasks_api.py

### Implementation for User Story 7

- [ ] T080 [US7] Create TaskService.delete_task in backend/src/services/task_service.py
- [ ] T081 [US7] Implement DELETE /api/tasks/{id} in backend/src/api/routes/tasks.py
- [ ] T082 [US7] Implement GET /api/tasks/{id} in backend/src/api/routes/tasks.py
- [ ] T083 [US7] Add delete button to TaskItem in frontend/src/components/TaskItem.tsx
- [ ] T084 [US7] Add confirmation dialog before delete
- [ ] T085 [US7] Remove task from list on successful delete
- [ ] T086 [US7] Handle delete errors with user feedback

**Checkpoint**: User Story 7 complete - all CRUD operations available

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T087 [P] Add /health endpoint in backend/src/api/routes/health.py
- [ ] T088 [P] Add loading states to all frontend components
- [ ] T089 [P] Add error boundary in frontend/src/app/error.tsx
- [ ] T090 Implement responsive design for mobile (375px+) across all components
- [ ] T091 Add task sorting by creation date (newest first) in backend
- [ ] T092 [P] Add frontend component tests in frontend/tests/components/
- [ ] T093 Run ruff check and mypy on backend code
- [ ] T094 Run ESLint and type check on frontend code
- [ ] T095 Update backend/.env.example with all required variables
- [ ] T096 Update frontend/.env.example with all required variables
- [ ] T097 Validate quickstart.md instructions work end-to-end
- [ ] T098 Add session expiry handling with redirect to login

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Setup - BLOCKS all user stories
- **Phases 3-9 (User Stories)**: All depend on Foundational completion
  - US1-US4 are P1 (core) - complete in order for MVP
  - US5-US7 are P2 (secondary) - can be done in parallel
- **Phase 10 (Polish)**: Depends on desired user stories being complete

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|------------|---------------------|
| US1 (Register) | Foundational | - |
| US2 (Login) | US1 (needs users) | - |
| US3 (View) | US2 (needs auth) | - |
| US4 (Add) | US3 (needs dashboard) | - |
| US5 (Complete) | US4 (needs tasks) | US6, US7 |
| US6 (Update) | US4 (needs tasks) | US5, US7 |
| US7 (Delete) | US4 (needs tasks) | US5, US6 |

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Backend before frontend
3. Service before routes
4. Core implementation before error handling

### Parallel Opportunities

**Setup Phase (9 tasks, 7 parallelizable)**:
```
T002, T003, T004, T005, T006, T007, T008, T009 can run in parallel
```

**Foundational Phase (15 tasks, 9 parallelizable)**:
```
T011, T012 can run in parallel
T014, T015 can run in parallel
T016, T017, T018 can run in parallel
T021, T022 can run in parallel
```

**User Stories (once at US4)**:
```
US5, US6, US7 can all be developed in parallel
```

---

## Implementation Strategy

### MVP First (User Stories 1-4)

1. Complete Phase 1: Setup (9 tasks)
2. Complete Phase 2: Foundational (15 tasks)
3. Complete Phase 3: US1 Registration (8 tasks)
4. Complete Phase 4: US2 Login/Logout (12 tasks)
5. Complete Phase 5: US3 View Dashboard (9 tasks)
6. Complete Phase 6: US4 Add Task (9 tasks)
7. **STOP and VALIDATE**: Full MVP working
8. Demo/Deploy if ready

**MVP Total**: 62 tasks

### Full Implementation

9. Complete Phase 7: US5 Mark Complete (7 tasks)
10. Complete Phase 8: US6 Update Task (8 tasks)
11. Complete Phase 9: US7 Delete Task (9 tasks)
12. Complete Phase 10: Polish (12 tasks)

**Full Total**: 98 tasks

---

## Summary

| Phase | User Story | Tasks | Parallelizable |
|-------|------------|-------|----------------|
| 1 | Setup | 9 | 7 |
| 2 | Foundational | 15 | 9 |
| 3 | US1 Registration | 8 | 2 |
| 4 | US2 Login/Logout | 12 | 3 |
| 5 | US3 View Dashboard | 9 | 2 |
| 6 | US4 Add Task | 9 | 2 |
| 7 | US5 Complete Toggle | 7 | 2 |
| 8 | US6 Update Task | 8 | 2 |
| 9 | US7 Delete Task | 9 | 2 |
| 10 | Polish | 12 | 5 |
| **Total** | | **98** | **36** |

**MVP Scope**: Phases 1-6 (US1-US4) = 62 tasks
**Parallel Opportunities**: 36 tasks can run in parallel (37%)

---

## Notes

- [P] tasks can run in parallel (different files, no dependencies)
- [Story] label maps task to specific user story for traceability
- Constitution requires tests per Principle III (Test-First Development)
- Each user story is independently testable after its phase completes
- Commit after each task or logical group
- Stop at any checkpoint to validate functionality
