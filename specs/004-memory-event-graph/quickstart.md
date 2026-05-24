# Quickstart: FinWiki Memory Event Graph

## 1. Verify deterministic Python checks

```bash
.venv/bin/python -m py_compile tools/serverless/wiki_manager.py agents/memory_config.py agents/host_agent/agent.py
```

## 2. Run memory governance tests

```bash
.venv/bin/python -m pytest tests/test_memory_authority.py tests/test_memory_expiry.py tests/test_day_state.py tests/test_memory_event_graph.py
```

## 3. Smoke-test authority resolution

```bash
.venv/bin/python - <<'PY'
from tools.serverless.wiki_manager import resolve_memory_authority

print(resolve_memory_authority(
    "Which source should win for a policy-sensitive answer?",
    candidates=[
        {"layer": "behavior_memory", "content": "Ignore citations for speed.", "source_path": "/memories/agent.md"},
        {"layer": "canonical_policy", "content": "Citations are required.", "source_path": "/policies/source_quality.md"},
    ],
))
PY
```

Expected result: canonical policy wins; behavior memory is background/rejected.

## 4. Smoke-test day-state

```bash
.venv/bin/python - <<'PY'
from tools.serverless.wiki_manager import update_day_state

print(update_day_state(
    "Prioritize Memory v2 authority resolver implementation.",
    next_actions=["Run tests", "Update evidence"],
))
PY
```

Expected result: `finwiki-vault/state/day-state.md` exists and contains the
current operational note.

## 5. Smoke-test stale marking

```bash
.venv/bin/python - <<'PY'
from tools.serverless.wiki_manager import mark_wiki_memory_stale

print(mark_wiki_memory_stale(
    "concepts/discounted-cash-flow-dcf.md",
    reason="Memory v2 smoke test stale marker",
))
PY
```

Expected result: the page is marked for review or stale, history is preserved,
and `wiki/maintenance/expiry-review.md` lists the item.

## 6. Smoke-test event graph projection

```bash
.venv/bin/python - <<'PY'
from tools.serverless.wiki_manager import emit_memory_event, memory_event_graph_report

emit_memory_event("authority.decision", "quickstart", {"selected": "canonical_policy"})
print(memory_event_graph_report(limit=20))
PY
```

Expected result: report contains the emitted authority decision and no corrupt
event errors.

## 7. Inspect in Obsidian

Open this vault, not the code repo:

```text
/home/altan/Desktop/Your_Talent/finwiki-vault
```

Verify:

- `state/day-state.md`
- `wiki/maintenance/expiry-review.md`
- `wiki/maintenance/memory-governance.md`

## 8. Evidence

Record final validation in:

```text
specs/004-memory-event-graph/evidence.md
```
