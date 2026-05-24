# Evidence: FinWiki Memory Event Graph

**Feature**: `004-memory-event-graph`
**Date**: 2026-05-24

## Checks Run

- `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`
  - Result: Passed.
  - Feature dir: `specs/004-memory-event-graph`
  - Available docs: `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `tasks.md`

- `.venv/bin/python -m py_compile tools/serverless/wiki_manager.py agents/memory_config.py agents/host_agent/agent.py app/hooks.py tests/conftest.py tests/test_memory_authority.py tests/test_memory_expiry.py tests/test_day_state.py tests/test_memory_event_graph.py`
  - Result: Passed.

- `.venv/bin/python -m pytest tests/test_memory_authority.py tests/test_memory_expiry.py tests/test_day_state.py tests/test_memory_event_graph.py`
  - Result: Passed.
  - Tests: 11 passed.

- `env DOTNET_CLI_HOME=/tmp/dotnet dotnet build dotnet-api/FinWiki.Api.csproj`
  - Result: Passed.
  - Output: 0 warnings, 0 errors.

- Authority resolver smoke:
  - Command: local Python call to `resolve_memory_authority(...)`
  - Result: Passed.
  - Canonical policy selected over behavior memory.

- Day-state smoke:
  - Command: local Python call to `update_day_state(...)`
  - Result: Passed.
  - `finwiki-vault/state/day-state.md` updated.

- Event graph smoke:
  - Command: local Python call to `emit_memory_event(...)` and `memory_event_graph_report(limit=20)`
  - Result: Passed.
  - `finwiki-vault/logs/memory-events.jsonl` appended and Obsidian maintenance pages regenerated.

- Stale marker smoke:
  - Command: local Python call to `upsert_wiki_page(...)` and `mark_wiki_memory_stale(...)`
  - Result: Passed.
  - Executed against a temporary vault to avoid falsely marking the canonical DCF example stale.

- Hook-blocked system smoke:
  - Command: `printf ... | .venv/bin/python scripts/invoke_agent.py`
  - Result: Passed.
  - Prompt requesting `.env` was blocked before model invocation.

- Local secret scan:
  - Command: `rg -n "(sk-[A-Za-z0-9]|AIza[[:alnum:]_-]{20,}|Bearer [A-Za-z0-9._+/=-]{20,}|HF_[A-Z0-9_]+=.+|api[_-]?key\\s*[:=])" ...`
  - Result: No real secrets found.
  - Matches were expected placeholders in `README.md` and regex definitions in `tools/serverless/wiki_manager.py`.

## Checks Not Run

- Full model-backed agent invocation was not run for this feature because Memory v2 tests are deterministic and model-free by design.
- Production Obsidian visual inspection was not automated; generated files are plain Markdown under `finwiki-vault/`.

## Residual Risks

- Existing wiki pages are not fully migrated to Memory v2 metadata unless rewritten by `upsert_wiki_page` or manually edited.
- The event graph is a lightweight JSONL projection, not a full graph database.
- `resolve_memory_authority` is deterministic but still depends on agents/tools actually calling it before sensitive answers.
- Stale/expiry governance demotes information; it does not automatically perform fresh web research.

## ActiveGraph Dependency Decision

ActiveGraph is not added as a runtime dependency in this feature. FinWiki first
implements the event-sourcing and projection pattern locally using JSONL and
Obsidian maintenance pages.
