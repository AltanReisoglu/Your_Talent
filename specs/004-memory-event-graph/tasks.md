# Tasks: FinWiki Memory Event Graph

**Input**: Design documents from `/specs/004-memory-event-graph/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Required by FR-010. Write deterministic model-free tests for authority ordering, expiry demotion, day-state supersession, and memory event projection.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

**Evidence**: Add or update `specs/004-memory-event-graph/evidence.md` before considering the feature complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps task to the user story in `spec.md`.
- Every task includes an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the feature validation surface and documentation shell.

- [x] T001 Create test package scaffold with repository import setup in `tests/conftest.py`
- [x] T002 Create initial evidence bundle from validation template in `specs/004-memory-event-graph/evidence.md`
- [x] T003 [P] Create Memory v2 documentation skeleton in `docs/memory_v2.md`
- [x] T004 [P] Create empty vault state directory marker in `finwiki-vault/state/.gitkeep`
- [x] T005 [P] Create memory maintenance directory marker in `finwiki-vault/wiki/maintenance/.gitkeep`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared helpers and vault files required before any user story work.

**Critical**: No user story implementation should start until this phase is complete.

- [x] T006 Add Memory v2 path constants for `state/day-state.md`, `logs/memory-events.jsonl`, and `wiki/maintenance/` in `tools/serverless/wiki_manager.py`
- [x] T007 Add safe frontmatter parse/update helpers for Memory v2 metadata in `tools/serverless/wiki_manager.py`
- [x] T008 Add authority ordering constants and freshness policy constants in `tools/serverless/wiki_manager.py`
- [x] T009 [P] Extend FinWiki page template with Memory v2 frontmatter fields in `finwiki-vault/wiki/templates/finwiki-page.md`
- [x] T010 [P] Extend source note template with source authority fields in `finwiki-vault/wiki/templates/source-note.md`
- [x] T011 [P] Create initial operational day-state file in `finwiki-vault/state/day-state.md`
- [x] T012 [P] Create initial expiry review page in `finwiki-vault/wiki/maintenance/expiry-review.md`
- [x] T013 [P] Create initial memory governance page in `finwiki-vault/wiki/maintenance/memory-governance.md`
- [x] T014 Add reusable temporary vault/test fixture helpers in `tests/conftest.py`

**Checkpoint**: Foundation ready; user story implementation can now begin.

---

## Phase 3: User Story 1 - Resolve memory authority before answers (Priority: P1) MVP

**Goal**: Deterministically rank candidate memories by authority, freshness, source, and decision scope.

**Independent Test**: Run `tests/test_memory_authority.py` and verify policy/direct-instruction behavior is deterministic without model calls.

### Tests for User Story 1

- [x] T015 [P] [US1] Add authority ordering tests for direct instruction, policy, day-state, wiki, memory, retrieval, and compressed summaries in `tests/test_memory_authority.py`
- [x] T016 [P] [US1] Add tests for missing source metadata and expired candidate demotion in `tests/test_memory_authority.py`

### Implementation for User Story 1

- [x] T017 [US1] Implement candidate normalization and authority score calculation in `tools/serverless/wiki_manager.py`
- [x] T018 [US1] Implement `resolve_memory_authority(query, candidates=None, page_paths=None)` in `tools/serverless/wiki_manager.py`
- [x] T019 [US1] Emit an `authority.decision` memory event from `resolve_memory_authority` in `tools/serverless/wiki_manager.py`
- [x] T020 [US1] Add `resolve_memory_authority` to the exported tool list/import surface in `agents/host_agent/agent.py`
- [x] T021 [US1] Update orchestrator instructions to call authority resolution for policy-sensitive or stale-prone answers in `agents/host_agent/agent.py`

**Checkpoint**: Authority resolver works independently and can be used before user answers.

---

## Phase 4: User Story 2 - Track provenance and expiry for wiki claims (Priority: P1)

**Goal**: Add durable validity metadata and stale/supersession handling for wiki pages and claims.

**Independent Test**: Run `tests/test_memory_expiry.py` and verify expired pages are demoted while historical evidence remains.

### Tests for User Story 2

- [x] T022 [P] [US2] Add tests that new `upsert_wiki_page` writes include Memory v2 frontmatter fields in `tests/test_memory_expiry.py`
- [x] T023 [P] [US2] Add tests for `mark_wiki_memory_stale` preserving history and updating review status in `tests/test_memory_expiry.py`

### Implementation for User Story 2

- [x] T024 [US2] Add Memory v2 frontmatter defaults to `upsert_wiki_page` in `tools/serverless/wiki_manager.py`
- [x] T025 [US2] Implement validity-window and expiry-status helper functions in `tools/serverless/wiki_manager.py`
- [x] T026 [US2] Implement `mark_wiki_memory_stale(page_path, reason, replacement=None, claim_id=None)` in `tools/serverless/wiki_manager.py`
- [x] T027 [US2] Integrate expiry demotion into `freshness_report` and `verify_wiki_claim` in `tools/serverless/wiki_manager.py`
- [x] T028 [US2] Ensure stale marking appends wiki log, audit log, and memory event records in `tools/serverless/wiki_manager.py`

**Checkpoint**: Wiki claims can be cited, demoted, expired, or superseded without deleting evidence.

---

## Phase 5: User Story 3 - Maintain a day-state whiteboard (Priority: P2)

**Goal**: Keep current operational state separate from long-term memory and financial facts.

**Independent Test**: Run `tests/test_day_state.py` and verify newer operational notes supersede older entries.

### Tests for User Story 3

- [x] T029 [P] [US3] Add tests for `update_day_state` creation, supersession, and event emission in `tests/test_day_state.py`
- [x] T030 [P] [US3] Add tests that day-state is included in memory config but not treated as a financial wiki source in `tests/test_day_state.py`

### Implementation for User Story 3

- [x] T031 [US3] Implement `update_day_state(summary, next_actions=None, supersedes=None, status="current")` in `tools/serverless/wiki_manager.py`
- [x] T032 [US3] Add `/finwiki-vault/state/day-state.md` to `FINWIKI_MEMORY_FILES` in `agents/memory_config.py`
- [x] T033 [US3] Update host agent prompt text to treat day-state as operational context only in `agents/host_agent/agent.py`
- [x] T034 [US3] Document day-state usage and expiry rules in `docs/memory_v2.md`

**Checkpoint**: Day-state is available to the agent without polluting durable financial knowledge.

---

## Phase 6: User Story 4 - Add an event-sourced memory graph layer (Priority: P2)

**Goal**: Record governance mutations as append-only events and project them into an inspectable graph report.

**Independent Test**: Run `tests/test_memory_event_graph.py` and verify emitted events rebuild into expected nodes and relations.

### Tests for User Story 4

- [x] T035 [P] [US4] Add tests for `emit_memory_event` JSONL append, redaction, and corrupt-line reporting in `tests/test_memory_event_graph.py`
- [x] T036 [P] [US4] Add projection tests for source, page, claim, supersedes, contradicts, and requires-review relations in `tests/test_memory_event_graph.py`

### Implementation for User Story 4

- [x] T037 [US4] Implement `emit_memory_event(event_type, target, payload=None, actor="finwiki")` in `tools/serverless/wiki_manager.py`
- [x] T038 [US4] Instrument `register_source`, `upsert_wiki_page`, `verify_wiki_claim`, and `mark_wiki_memory_stale` to emit memory events in `tools/serverless/wiki_manager.py`
- [x] T039 [US4] Implement event replay and graph projection helpers in `tools/serverless/wiki_manager.py`
- [x] T040 [US4] Implement `memory_event_graph_report(limit=50)` in `tools/serverless/wiki_manager.py`
- [x] T041 [US4] Add `memory_event_graph_report` and `emit_memory_event` to the host tool import surface in `agents/host_agent/agent.py`

**Checkpoint**: Memory governance has an append-only proof layer and a deterministic report.

---

## Phase 7: User Story 5 - Expose memory governance in Obsidian (Priority: P3)

**Goal**: Make memory health, stale pages, and governance rules visible inside the isolated Obsidian vault.

**Independent Test**: Open `finwiki-vault` in Obsidian and verify governance pages link to day-state, sources, stale pages, and maintenance actions without exposing repo files.

### Tests for User Story 5

- [x] T042 [P] [US5] Add tests that maintenance pages are generated under `finwiki-vault/wiki/maintenance/` in `tests/test_memory_event_graph.py`
- [x] T043 [P] [US5] Add tests that generated maintenance links stay inside `finwiki-vault/` in `tests/test_memory_event_graph.py`

### Implementation for User Story 5

- [x] T044 [US5] Implement expiry review page generation in `tools/serverless/wiki_manager.py`
- [x] T045 [US5] Implement memory governance page generation from event projection in `tools/serverless/wiki_manager.py`
- [x] T046 [US5] Update vault home/index links to memory governance pages in `finwiki-vault/home.md` and `finwiki-vault/wiki/home.md`
- [x] T047 [US5] Update user-facing docs for opening only `finwiki-vault` in Obsidian in `README.md`

**Checkpoint**: Memory governance is visible and navigable from Obsidian.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and evidence before implementation is considered complete.

- [x] T048 [P] Update operating procedures with Remember/Cite/Forget and Memory v2 tools in `AGENTS.md`
- [x] T049 [P] Complete Memory v2 architecture documentation in `docs/memory_v2.md`
- [x] T050 Run Python syntax validation for changed runtime files and record results in `specs/004-memory-event-graph/evidence.md`
- [x] T051 Run memory governance pytest suite and record results in `specs/004-memory-event-graph/evidence.md`
- [x] T052 Run quickstart smoke commands from `specs/004-memory-event-graph/quickstart.md` and record results in `specs/004-memory-event-graph/evidence.md`
- [x] T053 Run local secret scan for changed docs/config/examples and record results in `specs/004-memory-event-graph/evidence.md`
- [x] T054 Record skipped checks, residual risks, and ActiveGraph dependency decision in `specs/004-memory-event-graph/evidence.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **US1 Authority Resolution (Phase 3)**: Depends on Foundational.
- **US2 Provenance/Expiry (Phase 4)**: Depends on Foundational; can begin after T024 if US1 is not complete, but final answer-path behavior is strongest after US1.
- **US3 Day-State (Phase 5)**: Depends on Foundational; independent of US1/US2 except documentation consistency.
- **US4 Event Graph (Phase 6)**: Depends on Foundational and benefits from US1/US2 event sources.
- **US5 Obsidian Governance (Phase 7)**: Depends on US2 and US4 for useful maintenance content.
- **Polish (Phase 8)**: Depends on selected user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: MVP; no dependency on other stories after foundation.
- **User Story 2 (P1)**: No hard dependency on US1, but integrates with resolver once US1 exists.
- **User Story 3 (P2)**: Independent after foundation.
- **User Story 4 (P2)**: Can start after foundation; richer once US1/US2 emit events.
- **User Story 5 (P3)**: Depends on event and expiry outputs from US2/US4.

### Within Each User Story

- Tests must be written before implementation tasks in that story.
- Shared helper changes precede tool export/prompt changes.
- Tool implementation precedes host-agent tool-surface updates.
- Story checkpoint must pass before moving to lower-priority phases.

---

## Parallel Opportunities

- T003, T004, T005 can run in parallel after T001.
- T009, T010, T011, T012, T013 can run in parallel after T006-T008 are understood.
- T015 and T016 can run in parallel.
- T022 and T023 can run in parallel.
- T029 and T030 can run in parallel.
- T035 and T036 can run in parallel.
- T042 and T043 can run in parallel.
- T048 and T049 can run in parallel during polish.

---

## Parallel Example: User Story 1

```text
Task T015: Add authority ordering tests in tests/test_memory_authority.py
Task T016: Add missing source and expiry demotion tests in tests/test_memory_authority.py
```

After both tests exist, implement T017-T021 sequentially.

## Parallel Example: User Story 4

```text
Task T035: Add JSONL append/redaction/corrupt-line tests in tests/test_memory_event_graph.py
Task T036: Add graph projection relation tests in tests/test_memory_event_graph.py
```

After both tests exist, implement T037-T041 sequentially.

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1 authority resolution).
3. Stop and validate `tests/test_memory_authority.py`.
4. Use the resolver in agent answers before broad expiry/event graph work.

### Incremental Delivery

1. Add US1 authority resolver.
2. Add US2 expiry/provenance metadata.
3. Add US3 day-state.
4. Add US4 event graph proof layer.
5. Add US5 Obsidian governance pages.

### Safety Notes

- Do not make ActiveGraph a required dependency in this feature.
- Do not move financial facts into `/memories/`.
- Do not open the code repository as the user-facing Obsidian vault; use `finwiki-vault/`.
- Preserve single-writer behavior for wiki/index/log/manifest mutations.
- Preserve historical claims when marking memory stale or superseded.
