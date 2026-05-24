# Research: FinWiki Memory Event Graph

## Decision 1: Use Remember/Cite/Forget as the governance contract

**Decision**: Model memory as three required jobs:

- Remember by layer: hot session, day-state, project memory, retrieval/wiki,
  canonical policy, and direct instruction.
- Cite by provenance: every candidate that influences final answers must expose
  source path, authority level, timestamp, and freshness state.
- Forget by expiry: stale information is demoted, superseded, or marked for
  review without deleting historical evidence.

**Rationale**: FinWiki is financial-domain software. More memory without
authority and expiry increases risk. A memory item must declare what decision
level it can affect before entering the answer path.

**Alternatives considered**:

- Store more embeddings only: rejected because retrieval surfaces candidates but
  does not decide authority.
- Keep using freshness reports only: rejected because stale pages can still be
  retrieved and used.

## Decision 2: Add day-state as operational memory, not durable fact

**Decision**: Create `finwiki-vault/state/day-state.md` and load it through
DeepAgents memory config as short-lived operational context.

**Rationale**: Current system has hot conversation context and long-term memory,
but no "today's whiteboard" layer. Day-state prevents temporary priorities from
polluting project memory or financial wiki pages.

**Alternatives considered**:

- Put day-state in `memories/user_preferences.md`: rejected because day-state is
  task coordination, not preference.
- Put day-state in `wiki/`: rejected because day-state is not financial
  knowledge.

## Decision 3: Use ActiveGraph as architecture pattern before dependency

**Decision**: Implement a lightweight append-only memory event log and graph
projection in the existing codebase before adding `activegraph` as a dependency.

**Rationale**: ActiveGraph's strongest ideas are event-sourcing, behavior
reactions, replay/fork/diff, and graph projections. FinWiki can adopt those
ideas immediately with a small local layer while preserving DeepAgents as the
agent runtime and Obsidian as the user-facing KB.

**Alternatives considered**:

- Replace DeepAgents with ActiveGraph: rejected as too disruptive and not aligned
  with current runtime boundary.
- Add ActiveGraph immediately: deferred because the MVP needs governance
  semantics more than a new package.

## Decision 4: Keep Obsidian as the user-facing governance surface

**Decision**: Generate `wiki/maintenance/expiry-review.md` and
`wiki/maintenance/memory-governance.md` inside `finwiki-vault`.

**Rationale**: The user wants an Obsidian-based knowledge center. Governance
must be inspectable there, not only in logs.

**Alternatives considered**:

- Build a separate UI first: rejected because the vault is already the canonical
  human surface.

## Decision 5: Tests must be deterministic and model-free

**Decision**: Add local tests for authority ranking, expiry demotion, day-state
supersession, and event projection without LLM calls.

**Rationale**: Memory governance is infrastructure. It must be reliable even when
model providers fail or quota is exhausted.

**Alternatives considered**:

- Test only via agent invocation: rejected because model variability would hide
  deterministic failures.
