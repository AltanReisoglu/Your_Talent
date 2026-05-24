---
title: FinWiki Environment Thesis
type: methodology
tags:
  - project
  - finwiki
  - methodology
last_updated: 2026-05-24
status: active
related:
  - architecture
  - specs
---

# FinWiki Environment Thesis

FinWiki's durable value is the operating environment around the agent, not a
single model call.

## Layers

- `raw/`: immutable evidence
- `wiki/`: compiled financial knowledge
- `memories/`: behavior and preference memory
- `policies/`: read-only compliance and source-quality policy
- `logs/`: audit, observation, and maintenance history
- `specs/`: AI coding intent, plans, tasks, and evidence
- `dotnet-api/`: user gateway
- `agents/` and `tools/`: Python agent runtime

## Principle

Models can change. The local context structure, source lineage, task evidence,
and Markdown knowledge graph remain the reusable asset.
