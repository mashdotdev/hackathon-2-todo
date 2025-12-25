# Tasks: Phase I Console Todo Application

**Input**: Design documents from `/specs/001-phase1-console/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Test tasks are included as Phase I constitution requires Test-First Development (Principle III).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

## Path Conventions

- **Backend folder**: `backend/src/`, `backend/tests/` (Phase II ready structure)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Python project with UV and pyproject.toml in backend/
- [x] T002 Create project directory structure: backend/src/, backend/src/models/, backend/src/services/, backend/src/cli/, backend/tests/, backend/tests/unit/, backend/tests/integration/
- [x] T003 [P] Create backend/src/__init__.py with package metadata
- [x] T004 [P] Create backend/src/models/__init__.py
- [x] T005 [P] Create backend/src/services/__init__.py
- [x] T006 [P] Create backend/src/cli/__init__.py
- [x] T007 [P] Create backend/tests/__init__.py
- [x] T008 [P] Create backend/tests/unit/__init__.py
- [x] T009 [P] Create backend/tests/integration/__init__.py
- [x] T010 Install dependencies: typer>=0.9.0, rich>=13.0.0
- [x] T011 Install dev dependencies: pytest>=8.0.0, pytest-cov>=4.0.0, ruff>=0.1.0, mypy>=1.0.0
- [x] T012 [P] Configure ruff in pyproject.toml (linting and formatting)
- [x] T013 [P] Configure mypy in pyproject.toml (strict mode)
- [x] T014 [P] Configure pytest in pyproject.toml (test paths and coverage)

**Checkpoint**: Project structure ready, all tools configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and services that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T015 Create TaskStatus enum (PENDING, COMPLETED) in backend/src/models/task.py
- [x] T016 Create Task dataclass with all fields (id, title, description, status, created_at, updated_at) in backend/src/models/task.py
- [x] T017 Implement Task validation in __post_init__ (title 1-200 chars, description 0-1000 chars) in backend/src/models/task.py
- [x] T018 Export Task and TaskStatus from backend/src/models/__init__.py
- [x] T019 Create in-memory storage dict (_tasks: dict[str, Task]) in backend/src/services/task_service.py
- [x] T020 Implement clear_tasks() helper for testing in backend/src/services/task_service.py
- [x] T021 Create Typer app instance in backend/src/main.py
- [x] T022 Create CLI app with Rich console in backend/src/cli/commands.py
- [x] T023 Wire CLI commands to main app in backend/src/main.py
- [x] T024 Create backend/tests/conftest.py with shared fixtures (clear_tasks, sample_task, cli_runner)

**Checkpoint**: Foundation ready - Task model, storage, and CLI framework in place

---

## Phase 3: User Story 1 - Add a New Task (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks with title and optional description

**Independent Test**: Run `todo add "Test task"` and verify task appears with unique ID

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T025 [P] [US1] Unit test: Task creation with valid title in backend/tests/unit/test_task.py
- [ ] T026 [P] [US1] Unit test: Task creation with title and description in backend/tests/unit/test_task.py
- [ ] T027 [P] [US1] Unit test: Task creation fails with empty title in backend/tests/unit/test_task.py
- [ ] T028 [P] [US1] Unit test: Task creation fails with title > 200 chars in backend/tests/unit/test_task.py
- [ ] T029 [P] [US1] Unit test: Task creation fails with description > 1000 chars in backend/tests/unit/test_task.py
- [ ] T030 [P] [US1] Unit test: Task gets unique 8-char ID in backend/tests/unit/test_task.py
- [ ] T031 [P] [US1] Unit test: Task gets created_at and updated_at timestamps in backend/tests/unit/test_task.py
- [ ] T032 [P] [US1] Service test: add_task() stores task in backend/tests/unit/test_task_service.py
- [ ] T033 [P] [US1] Service test: add_task() returns task with ID in backend/tests/unit/test_task_service.py
- [ ] T034 [P] [US1] Integration test: CLI add command creates task in backend/tests/integration/test_cli.py
- [ ] T035 [P] [US1] Integration test: CLI add with --description flag in backend/tests/integration/test_cli.py

### Implementation for User Story 1

- [ ] T036 [US1] Implement add_task(title, description) in backend/src/services/task_service.py
- [ ] T037 [US1] Implement CLI add command with title argument in backend/src/cli/commands.py
- [ ] T038 [US1] Add --description option to add command in backend/src/cli/commands.py
- [ ] T039 [US1] Display success message with task ID after add in backend/src/cli/commands.py
- [ ] T040 [US1] Handle validation errors with user-friendly messages in backend/src/cli/commands.py

**Checkpoint**: User can add tasks via `todo add "Title"` - MVP functional

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can see all tasks in a formatted table with status indicators

**Independent Test**: Add multiple tasks, run `todo list` and verify table displays all tasks

### Tests for User Story 2

- [ ] T041 [P] [US2] Service test: get_all_tasks() returns all tasks in backend/tests/unit/test_task_service.py
- [ ] T042 [P] [US2] Service test: get_all_tasks() returns empty list when no tasks in backend/tests/unit/test_task_service.py
- [ ] T043 [P] [US2] Service test: filter_by_status() returns pending only in backend/tests/unit/test_task_service.py
- [ ] T044 [P] [US2] Service test: filter_by_status() returns completed only in backend/tests/unit/test_task_service.py
- [ ] T045 [P] [US2] Service test: get_statistics() returns correct counts in backend/tests/unit/test_task_service.py
- [ ] T046 [P] [US2] Integration test: CLI list shows all tasks in backend/tests/integration/test_cli.py
- [ ] T047 [P] [US2] Integration test: CLI list --status pending filters in backend/tests/integration/test_cli.py
- [ ] T048 [P] [US2] Integration test: CLI list shows "No tasks found" when empty in backend/tests/integration/test_cli.py

### Implementation for User Story 2

- [ ] T049 [US2] Implement get_all_tasks() in backend/src/services/task_service.py
- [ ] T050 [US2] Implement filter_by_status(status) in backend/src/services/task_service.py
- [ ] T051 [US2] Implement get_statistics() returning (total, pending, completed) in backend/src/services/task_service.py
- [ ] T052 [US2] Create Rich table formatter for task display in backend/src/cli/commands.py
- [ ] T053 [US2] Implement CLI list command with Rich table in backend/src/cli/commands.py
- [ ] T054 [US2] Add --status option (all/pending/completed) to list command in backend/src/cli/commands.py
- [ ] T055 [US2] Display statistics (total/pending/completed) below table in backend/src/cli/commands.py
- [ ] T056 [US2] Display "No tasks found" message when list is empty in backend/src/cli/commands.py

**Checkpoint**: User can view tasks via `todo list` with filtering - Core MVP complete

---

## Phase 5: User Story 3 - Mark Task as Complete (Priority: P2)

**Goal**: Users can toggle task status between pending and completed

**Independent Test**: Create task, run `todo complete <id>`, verify status changes

### Tests for User Story 3

- [ ] T057 [P] [US3] Service test: get_task() returns task by ID in backend/tests/unit/test_task_service.py
- [ ] T058 [P] [US3] Service test: get_task() returns None for invalid ID in backend/tests/unit/test_task_service.py
- [ ] T059 [P] [US3] Service test: toggle_complete() changes pending to completed in backend/tests/unit/test_task_service.py
- [ ] T060 [P] [US3] Service test: toggle_complete() changes completed to pending in backend/tests/unit/test_task_service.py
- [ ] T061 [P] [US3] Service test: toggle_complete() updates updated_at timestamp in backend/tests/unit/test_task_service.py
- [ ] T062 [P] [US3] Integration test: CLI complete command toggles status in backend/tests/integration/test_cli.py
- [ ] T063 [P] [US3] Integration test: CLI complete with invalid ID shows error in backend/tests/integration/test_cli.py

### Implementation for User Story 3

- [ ] T064 [US3] Implement get_task(task_id) in backend/src/services/task_service.py
- [ ] T065 [US3] Implement toggle_complete(task_id) in backend/src/services/task_service.py
- [ ] T066 [US3] Implement CLI complete command with task_id argument in backend/src/cli/commands.py
- [ ] T067 [US3] Display confirmation with new status after toggle in backend/src/cli/commands.py
- [ ] T068 [US3] Handle "task not found" error with user-friendly message in backend/src/cli/commands.py

**Checkpoint**: User can mark tasks complete/incomplete via `todo complete <id>`

---

## Phase 6: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Users can modify task title and/or description

**Independent Test**: Create task, run `todo update <id> --title "New"`, verify change persists

### Tests for User Story 4

- [ ] T069 [P] [US4] Service test: update_task() updates title only in backend/tests/unit/test_task_service.py
- [ ] T070 [P] [US4] Service test: update_task() updates description only in backend/tests/unit/test_task_service.py
- [ ] T071 [P] [US4] Service test: update_task() updates both fields in backend/tests/unit/test_task_service.py
- [ ] T072 [P] [US4] Service test: update_task() validates new title in backend/tests/unit/test_task_service.py
- [ ] T073 [P] [US4] Service test: update_task() updates updated_at timestamp in backend/tests/unit/test_task_service.py
- [ ] T074 [P] [US4] Integration test: CLI update --title works in backend/tests/integration/test_cli.py
- [ ] T075 [P] [US4] Integration test: CLI update --description works in backend/tests/integration/test_cli.py
- [ ] T076 [P] [US4] Integration test: CLI update with invalid ID shows error in backend/tests/integration/test_cli.py

### Implementation for User Story 4

- [ ] T077 [US4] Implement update_task(task_id, title, description) in backend/src/services/task_service.py
- [ ] T078 [US4] Implement CLI update command with task_id argument in backend/src/cli/commands.py
- [ ] T079 [US4] Add --title option to update command in backend/src/cli/commands.py
- [ ] T080 [US4] Add --description option to update command in backend/src/cli/commands.py
- [ ] T081 [US4] Display confirmation with updated values in backend/src/cli/commands.py
- [ ] T082 [US4] Handle validation errors (empty title, too long) in backend/src/cli/commands.py

**Checkpoint**: User can update tasks via `todo update <id> --title/--description`

---

## Phase 7: User Story 5 - Delete a Task (Priority: P3)

**Goal**: Users can permanently remove tasks with confirmation

**Independent Test**: Create task, run `todo delete <id>`, confirm deletion, verify task gone

### Tests for User Story 5

- [ ] T083 [P] [US5] Service test: delete_task() removes task from storage in backend/tests/unit/test_task_service.py
- [ ] T084 [P] [US5] Service test: delete_task() returns True on success in backend/tests/unit/test_task_service.py
- [ ] T085 [P] [US5] Service test: delete_task() returns False for invalid ID in backend/tests/unit/test_task_service.py
- [ ] T086 [P] [US5] Integration test: CLI delete with confirmation removes task in backend/tests/integration/test_cli.py
- [ ] T087 [P] [US5] Integration test: CLI delete --force skips confirmation in backend/tests/integration/test_cli.py
- [ ] T088 [P] [US5] Integration test: CLI delete with 'n' confirmation keeps task in backend/tests/integration/test_cli.py
- [ ] T089 [P] [US5] Integration test: CLI delete with invalid ID shows error in backend/tests/integration/test_cli.py

### Implementation for User Story 5

- [ ] T090 [US5] Implement delete_task(task_id) in backend/src/services/task_service.py
- [ ] T091 [US5] Implement CLI delete command with task_id argument in backend/src/cli/commands.py
- [ ] T092 [US5] Add confirmation prompt (y/n) before delete in backend/src/cli/commands.py
- [ ] T093 [US5] Add --force flag to skip confirmation in backend/src/cli/commands.py
- [ ] T094 [US5] Display success message after deletion in backend/src/cli/commands.py
- [ ] T095 [US5] Handle "task not found" error with user-friendly message in backend/src/cli/commands.py

**Checkpoint**: User can delete tasks via `todo delete <id>` with confirmation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Quality improvements across all user stories

- [ ] T096 [P] Verify all tests pass with `cd backend && uv run pytest --cov=src`
- [ ] T097 [P] Run ruff format on backend/src/ and backend/tests/
- [ ] T098 [P] Run ruff check and fix any linting issues
- [ ] T099 [P] Run mypy backend/src/ and fix any type errors
- [ ] T100 Validate quickstart.md commands work as documented
- [ ] T101 Final code review for consistency and quality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - US1 (Add) and US2 (View) are P1 priority - complete first for MVP
  - US3 (Complete) and US4 (Update) are P2 priority - complete after MVP
  - US5 (Delete) is P3 priority - complete last
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (Add)**: Requires foundational Task model and storage only
- **User Story 2 (View)**: Requires add functionality to have tasks to view
- **User Story 3 (Complete)**: Requires add + view to verify changes
- **User Story 4 (Update)**: Requires add + view to verify changes
- **User Story 5 (Delete)**: Requires add + view to verify removal

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Service layer before CLI layer
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All `__init__.py` files in Setup (T003-T009) can run in parallel
- All config tasks in Setup (T012-T014) can run in parallel
- All tests within a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel after foundation

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test: Task creation with valid title in backend/tests/unit/test_task.py"
Task: "Unit test: Task creation with title and description in backend/tests/unit/test_task.py"
Task: "Unit test: Task creation fails with empty title in backend/tests/unit/test_task.py"
Task: "Service test: add_task() stores task in backend/tests/unit/test_task_service.py"
Task: "Integration test: CLI add command creates task in backend/tests/integration/test_cli.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add)
4. Complete Phase 4: User Story 2 (View)
5. **STOP and VALIDATE**: Test `add` and `list` commands work
6. Demo MVP: Users can add and view tasks

### Full Feature Delivery

1. Complete MVP (Stories 1 + 2)
2. Add User Story 3 (Complete) → Test toggle works
3. Add User Story 4 (Update) → Test modifications work
4. Add User Story 5 (Delete) → Test removal works
5. Complete Polish phase
6. Run full test suite with coverage

### Using Phase I Skills

```bash
# Use custom skills to accelerate implementation:
/todo.setup    # Runs Setup phase (T001-T014)
/todo.crud     # Generates Foundation + service code
/todo.test     # Generates all test files
```

---

## Summary

| Phase | Purpose | Task Count | Parallelizable |
|-------|---------|------------|----------------|
| 1. Setup | Project structure | 14 | 8 |
| 2. Foundational | Core models/storage | 10 | 0 |
| 3. US1 Add | Create tasks | 16 | 11 |
| 4. US2 View | List tasks | 16 | 8 |
| 5. US3 Complete | Toggle status | 12 | 7 |
| 6. US4 Update | Modify tasks | 14 | 8 |
| 7. US5 Delete | Remove tasks | 13 | 7 |
| 8. Polish | Quality & validation | 6 | 4 |
| **Total** | | **101** | **53** |

**MVP Scope**: Phases 1-4 (56 tasks) → Users can add and view tasks
**Full Scope**: All 8 phases (101 tasks) → Complete CRUD functionality

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable after completion
- Commit after each task or logical group
- Use `/todo.*` skills to accelerate common patterns
