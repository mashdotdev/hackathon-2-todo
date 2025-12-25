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

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and dependency configuration

- [x] T001 Upgrade backend from Typer CLI to FastAPI structure in backend/src/main.py
- [x] T002 [P] Add FastAPI dependencies to backend/pyproject.toml (fastapi, uvicorn, sqlmodel, python-jose, bcrypt)
- [x] T003 [P] Create backend/.env.example with DATABASE_URL, SECRET_KEY, FRONTEND_URL
- [x] T004 [P] Initialize Next.js 16+ project in frontend/ with App Router
- [x] T005 [P] Configure Tailwind CSS in frontend/tailwind.config.ts (auto-configured by Next.js)
- [x] T006 [P] Add frontend dependencies to frontend/package.json (axios, js-cookie)
- [x] T007 [P] Create frontend/.env.example with NEXT_PUBLIC_API_URL
- [x] T008 [P] Configure backend ruff and mypy in backend/pyproject.toml
- [x] T009 [P] Configure frontend ESLint and Prettier in frontend/

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Create backend/src/core/config.py with Settings class (DATABASE_URL, SECRET_KEY, etc.)
- [x] T011 [P] Create backend/src/core/security.py with JWT utilities (create_token, verify_token)
- [x] T012 [P] Create backend/src/core/database.py with SQLModel engine and session
- [x] T013 Setup Alembic in backend/alembic/ with initial configuration
- [x] T014 Create User SQLModel in backend/src/models/user.py per data-model.md
- [x] T015 [P] Create Task SQLModel in backend/src/models/task.py per data-model.md
- [x] T016 Create Pydantic schemas in backend/src/schemas/user.py (UserCreate, UserLogin, UserResponse, AuthResponse)
- [x] T017 [P] Create Pydantic schemas in backend/src/schemas/task.py (TaskCreate, TaskUpdate, TaskResponse)
- [x] T018 [P] Create Pydantic schemas in backend/src/schemas/error.py (ErrorResponse)
- [x] T019 Generate Alembic migration for users and tasks tables
- [x] T020 Create backend/src/api/deps.py with get_db and get_current_user dependencies
- [x] T021 [P] Create frontend/src/lib/api.ts with axios client and auth interceptor
- [x] T022 [P] Create frontend/src/contexts/AuthContext.tsx with auth state management
- [x] T023 Create frontend/src/app/layout.tsx with providers and global styles
- [x] T024 Configure CORS middleware in backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin ✅

---

## Phase 3: User Story 1 - User Registration (Priority: P1) ✅ COMPLETE

**Goal**: New users can create an account with email and password

**Independent Test**: Complete registration flow, verify account created, auto-login to dashboard

### Tests for User Story 1

- [x] T025 [P] [US1] API test for auth_service.register in backend/tests/api/test_auth.py
- [x] T026 [P] [US1] Integration test for POST /api/auth/register in backend/tests/api/test_auth.py

### Implementation for User Story 1

- [x] T027 [US1] Create AuthService.register in backend/src/services/auth_service.py
- [x] T028 [US1] Implement POST /api/auth/register in backend/src/api/routes/auth.py
- [x] T029 [US1] Create registration form in frontend/src/app/register/page.tsx
- [x] T030 [US1] Create registration page in frontend/src/app/register/page.tsx
- [x] T031 [US1] Add form validation (email format, password min 8 chars)
- [x] T032 [US1] Handle registration errors (duplicate email, validation) with user feedback

**Checkpoint**: User Story 1 complete - users can register accounts ✅

---

## Phase 4: User Story 2 - User Login and Logout (Priority: P1) ✅ COMPLETE

**Goal**: Registered users can log in, stay logged in across refreshes, and log out

**Independent Test**: Login with valid credentials, verify dashboard access, logout, verify redirect

### Tests for User Story 2

- [x] T033 [P] [US2] API test for auth_service.login in backend/tests/api/test_auth.py
- [x] T034 [P] [US2] Integration test for POST /api/auth/login in backend/tests/api/test_auth.py
- [x] T035 [P] [US2] Integration test for POST /api/auth/logout in backend/tests/api/test_auth.py

### Implementation for User Story 2

- [x] T036 [US2] Create AuthService.login in backend/src/services/auth_service.py
- [x] T037 [US2] Implement logout in backend/src/api/routes/auth.py
- [x] T038 [US2] Implement POST /api/auth/login in backend/src/api/routes/auth.py
- [x] T039 [US2] Implement POST /api/auth/logout in backend/src/api/routes/auth.py
- [x] T040 [US2] Implement GET /api/auth/me in backend/src/api/routes/auth.py
- [x] T041 [US2] Create login page in frontend/src/app/login/page.tsx
- [x] T042 [US2] Add JWT token storage in frontend/src/contexts/AuthContext.tsx
- [x] T043 [US2] Add logout button and functionality to dashboard header
- [x] T044 [US2] Add auth redirect in frontend/src/app/dashboard/page.tsx

**Checkpoint**: User Story 2 complete - users can login/logout ✅

---

## Phase 5: User Story 3 - View Task Dashboard (Priority: P1) ✅ COMPLETE

**Goal**: Logged-in users see their personal task dashboard with all tasks

**Independent Test**: Login, view dashboard, verify empty state message, verify task list display

### Tests for User Story 3

- [x] T045 [P] [US3] API test for task_service.list_tasks in backend/tests/api/test_tasks.py
- [x] T046 [P] [US3] Integration test for GET /api/tasks in backend/tests/api/test_tasks.py

### Implementation for User Story 3

- [x] T047 [US3] Create TaskService.list_tasks in backend/src/services/task_service.py
- [x] T048 [US3] Implement GET /api/tasks in backend/src/api/routes/tasks.py
- [x] T049 [US3] Create TaskList component in frontend/src/components/TaskList.tsx
- [x] T050 [US3] Create TaskCard component in frontend/src/components/TaskCard.tsx
- [x] T051 [US3] Create dashboard page in frontend/src/app/dashboard/page.tsx
- [x] T052 [US3] Add empty state message "No tasks yet. Add one above!"
- [x] T053 [US3] Add status indicators (checkbox for pending, checkmark for completed)

**Checkpoint**: User Story 3 complete - users can view their task list ✅

---

## Phase 6: User Story 4 - Add New Task (Priority: P1) ✅ COMPLETE

**Goal**: Logged-in users can create tasks with title and optional description

**Independent Test**: Create task, verify it appears in list with correct data and pending status

### Tests for User Story 4

- [x] T054 [P] [US4] API test for task_service.create_task in backend/tests/api/test_tasks.py
- [x] T055 [P] [US4] Integration test for POST /api/tasks in backend/tests/api/test_tasks.py

### Implementation for User Story 4

- [x] T056 [US4] Create TaskService.create_task in backend/src/services/task_service.py
- [x] T057 [US4] Implement POST /api/tasks in backend/src/api/routes/tasks.py
- [x] T058 [US4] Create TaskForm component in frontend/src/components/TaskForm.tsx
- [x] T059 [US4] Add TaskForm to dashboard page
- [x] T060 [US4] Add title validation (required, max 200 chars) in TaskForm
- [x] T061 [US4] Add description validation (max 1000 chars) in TaskForm
- [x] T062 [US4] Update task list after successful creation

**Checkpoint**: User Story 4 complete - users can create tasks (MVP COMPLETE) ✅

---

## Phase 7: User Story 5 - Mark Task Complete/Incomplete (Priority: P2) ✅ COMPLETE

**Goal**: Users can toggle task status between complete and incomplete

**Independent Test**: Click checkbox, verify status changes, refresh page, verify persisted

### Tests for User Story 5

- [x] T063 [P] [US5] API test for task_service.toggle_complete in backend/tests/api/test_tasks.py
- [x] T064 [P] [US5] Integration test for PATCH /api/tasks/{id}/complete in backend/tests/api/test_tasks.py

### Implementation for User Story 5

- [x] T065 [US5] Create TaskService.toggle_complete in backend/src/services/task_service.py
- [x] T066 [US5] Implement PATCH /api/tasks/{id}/complete in backend/src/api/routes/tasks.py
- [x] T067 [US5] Add click handler to TaskCard checkbox in frontend/src/components/TaskCard.tsx
- [x] T068 [US5] Update TaskCard visual state on toggle (immediate feedback)
- [x] T069 [US5] Handle toggle errors with user feedback

**Checkpoint**: User Story 5 complete - users can toggle task completion ✅

---

## Phase 8: User Story 6 - Update Task (Priority: P2) ✅ COMPLETE

**Goal**: Users can edit task title and description

**Independent Test**: Click edit, modify title, save, verify updated display, refresh to confirm

### Tests for User Story 6

- [x] T070 [P] [US6] API test for task_service.update_task in backend/tests/api/test_tasks.py
- [x] T071 [P] [US6] Integration test for PUT /api/tasks/{id} in backend/tests/api/test_tasks.py

### Implementation for User Story 6

- [x] T072 [US6] Create TaskService.update_task in backend/src/services/task_service.py
- [x] T073 [US6] Implement PUT /api/tasks/{id} in backend/src/api/routes/tasks.py
- [x] T074 [US6] Add edit mode to TaskList component via TaskForm
- [x] T075 [US6] Add edit form with save/cancel buttons in TaskForm
- [x] T076 [US6] Add validation for empty title on save
- [x] T077 [US6] Handle update errors with user feedback

**Checkpoint**: User Story 6 complete - users can edit tasks ✅

---

## Phase 9: User Story 7 - Delete Task (Priority: P2) ✅ COMPLETE

**Goal**: Users can delete tasks with confirmation dialog

**Independent Test**: Click delete, confirm, verify removed from list, refresh to confirm gone

### Tests for User Story 7

- [x] T078 [P] [US7] API test for task_service.delete_task in backend/tests/api/test_tasks.py
- [x] T079 [P] [US7] Integration test for DELETE /api/tasks/{id} in backend/tests/api/test_tasks.py

### Implementation for User Story 7

- [x] T080 [US7] Create TaskService.delete_task in backend/src/services/task_service.py
- [x] T081 [US7] Implement DELETE /api/tasks/{id} in backend/src/api/routes/tasks.py
- [x] T082 [US7] Implement GET /api/tasks/{id} in backend/src/api/routes/tasks.py
- [x] T083 [US7] Add delete button to TaskCard in frontend/src/components/TaskCard.tsx
- [x] T084 [US7] Add confirmation dialog before delete
- [x] T085 [US7] Remove task from list on successful delete
- [x] T086 [US7] Handle delete errors with user feedback

**Checkpoint**: User Story 7 complete - all CRUD operations available ✅

---

## Phase 10: Polish & Cross-Cutting Concerns (Partial)

**Purpose**: Improvements that affect multiple user stories

- [x] T087 [P] Add /health endpoint in backend/src/main.py
- [x] T088 [P] Add loading states to frontend components
- [ ] T089 [P] Add error boundary in frontend/src/app/error.tsx
- [x] T090 Implement responsive design for mobile (375px+) via Tailwind
- [x] T091 Add task sorting by creation date (newest first) in backend
- [ ] T092 [P] Add frontend component tests in frontend/tests/components/
- [ ] T093 Run ruff check and mypy on backend code
- [ ] T094 Run ESLint and type check on frontend code
- [x] T095 Update backend/.env.example with all required variables
- [x] T096 Update frontend/.env.example with all required variables
- [ ] T097 Validate quickstart.md instructions work end-to-end
- [x] T098 Add session expiry handling with redirect to login

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately ✅
- **Phase 2 (Foundational)**: Depends on Setup - BLOCKS all user stories ✅
- **Phases 3-9 (User Stories)**: All depend on Foundational completion ✅
  - US1-US4 are P1 (core) - complete in order for MVP ✅
  - US5-US7 are P2 (secondary) - can be done in parallel ✅
- **Phase 10 (Polish)**: Depends on desired user stories being complete (partial)

### User Story Dependencies

| Story | Depends On | Can Parallelize With | Status |
|-------|------------|---------------------|--------|
| US1 (Register) | Foundational | - | ✅ |
| US2 (Login) | US1 (needs users) | - | ✅ |
| US3 (View) | US2 (needs auth) | - | ✅ |
| US4 (Add) | US3 (needs dashboard) | - | ✅ |
| US5 (Complete) | US4 (needs tasks) | US6, US7 | ✅ |
| US6 (Update) | US4 (needs tasks) | US5, US7 | ✅ |
| US7 (Delete) | US4 (needs tasks) | US5, US6 | ✅ |

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

### MVP First (User Stories 1-4) ✅ COMPLETE

1. Complete Phase 1: Setup (9 tasks) ✅
2. Complete Phase 2: Foundational (15 tasks) ✅
3. Complete Phase 3: US1 Registration (8 tasks) ✅
4. Complete Phase 4: US2 Login/Logout (12 tasks) ✅
5. Complete Phase 5: US3 View Dashboard (9 tasks) ✅
6. Complete Phase 6: US4 Add Task (9 tasks) ✅
7. **STOP and VALIDATE**: Full MVP working ✅
8. Demo/Deploy if ready

**MVP Total**: 62 tasks ✅

### Full Implementation ✅ COMPLETE

9. Complete Phase 7: US5 Mark Complete (7 tasks) ✅
10. Complete Phase 8: US6 Update Task (8 tasks) ✅
11. Complete Phase 9: US7 Delete Task (9 tasks) ✅
12. Complete Phase 10: Polish (12 tasks) - Partial (8/12)

**Full Total**: 98 tasks (90 completed, 8 remaining polish tasks)

---

## Summary

| Phase | User Story | Tasks | Completed | Status |
|-------|------------|-------|-----------|--------|
| 1 | Setup | 9 | 9 | ✅ |
| 2 | Foundational | 15 | 15 | ✅ |
| 3 | US1 Registration | 8 | 8 | ✅ |
| 4 | US2 Login/Logout | 12 | 12 | ✅ |
| 5 | US3 View Dashboard | 9 | 9 | ✅ |
| 6 | US4 Add Task | 9 | 9 | ✅ |
| 7 | US5 Complete Toggle | 7 | 7 | ✅ |
| 8 | US6 Update Task | 8 | 8 | ✅ |
| 9 | US7 Delete Task | 9 | 9 | ✅ |
| 10 | Polish | 12 | 8 | Partial |
| **Total** | | **98** | **90** | **92%** |

**MVP Scope**: Phases 1-6 (US1-US4) = 62 tasks ✅ COMPLETE
**Full Scope**: All user stories complete, polish tasks partial

---

## Notes

- [P] tasks can run in parallel (different files, no dependencies)
- [Story] label maps task to specific user story for traceability
- Constitution requires tests per Principle III (Test-First Development)
- Each user story is independently testable after its phase completes
- Commit after each task or logical group
- Stop at any checkpoint to validate functionality

## Implementation Notes

- Used `js-cookie` instead of `better-auth` for simpler token management
- Created `AuthContext` instead of separate auth.ts for React state integration
- API tests cover both unit and integration testing needs (32 tests passing)
- Used bcrypt directly instead of passlib due to Python 3.14 compatibility
- TaskCard component combines TaskItem functionality
- Frontend builds successfully with Next.js 16.1.1
