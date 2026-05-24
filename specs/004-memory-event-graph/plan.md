# Implementation Plan: FinWiki Memory Event Graph

**Branch**: `004-memory-event-graph` | **Date**: 2026-05-24 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/004-memory-event-graph/spec.md`

## Summary

Implement Memory v2 for FinWiki by adding deterministic Remember/Cite/Forget
governance to the existing Markdown-first knowledge system. The MVP keeps
DeepAgents as the orchestration runtime and Obsidian as the human-facing vault,
while adding authority resolution, validity/expiry metadata, day-state,
structured memory events, and a lightweight event-graph projection inspired by
ActiveGraph. ActiveGraph itself is not added as a runtime dependency in the MVP.

## Technical Context

**Language/Version**: Python 3.13, Markdown/YAML frontmatter, optional C# gateway
unchanged

**Primary Dependencies**: Existing DeepAgents/LangChain runtime, standard-library
JSON/Markdown helpers, existing `tools/serverless/wiki_manager.py`, no new
required package for MVP

**Storage**: Local Obsidian vault under `finwiki-vault/`; JSONL event logs under
`finwiki-vault/logs/`; Markdown day-state under `finwiki-vault/state/`

**Testing**: Python `py_compile`; pytest-style local tests under `tests/`; direct
tool smoke tests with `.venv/bin/python`

**Target Platform**: Local Linux developer machine with repository workspace and
Obsidian vault

**Project Type**: Agent memory/governance layer over a local Markdown knowledge
base

**Performance Goals**: Authority resolution and event projection complete in
under one second for current local vault size; search remains dependency-free

**Constraints**: Python remains runtime; C# gateway does not duplicate memory
logic; no direct writes to `.env`, `.git`, `raw/`, or `policies/`; wiki writes
remain serialized through existing wiki-manager/ingestor path; financial
answers remain educational and source-aware

**Scale/Scope**: Single-user local FinWiki vault with dozens to hundreds of
Markdown pages and JSONL event history

## Constitution Check

- Runtime Boundary: Passed. All memory/governance logic remains in Python.
- Financial Safety: Passed. Feature strengthens source, freshness, and authority
  handling for financial claims.
- Protected Surfaces: Passed. No `.env`, `.git`, `raw/`, or `policies/` writes
  are required. Policy files are read-only inputs.
- Single Writer: Passed. Event logging and maintenance pages are serialized by
  wiki-manager functions; no parallel wiki writers are introduced.
- Evidence: Required before commit/push.

## Project Structure

### Documentation (this feature)

```text
specs/004-memory-event-graph/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── memory-governance-tools.md
├── tasks.md
└── evidence.md
```

### Source Code

```text
tools/serverless/
└── wiki_manager.py              # authority, expiry, day-state, event graph tools

agents/
├── memory_config.py             # include day-state as operational memory
└── host_agent/agent.py          # prompt/tool guidance for memory governance

finwiki-vault/
├── state/
│   └── day-state.md             # short-lived operating whiteboard
├── logs/
│   └── memory-events.jsonl      # append-only memory event log
└── wiki/
    ├── maintenance/
    │   ├── expiry-review.md
    │   └── memory-governance.md
    └── templates/
        ├── finwiki-page.md
        └── source-note.md

tests/
├── test_memory_authority.py
├── test_memory_expiry.py
├── test_day_state.py
└── test_memory_event_graph.py

docs/
└── memory_v2.md

AGENTS.md
README.md
```

**Structure Decision**: Extend the current `wiki_manager.py` local-tool module
instead of adding a new runtime. Add tests under a new `tests/` directory so the
governance layer can be validated without model calls.

## FinWiki Constitution Gates

- Runtime Boundary: Python remains the agent runtime; C# remains a gateway.
- Financial Safety: Memory resolution must not allow behavior memory, summaries,
  or day-state to override policies or sourced wiki facts.
- Protected Surfaces: `policies/**` are read-only; `.env`, `.git`, and `raw/`
  remain protected.
- Single Writer: Existing wiki write helpers remain the only code path for page,
  index, log, and manifest mutation.
- Evidence: `evidence.md` records tests, syntax checks, smoke checks, skipped
  checks, and residual risks.

## Complexity Tracking

No constitution violations. The event graph is implemented as a lightweight
projection over JSONL events first; adding ActiveGraph as a package dependency is
reserved for a later feature if the local projection proves insufficient.
