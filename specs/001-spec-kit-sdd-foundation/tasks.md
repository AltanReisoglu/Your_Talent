# Tasks: Spec Kit SDD Foundation

**Input**: Design documents from `specs/001-spec-kit-sdd-foundation/`

**Prerequisites**: plan.md, spec.md

**Tests**: Python syntax check, Spec Kit script help, evidence checker, .NET build

**Organization**: Tasks are grouped by user story and completed in dependency order.

## Phase 1: Setup

- [x] T001 Initialize GitHub Spec Kit with Codex integration
- [x] T002 Inspect generated `.agents/skills/` and `.specify/` files

---

## Phase 2: Foundation

- [x] T003 Replace constitution template with FinWiki-specific principles
- [x] T004 Update plan template with FinWiki constitution gates
- [x] T005 Update tasks template with evidence bundle requirement
- [x] T006 Add evidence bundle template

---

## Phase 3: User Story 1 - Start AI coding from a spec (Priority: P1)

**Goal**: Developers and AI agents can use official Spec Kit skills for code changes.

**Independent Test**: `.agents/skills/speckit-*` and `.specify/` exist.

- [x] T007 Document Spec Kit workflow in README.md
- [x] T008 Document Spec Kit artifact layout in README.md

---

## Phase 4: User Story 2 - Preserve FinWiki governance (Priority: P1)

**Goal**: FinWiki runtime, financial safety, and wiki governance are encoded in
the constitution and agent instructions.

**Independent Test**: Constitution has no placeholder tokens and AGENTS.md
references the Spec Kit workflow.

- [x] T009 Add Spec-Driven Development section to AGENTS.md
- [x] T010 Add code-change Spec Kit context to app/hooks.py

---

## Phase 5: User Story 3 - Record evidence before completion (Priority: P2)

**Goal**: Completed features can validate required artifacts and evidence.

**Independent Test**: `scripts/spec_evidence_check.py --require-evidence` passes.

- [x] T011 Add scripts/spec_evidence_check.py
- [x] T012 Create this feature's spec, plan, tasks, and evidence files

---

## Phase 6: Validation

- [x] T013 Run Python syntax check
- [x] T014 Run evidence checker
- [x] T015 Run Spec Kit prerequisite script help
- [x] T016 Run C# gateway build
- [x] T017 Run secret scan over changed workflow files

## Notes

- This feature intentionally uses official Spec Kit folders and command skills.
- Future feature branches should normally be created through Spec Kit commands.
