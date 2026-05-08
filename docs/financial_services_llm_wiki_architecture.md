# Financial Services LLM Wiki Architecture

Last reviewed: 2026-05-06

## Goal

FinWiki is a local-first, Obsidian-compatible LLM Wiki for financial services.
It compiles raw sources into durable Markdown pages, preserves source lineage,
and uses agents to keep the knowledge base current instead of re-deriving
answers from raw documents on every query.

## Design Position

FinWiki is not only a RAG index. It is a compiled knowledge layer:

1. Raw sources remain immutable in `/raw/`.
2. The LLM maintains `/wiki/` as the durable, interlinked synthesis layer.
3. Agent instructions in `AGENTS.md` define routing, ingest, lint, and fan-out.
4. Search/graph systems such as qmd, GraphRAG, LightRAG, or HippoRAG can be
   added on top of the wiki, but they do not replace the Markdown source of
   truth.

## Current Stack

- DeepAgents + LangGraph for supervisor/subagent orchestration and optional async fan-out.
- Markdown + Obsidian wikilinks for durable, human-readable knowledge.
- YAML frontmatter for Dataview, linting, source lineage, and graph-ready metadata.
- DeepAgents filesystem-backed memory for agent/user preferences and read-only policies.
- Wiki Builder-style local configuration and prompt templates.
- `wiki/.manifest.json` for raw source registration and delta tracking.
- `wiki/index.md` for human and agent navigation.
- `wiki/log.md` for append-only operational history.

## Memory Architecture

FinWiki uses DeepAgents long-term memory, but financial knowledge remains in
the wiki. Memory is reserved for behavior, preferences, and policies.

```text
/wiki/       financial facts, analyses, concepts, models, risks, regulation
/raw/        immutable evidence and attachments
/memories/   writable agent/user behavioral memory
/policies/   read-only organization-level policy memory
/skills/     procedural memory
```

Configured memory files:

- `/AGENTS.md`: core operating schema.
- `/wiki.config.md`: local wiki purpose, flavor, taxonomy, and update rules.
- `/sources.md`: human-readable source registry and source-quality notes.
- `/memories/agent.md`: learned operating preferences for FinWiki.
- `/memories/user_preferences.md`: local/default user preferences.
- `/policies/compliance.md`: read-only compliance posture.
- `/policies/source_quality.md`: read-only source hierarchy and citation rules.

Policy files are protected with a write-deny filesystem permission for
`/policies/**`. In a deployed multi-user environment, user preferences should
move to a user-scoped StoreBackend namespace, while policies should remain
organization-scoped and read-only.

Memory placement rules:

- Market facts, company financials, regulatory details, and reusable analyses
  go to `/wiki/`.
- Raw documents, datasets, and attachments go to `/raw/`.
- Response style, workflow lessons, and safe operating habits go to
  `/memories/agent.md`.
- User preferences and watchlists go to `/memories/user_preferences.md` only
  when the user asks to remember them.
- Compliance and source-quality constraints go to `/policies/` and are not
  editable by the agent.

## Wiki Builder Mentality

FinWiki adopts the Wiki Builder idea: each wiki should carry its own local
contract and workflow prompts. This keeps the system portable and reduces the
setup cost for future financial-service wikis.

Local scaffold:

- `wiki.config.md`: purpose, audience, flavor, page types, update rules, quality bar.
- `prompts/compile-index.md`: rebuild the navigation catalog.
- `prompts/compile-source-page.md`: turn raw evidence into compiled pages.
- `prompts/compile-concept-page.md`: create durable concept pages.
- `prompts/query-and-file.md`: answer questions and persist reusable answers.
- `prompts/lint-wiki.md`: run maintenance and self-healing checks.
- `sources.md`: human-readable source registry.
- `derived/`: generated artifacts before they become canonical wiki pages.
- `logs/maintenance-log.md`: manual maintenance decisions and lint summaries.

The operating rule is config-first: when page shape, category, or filing
behavior is unclear, the agent reads `wiki.config.md` and the relevant local
prompt before making structural changes.

## Financial Services Taxonomy

The wiki is organized around reusable financial-services objects:

- `concepts/`: valuation, accounting, risk, market structure concepts.
- `companies/`: issuer and counterparty analysis.
- `instruments/`: equities, bonds, derivatives, funds, crypto assets.
- `markets/`: exchanges, indices, asset-class and country markets.
- `macro/`: rates, inflation, growth, FX, commodities, policy.
- `regulation/`: regulators, rules, disclosures, supervisory guidance.
- `risk/`: credit, market, liquidity, operational, compliance, model risk.
- `models/`: valuation models, risk models, forecasting models, agent patterns.
- `sources/`: source profiles, datasets, filings, APIs, providers, lineage notes.
- `strategies/`: investment strategies, screening rules, portfolio frameworks.

## Obsidian Conventions

Every wiki page should render cleanly in Obsidian:

```yaml
---
title: <Topic>
tags: [finance, <category>]
domain: financial-services
last_updated: YYYY-MM-DD
review_status: draft
aliases: []
sources:
  - "https://..."
related:
  - "related_topic"
---
```

Page bodies should use:

- `[[wikilinks]]` for concepts, companies, instruments, markets, risks, and models.
- `## Sources` with source markers for factual claims.
- `## See Also` for graph edges.
- Clear dated notes for stale or superseded claims.

## Research Scan

### DeepAgents / LangGraph

DeepAgents provides an agent harness with planning, subagents, filesystem
context, skills, and memory. It is built on LangGraph, which supplies durable
execution and agent runtime primitives. Async subagents add non-blocking
background work via Agent Protocol servers and task tools such as
`start_async_task`, `check_async_task`, `update_async_task`, `cancel_async_task`,
and `list_async_tasks`.

Source: https://docs.langchain.com/oss/python/deepagents/overview  
Source: https://docs.langchain.com/oss/python/deepagents/async-subagents

### Obsidian / LLM Wiki Pattern

The LLM Wiki pattern turns conversations and raw source ingestion into a
compounding Markdown wiki. Obsidian becomes the reader/graph interface while
the LLM acts as the maintainer.

Source: https://github.com/Ar9av/obsidian-wiki  
Source: https://llm-wiki.net/

### qmd

qmd is a local Markdown search engine with BM25/vector-style hybrid search and
MCP support. It is a natural next layer once `wiki/index.md` and lightweight
`search_wiki` become insufficient.

Source: https://github.com/tobi/qmd

### GraphRAG

Microsoft GraphRAG builds LLM-derived knowledge graphs from text datasets and
uses graph/community summaries for richer discovery over private data.

Source: https://www.microsoft.com/en-us/research/project/graphrag/

### LightRAG

LightRAG combines graph structures with vector representations and incremental
updates. The key lesson for FinWiki is to keep entity relationships explicit in
Markdown so graph-enhanced retrieval can be added later.

Source: https://huggingface.co/papers/2410.05779  
Source: https://lightrag.github.io/

### HippoRAG

HippoRAG treats retrieval as long-term memory, combining LLM extraction,
knowledge graphs, and Personalized PageRank for multi-hop integration.
FinWiki should preserve entity links and source trails to support this style
of multi-hop reasoning later.

Source: https://huggingface.co/papers/2405.14831

### Financial AI Agent Workflows

FinRobot and FinGPT Search Agents emphasize domain-specialized financial
agents, task decomposition, model/data ops, proprietary/local data, and
time-sensitive financial information.

Source: https://huggingface.co/papers/2405.14767  
Source: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4993491

### Financial Knowledge Graph Construction

FinReflectKG is directly relevant for financial services because it focuses on
financial documents, table-aware chunking, schema-guided extraction, and a
reflection-driven loop for improving KG construction quality.

Source: https://huggingface.co/papers/2508.17906

## Architectural Commitments

- Keep Markdown as the durable truth layer.
- Preserve raw-source lineage before adding heavier retrieval infrastructure.
- Use fan-out for independent research lanes, never for concurrent wiki writes.
- Treat regulation, risk, models, and sources as first-class financial-service
  categories.
- Prefer incremental graph readiness over premature graph database adoption.
- Add qmd first when search becomes painful; add GraphRAG/LightRAG-style graph
  extraction only after the wiki has enough high-quality pages.
