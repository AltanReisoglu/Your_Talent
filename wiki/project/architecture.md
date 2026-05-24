---
title: FinWiki Architecture Map
type: methodology
tags:
  - project
  - architecture
  - finwiki
last_updated: 2026-05-24
status: active
related:
  - index
  - specs
---

# FinWiki Architecture Map

## Core Documents

- [README](../../README.md)
- [AGENTS](../../AGENTS.md)
- [Full Project Report](../../docs/finwiki_project_full_report.md)
- [Financial Services LLM Wiki Architecture](../../docs/financial_services_llm_wiki_architecture.md)
- [Spec Kit Constitution](../../.specify/memory/constitution.md)

## Runtime Boundaries

- Python agent runtime: `agents/`, `app/`, `tools/`
- C# gateway and browser UI: `dotnet-api/`
- Durable financial knowledge: `wiki/`
- Immutable source layer: `raw/`
- Behavior memory: `memories/`
- Read-only policy memory: `policies/`

## Operational Logs

- [Maintenance Log](../../logs/maintenance-log.md)
- [Audit Log](../../logs/audit-log.jsonl)
- [Agent Observations](../../logs/agent-observations.jsonl)
