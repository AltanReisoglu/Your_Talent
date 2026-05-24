# Contract: Memory Governance Tools

These are Python local-tool contracts for `tools/serverless/wiki_manager.py`.
They are deterministic and model-free.

## `resolve_memory_authority(query, candidates=None, page_paths=None)`

Ranks memory candidates for a query.

Inputs:

- `query: str`
- `candidates: list[dict] | None`
- `page_paths: list[str] | None`

Output:

- Markdown or JSON-compatible text report containing:
  - selected candidate
  - rejected candidates
  - authority ranking reason
  - freshness/expiry status
  - whether citation, refresh, or human confirmation is required

Rules:

- Direct instruction outranks canonical policy only for the current task and only
  when it does not attempt to weaken compliance/source-quality policy.
- Canonical policy outranks writable memories.
- Expired or stale candidates cannot have `decision_scope=final`.
- Missing source metadata forces `decision_scope=hint` or `background`.

## `mark_wiki_memory_stale(page_path, reason, replacement=None, claim_id=None)`

Marks a page or claim as stale, expired, or superseded without deleting history.

Inputs:

- `page_path: str`
- `reason: str`
- `replacement: str | None`
- `claim_id: str | None`

Output:

- Markdown report with mutation summary and next action.

Side effects:

- Updates page frontmatter where safe.
- Appends to `wiki/log.md`.
- Emits audit event.
- Emits memory event.
- Adds/updates `wiki/maintenance/expiry-review.md`.

Rules:

- Must reject paths outside `finwiki-vault/wiki`.
- Must not edit `raw/`, `policies/`, `.env`, or `.git`.
- Must preserve old source references.

## `update_day_state(summary, next_actions=None, supersedes=None, status="current")`

Updates today's operational whiteboard.

Inputs:

- `summary: str`
- `next_actions: list[str] | None`
- `supersedes: list[str] | None`
- `status: str`

Output:

- Markdown report with current day-state and superseded entries.

Side effects:

- Creates or updates `finwiki-vault/state/day-state.md`.
- Emits `day_state.updated` memory event.

Rules:

- Day-state is operational context only.
- Day-state cannot be used as final authority for financial facts.

## `emit_memory_event(event_type, target, payload=None, actor="finwiki")`

Appends a structured event to the memory governance event log.

Inputs:

- `event_type: str`
- `target: str`
- `payload: dict | None`
- `actor: str`

Output:

- Event ID or JSON-compatible event summary.

Side effects:

- Appends one JSON line to `finwiki-vault/logs/memory-events.jsonl`.

Rules:

- Event IDs must be stable and monotonic enough for deterministic replay.
- Event payloads must be JSON-serializable and redacted before writing.

## `memory_event_graph_report(limit=50)`

Replays recent memory events into a lightweight graph projection.

Inputs:

- `limit: int`

Output:

- Markdown report containing nodes, relations, stale items, contradictions, and
  recent authority decisions.

Side effects:

- May regenerate `wiki/maintenance/memory-governance.md`.
- Must not mutate financial wiki pages.

Rules:

- Projection is read-only and derived from event log.
- Broken/corrupt event lines must be reported, not silently ignored.
