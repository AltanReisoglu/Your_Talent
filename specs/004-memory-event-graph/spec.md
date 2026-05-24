# Feature Specification: FinWiki Memory Event Graph

**Feature Branch**: `004-memory-event-graph`
**Created**: 2026-05-24
**Status**: Draft
**Input**: User description: "Create tasks for the memory discussions and improve our memory system."

## User Scenarios & Testing

### User Story 1 - Resolve memory authority before answers (Priority: P1)

As a FinWiki operator, I want the agent to distinguish direct instructions,
canonical policy, project memory, wiki facts, retrieval summaries, and compressed
context before using memory in an answer, so stale or low-authority memory cannot
silently override trusted sources.

**Why this priority**: This is the core reliability gap from the
Remember/Cite/Forget framework. Without authority resolution, adding more memory
increases risk.

**Independent Test**: A deterministic local test can feed conflicting candidate
memories into the resolver and verify that direct instruction and policy outrank
project memory, retrieval summaries, and compressed context.

**Acceptance Scenarios**:

1. **Given** a direct instruction conflicts with a project memory note, **When**
   the resolver ranks candidates, **Then** the direct instruction is selected and
   the lower-authority memory is marked as background only.
2. **Given** a policy file conflicts with writable user memory, **When** the
   resolver ranks candidates, **Then** the policy wins and the user memory cannot
   override it.
3. **Given** a wiki claim has no source or validity metadata, **When** it enters
   the answer path, **Then** it is treated as uncitable context unless explicitly
   confirmed by a higher-authority source.

---

### User Story 2 - Track provenance and expiry for wiki claims (Priority: P1)

As a FinWiki operator, I want durable wiki pages and claims to carry source,
authority, decision scope, and validity metadata, so the agent can cite trusted
information and forget or demote stale information.

**Why this priority**: Financial claims decay quickly. The system already has
freshness reports, but stale memory can still enter retrieval as if it were
current.

**Independent Test**: A local test can create a temporary wiki page with expired
metadata, run search/freshness/verification helpers, and verify that the page is
reported as stale and not treated as final authority.

**Acceptance Scenarios**:

1. **Given** a wiki page has `valid_until` in the past, **When** freshness or
   authority resolution runs, **Then** the page is reported as expired and
   demoted below current sourced pages.
2. **Given** a new source supersedes an old claim, **When** the old page is
   marked stale, **Then** frontmatter/log/audit records preserve the old claim
   and point to the replacement or review reason.
3. **Given** a regulation, market data, or company financial page is written,
   **When** the page is upserted, **Then** frontmatter includes authority,
   decision scope, freshness policy, and validity fields.

---

### User Story 3 - Maintain a day-state whiteboard (Priority: P2)

As a FinWiki operator, I want the agent to keep a short-lived day-state file for
today's active work, superseded decisions, and next actions, so current task
coordination does not pollute long-term memory.

**Why this priority**: Day-state is the missing layer between hot session context
and durable project memory.

**Independent Test**: A local test can update the day-state twice and verify
that newer decisions supersede older entries while preserving a small audit
record.

**Acceptance Scenarios**:

1. **Given** the user changes today's priority, **When** day-state is updated,
   **Then** the older priority is retained as superseded and the current priority
   is visible at the top.
2. **Given** the next conversation starts, **When** memory files are loaded,
   **Then** the day-state file is available as operational context without being
   treated as financial fact.

---

### User Story 4 - Add an event-sourced memory graph layer (Priority: P2)

As a FinWiki operator, I want memory and wiki mutations to emit structured
events that can be replayed into a lightweight graph projection, so source,
claim, page, contradiction, expiry, and maintenance relationships are auditable.

**Why this priority**: This applies the strongest ActiveGraph idea without
rewriting the agent runtime: the event log becomes the proof layer, while
Obsidian remains the human-readable knowledge base.

**Independent Test**: A local test can emit memory events into JSONL, rebuild a
projection from the event log, and verify expected nodes and relations exist.

**Acceptance Scenarios**:

1. **Given** a source is registered and a wiki page is updated, **When** memory
   graph events are emitted, **Then** the projection contains source, page, and
   relation records.
2. **Given** a claim is contradicted or expired, **When** the projection rebuilds,
   **Then** the graph shows the old claim, the superseding claim or issue, and
   the event IDs that caused the transition.
3. **Given** the event graph feature is enabled, **When** existing audit logging
   runs, **Then** it still writes append-only records and does not introduce
   parallel wiki writers.

---

### User Story 5 - Expose memory governance in Obsidian (Priority: P3)

As a FinWiki user, I want Obsidian pages for memory health, expiry review, and
source authority, so I can inspect and manually correct the knowledge base
without reading Python logs.

**Why this priority**: The user-facing KB is Obsidian-based. Governance should be
visible in the same place as the knowledge.

**Independent Test**: Open `finwiki-vault` in Obsidian and verify that memory
review pages link to stale pages, maintenance tasks, day-state, and source
registry.

**Acceptance Scenarios**:

1. **Given** stale pages exist, **When** maintenance pages are regenerated,
   **Then** `wiki/maintenance/expiry-review.md` lists them with reasons and next
   actions.
2. **Given** memory governance docs are added, **When** the vault graph is opened,
   **Then** governance pages link to relevant wiki categories without exposing
   code repo files.

### Edge Cases

- Memory candidates may have missing source metadata.
- Multiple memories may have the same authority level but different timestamps.
- Existing wiki pages may not yet contain Memory v2 frontmatter fields.
- Expiry should demote facts without deleting historical evidence.
- Day-state should not become a permanent source for financial facts.
- Event graph writes must not break existing JSONL audit/observation logs.
- `policies/**`, `.env`, `.git`, and raw source files remain protected surfaces.

## Requirements

### Functional Requirements

- **FR-001**: System MUST define a deterministic authority order for memory
  candidates: direct instruction, canonical policy, current day-state, recent
  project decision, sourced wiki fact, long-term behavior memory, retrieval
  summary, compressed summary.
- **FR-002**: System MUST expose a local resolver function/tool that reports the
  selected memory, rejected candidates, authority reasons, freshness status, and
  citation requirements.
- **FR-003**: System MUST add Memory v2 frontmatter fields to wiki page templates
  and new `upsert_wiki_page` writes: `authority_level`, `decision_scope`,
  `valid_from`, `valid_until`, `freshness_policy`, `supersedes`, and
  `superseded_by`.
- **FR-004**: System MUST provide a function/tool to mark a wiki page or claim as
  stale, expired, or superseded without deleting the historical record.
- **FR-005**: System MUST create and maintain `finwiki-vault/state/day-state.md`
  as short-lived operational memory.
- **FR-006**: System MUST include the day-state file in DeepAgents memory loading
  as operational context, clearly separated from financial facts.
- **FR-007**: System MUST emit structured memory events for source registration,
  claim verification, page upsert, stale marking, authority decisions, and
  maintenance issue creation.
- **FR-008**: System MUST provide a deterministic event projection report that
  summarizes nodes, relations, stale items, contradictions, and recent decisions.
- **FR-009**: System MUST generate Obsidian-readable maintenance pages for expiry
  review and memory governance inside `finwiki-vault/wiki/maintenance/`.
- **FR-010**: System MUST add tests for authority ordering, expiry demotion,
  day-state supersession, and memory event projection.
- **FR-011**: System MUST update AGENTS/README/docs to explain Remember, Cite,
  Forget and the ActiveGraph-inspired event layer.
- **FR-012**: System MUST preserve single-writer behavior for wiki/index/log/
  manifest mutations.

### Key Entities

- **MemoryCandidate**: A candidate piece of context with layer, source path,
  timestamp, validity window, authority level, and decision scope.
- **AuthorityDecision**: Resolver output explaining what can influence the final
  answer, what is only background, and why.
- **WikiClaim**: A durable claim represented in a wiki page with source,
  validity, and optional supersession metadata.
- **ValidityWindow**: `valid_from`, `valid_until`, freshness policy, and stale
  reason for a claim or page.
- **DayStateEntry**: Short-lived operational note with current status,
  supersession history, and next action.
- **MemoryEvent**: Append-only JSONL event describing a memory/wiki governance
  mutation.
- **MemoryGraphProjection**: Deterministic projection from MemoryEvent records
  into nodes and relations for reporting.
- **MaintenanceIssue**: Obsidian-visible task for stale, missing, contradictory,
  or uncited memory.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Local tests cover authority ordering, expiry demotion, day-state
  supersession, and event projection.
- **SC-002**: New wiki pages written by `upsert_wiki_page` include Memory v2
  frontmatter fields.
- **SC-003**: `freshness_report` or the new resolver reports expired pages as
  stale/demoted rather than current authority.
- **SC-004**: `finwiki-vault/state/day-state.md` exists and is included in
  DeepAgents memory configuration.
- **SC-005**: `logs/memory-events.jsonl` or an equivalent vault-local event log
  records at least source, page, claim, authority, and expiry events.
- **SC-006**: `finwiki-vault/wiki/maintenance/expiry-review.md` is generated and
  linkable from the vault.
- **SC-007**: Python syntax checks pass for changed Python modules.
- **SC-008**: Evidence bundle records checks run, skipped checks, and residual
  risks before commit/push.

## Assumptions

- Obsidian remains the user-facing knowledge center at `finwiki-vault/`.
- Python remains the agent/runtime/governance implementation layer.
- ActiveGraph is evaluated as an architecture pattern first; adding the package
  dependency is out of scope for the MVP unless a later task explicitly chooses
  it.
- Existing JSONL audit and observation logs remain supported.
- This feature does not migrate old pages automatically beyond safe template and
  helper changes; broad content migration can be a follow-up task.
