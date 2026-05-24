# Tasks: Obsidian-Integrated Spec Workspace

**Input**: Design documents from `specs/002-obsidian-workspace/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/`

**Tests**: No TDD test files are required by the spec. Validation is handled through Markdown/link review, Spec Kit evidence checks, and deterministic script checks.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently.

**Evidence**: Add or update `specs/002-obsidian-workspace/evidence.md` before considering the feature complete. Record commands/checks run, checks intentionally skipped, and residual risk.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on incomplete tasks.
- **[Story]**: Maps task to a user story from `spec.md`.
- Every task includes an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the Obsidian-facing project navigation surface without moving canonical Spec Kit files.

- [x] T001 Create the Obsidian project navigation directory in `wiki/project/.gitkeep`
- [x] T002 Create feature summary directory in `wiki/project/features/.gitkeep`
- [x] T003 Create methodology directory in `wiki/project/methodology/.gitkeep`
- [x] T004 Create evidence navigation directory in `wiki/project/evidence/.gitkeep`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared frontmatter, status, and generation rules used by all Obsidian-facing pages.

**Critical**: Complete this phase before user story work so all pages follow the same metadata and link conventions.

- [x] T005 Document Obsidian page conventions and frontmatter rules in `docs/obsidian_workspace.md`
- [x] T006 Add Obsidian workspace conventions to the local wiki contract in `wiki.config.md`
- [x] T007 Add a generated-file policy note for project navigation pages in `docs/obsidian_workspace.md`
- [x] T008 Create an index-generation helper skeleton in `scripts/update_obsidian_project_index.py`
- [x] T009 Add feature scanning logic for `specs/*/{spec.md,plan.md,tasks.md,evidence.md}` in `scripts/update_obsidian_project_index.py`
- [x] T010 Add safe Markdown frontmatter rendering helpers in `scripts/update_obsidian_project_index.py`

**Checkpoint**: Foundation ready. Obsidian pages can now be created with consistent metadata and links.

---

## Phase 3: User Story 1 - Navigate AI Coding Intent in Obsidian (Priority: P1) - MVP

**Goal**: A developer can open the repository root as an Obsidian vault and navigate from one project page to specs, plans, tasks, evidence, wiki pages, and architecture notes.

**Independent Test**: Open `wiki/project/index.md` in Obsidian or a Markdown viewer and follow links to `specs/002-obsidian-workspace/spec.md`, `specs/002-obsidian-workspace/plan.md`, `specs/002-obsidian-workspace/tasks.md`, and architecture docs.

### Implementation for User Story 1

- [x] T011 [US1] Create main project navigation page with frontmatter and primary surfaces in `wiki/project/index.md`
- [x] T012 [US1] Create Spec Kit feature index page listing all current feature directories in `wiki/project/specs.md`
- [x] T013 [US1] Create architecture navigation page linking README, AGENTS, constitution, and architecture docs in `wiki/project/architecture.md`
- [x] T014 [US1] Create feature summary page for `001-spec-kit-sdd-foundation` in `wiki/project/features/001-spec-kit-sdd-foundation.md`
- [x] T015 [US1] Create feature summary page for `002-obsidian-workspace` in `wiki/project/features/002-obsidian-workspace.md`
- [x] T016 [US1] Create feature summary page for `003-finwiki-web-app` in `wiki/project/features/003-finwiki-web-app.md`
- [x] T017 [US1] Add generated project index rendering for `wiki/project/specs.md` in `scripts/update_obsidian_project_index.py`
- [x] T018 [US1] Add generated feature summary rendering for `wiki/project/features/*.md` in `scripts/update_obsidian_project_index.py`

**Checkpoint**: User Story 1 is complete when a developer can navigate the project from `wiki/project/index.md` without terminal search.

---

## Phase 4: User Story 2 - Keep Spec Kit as Execution Source of Truth (Priority: P1)

**Goal**: Obsidian pages summarize and link to canonical Spec Kit artifacts without replacing, moving, or duplicating `.specify/` or `specs/`.

**Independent Test**: Confirm all Obsidian-facing feature pages link back to canonical `spec.md`, `plan.md`, `tasks.md`, and `evidence.md` paths under `specs/`.

### Implementation for User Story 2

- [x] T019 [US2] Add canonical artifact warnings to `wiki/project/specs.md`
- [x] T020 [US2] Add canonical artifact links to `wiki/project/features/001-spec-kit-sdd-foundation.md`
- [x] T021 [US2] Add canonical artifact links to `wiki/project/features/002-obsidian-workspace.md`
- [x] T022 [US2] Add canonical artifact links to `wiki/project/features/003-finwiki-web-app.md`
- [x] T023 [US2] Update `README.md` with a short Obsidian workspace section pointing to `wiki/project/index.md`
- [x] T024 [US2] Update `AGENTS.md` with the rule that Obsidian project pages must not replace canonical Spec Kit artifacts
- [x] T025 [US2] Add non-moving/non-duplicating behavior checks to `scripts/update_obsidian_project_index.py`

**Checkpoint**: User Story 2 is complete when Spec Kit remains canonical and Obsidian pages only provide navigation or summaries.

---

## Phase 5: User Story 3 - Preserve Project Knowledge as Infrastructure (Priority: P2)

**Goal**: Decisions, evidence, methodology, and related FinWiki concepts are discoverable as durable project knowledge.

**Independent Test**: A future agent or developer can answer why a feature exists by reading Obsidian-linked spec, evidence, methodology, and architecture pages.

### Implementation for User Story 3

- [x] T026 [P] [US3] Create evidence index page with frontmatter and feature evidence links in `wiki/project/evidence/index.md`
- [x] T027 [P] [US3] Create Spec Kit methodology page explaining the local AI coding workflow in `wiki/project/methodology/spec-kit-workflow.md`
- [x] T028 [P] [US3] Create FinWiki environment thesis page linking wiki, raw, memory, policy, hooks, and specs in `wiki/project/methodology/finwiki-environment.md`
- [x] T029 [US3] Add residual-risk extraction from feature evidence files to `scripts/update_obsidian_project_index.py`
- [x] T030 [US3] Add evidence completeness status rendering to `wiki/project/evidence/index.md`
- [x] T031 [US3] Link relevant FinWiki concept pages from feature summaries in `wiki/project/features/002-obsidian-workspace.md`
- [x] T032 [US3] Link the full project report from project navigation in `wiki/project/index.md`

**Checkpoint**: User Story 3 is complete when evidence, decisions, methodology, and reports are visible as graph nodes.

---

## Phase 6: User Story 4 - Avoid Tool or Plugin Lock-In (Priority: P3)

**Goal**: The Obsidian integration remains useful as plain Markdown and does not require Dataview, Canvas, or any SaaS/plugin dependency.

**Independent Test**: Browse `wiki/project/index.md`, `wiki/project/specs.md`, and feature summaries in a plain Markdown viewer and run CLI validation without Obsidian installed.

### Implementation for User Story 4

- [x] T033 [P] [US4] Add plugin-optional guidance to `docs/obsidian_workspace.md`
- [x] T034 [P] [US4] Add plain Markdown navigation fallback notes to `wiki/project/index.md`
- [x] T035 [US4] Add optional Dataview snippets as fenced examples only in `docs/obsidian_workspace.md`
- [x] T036 [US4] Add CLI-only validation instructions to `docs/obsidian_workspace.md`
- [x] T037 [US4] Ensure `scripts/update_obsidian_project_index.py` uses only Python standard library

**Checkpoint**: User Story 4 is complete when the workflow works without Obsidian plugins or new runtime dependencies.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate links, evidence, and documentation across all stories.

- [x] T038 Run `scripts/update_obsidian_project_index.py` and verify generated pages in `wiki/project/`
- [x] T039 Run Python syntax check for `scripts/update_obsidian_project_index.py`
- [x] T040 Run Spec Kit evidence check for `specs/002-obsidian-workspace/evidence.md`
- [x] T041 Run Markdown link review for `wiki/project/index.md`, `wiki/project/specs.md`, and `wiki/project/features/*.md`
- [x] T042 Run secret scan over `wiki/project/`, `docs/obsidian_workspace.md`, and `scripts/update_obsidian_project_index.py`
- [x] T043 Complete `specs/002-obsidian-workspace/evidence.md` with checks run, checks not run, changed artifacts, and residual risks

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1.
- **User Story 1**: Depends on Phase 2. MVP scope.
- **User Story 2**: Depends on Phase 2 and can proceed after US1 page targets exist.
- **User Story 3**: Depends on Phase 2; evidence graph links are more useful after US1 and US2.
- **User Story 4**: Depends on Phase 2; can proceed after core docs/pages exist.
- **Polish**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: MVP. Creates the navigable Obsidian project surface.
- **US2 (P1)**: Protects Spec Kit canonical ownership. Should be completed before treating the integration as safe.
- **US3 (P2)**: Adds evidence/methodology as reusable project knowledge.
- **US4 (P3)**: Hardens against plugin lock-in.

### Within Each User Story

- Create or update documentation/page files before adding script-generated regeneration.
- Keep canonical Spec Kit files under `specs/`.
- Do not move `.specify/`, `raw/`, `policies/`, or existing wiki pages.
- Validate each story independently before moving to polish.

## Parallel Opportunities

- T026, T027, and T028 can run in parallel because they create different pages.
- T033 and T034 can run in parallel because they update different files.
- Feature summary page tasks can be parallelized only if each worker owns a different file under `wiki/project/features/`.
- Do not parallelize edits to `wiki/project/specs.md`, `wiki/project/index.md`, or `scripts/update_obsidian_project_index.py`.

## Parallel Example: User Story 3

```bash
Task: "Create evidence index page with frontmatter and feature evidence links in wiki/project/evidence/index.md"
Task: "Create Spec Kit methodology page explaining the local AI coding workflow in wiki/project/methodology/spec-kit-workflow.md"
Task: "Create FinWiki environment thesis page linking wiki, raw, memory, policy, hooks, and specs in wiki/project/methodology/finwiki-environment.md"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1.
2. Complete Phase 2.
3. Complete User Story 1.
4. Stop and validate navigation from `wiki/project/index.md`.

### Safe Incremental Delivery

1. Deliver US1 so the repo becomes navigable in Obsidian.
2. Deliver US2 so Spec Kit remains canonical and protected.
3. Deliver US3 so evidence and methodology become durable graph nodes.
4. Deliver US4 so the workflow remains Markdown-first and plugin-optional.
5. Complete Phase 7 evidence and validation.

### Notes

- Every task uses an exact file path.
- User-story tasks carry `[US#]` labels.
- `[P]` tasks touch different files and can be parallelized.
- Generated navigation must never replace canonical Spec Kit artifacts.
- Produce `evidence.md` before commit or push.
