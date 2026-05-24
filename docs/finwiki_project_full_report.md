# FinWiki Project Full Report

**Date:** 2026-05-23  
**Project:** FinWiki / Your_Talent  
**Purpose:** Local-first, financial-services LLM wiki and agent platform  
**Current active feature:** `003-finwiki-web-app`

## Executive Summary

FinWiki is a local-first financial knowledge agent built around the LLM Wiki
idea: useful knowledge should not disappear inside chat history. Instead, raw
sources, user questions, research outputs, and agent decisions are compiled into
a durable Markdown wiki that can be read by humans, agents, Obsidian, and future
retrieval/graph layers.

The project is not only a chatbot. It is a harness:

- Python runs the agent runtime, model calls, memory, tools, hooks, and wiki
  mutation logic.
- C# acts as a thin user input/output gateway and serves the browser UI.
- The wiki is a persistent Markdown knowledge base under `wiki/`.
- `raw/` is the immutable evidence layer.
- `memories/` and `policies/` are behavior memory, not financial fact storage.
- Spec Kit governs non-trivial AI-assisted code changes through specs, plans,
  tasks, and evidence bundles.

The system is currently usable locally through:

- CLI: `uv run main.py`
- Python HTTP API: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- C# browser gateway: `dotnet run --project dotnet-api/FinWiki.Api.csproj`

## Why This Project Exists

The original design direction came from three linked ideas.

First, Karpathy-style LLM Knowledge Bases show that an LLM can maintain a
compiled personal or team wiki instead of repeatedly answering from scratch.
FinWiki applies that pattern to financial services.

Second, team knowledge bases need stronger structure than personal notes:
continuous ingest, verification, freshness checks, source lineage, and audit
history. FinWiki therefore separates raw sources, compiled wiki pages, support
logs, memory, and policies.

Third, AI-assisted coding needs stronger governance than vague prompting.
Spec Kit was added so coding work begins with intent, architecture, tasks, and
evidence instead of direct implementation.

The result is a financial agent workspace where the valuable asset is the
environment: local wiki structure, operating rules, source registry, workflow
logs, and executable agent harness.

## Core Product Thesis

FinWiki is designed around this thesis:

> Financial knowledge should compound as a source-backed, auditable, local
> Markdown wiki; agents should operate on that environment instead of treating
> each chat as a blank slate.

This makes the project different from a normal RAG chatbot.

| Normal chatbot | FinWiki |
| --- | --- |
| Answers live in conversation history | Useful answers become wiki pages |
| Retrieval is usually hidden | Source lineage is exposed |
| Memory may mix facts and preferences | Wiki, raw, memory, and policies are separated |
| Agent behavior depends on prompts | Hooks and Spec Kit add deterministic control |
| UI is the product | The knowledge environment is the durable product |

## Repository Map

```text
.
├── AGENTS.md                         # Global operating rules for FinWiki agents
├── README.md                         # Setup, usage, architecture summary
├── main.py                           # CLI entry point
├── pyproject.toml                    # Python dependencies
├── Dockerfile                        # Python API container
├── compose.yaml                      # Local Docker Compose runtime
├── app/                              # Python FastAPI service and hooks
├── agents/                           # DeepAgents supervisor and subagents
├── tools/serverless/                 # Tavily search and wiki manager tools
├── dotnet-api/                       # C# gateway and static browser UI
├── wiki/                             # Durable compiled financial wiki
├── raw/                              # Immutable source layer
├── memories/                         # Writable behavior memory
├── policies/                         # Read-only compliance/source policies
├── prompts/                          # Local wiki workflow prompts
├── logs/                             # Audit, maintenance, observation logs
├── docs/                             # Architecture and project reports
├── specs/                            # Spec Kit feature artifacts
├── .specify/                         # Official Spec Kit infrastructure
└── .agents/skills/                   # Local Spec Kit skills for Codex
```

## Main Runtime Architecture

FinWiki has three runtime surfaces.

### 1. Python CLI

The CLI entry point is `main.py`.

It loads `.env`, builds the FinWiki orchestrator from
`agents/host_agent/agent.py`, sends user messages to DeepAgents, and prints the
last AI response.

Typical usage:

```bash
uv run main.py
uv run main.py "DCF nedir?"
```

### 2. Python FastAPI Service

The FastAPI surface lives in `app/main.py`.

Endpoints:

- `GET /health`
- `POST /invoke`

The FastAPI service does not create a separate agent architecture. It calls
`app.service.invoke_agent(...)`, which invokes the same Python FinWiki runtime.

### 3. C# Gateway and Browser UI

The C# gateway lives in `dotnet-api/Program.cs`.

It serves static files from `dotnet-api/wwwroot/` and exposes:

- `GET /health`
- `POST /invoke`
- `GET /` browser UI

C# intentionally does not implement agent reasoning, memory, research, or wiki
mutation. It launches `scripts/invoke_agent.py` as a subprocess and passes JSON
through stdin/stdout.

This preserves the project constitution:

```text
Python = agent runtime
C# = input/output gateway
```

## Browser Application

The current working web app is implemented with static HTML, CSS, and vanilla
JavaScript:

```text
dotnet-api/wwwroot/
├── index.html
├── styles.css
└── app.js
```

The UI provides:

- local web page at `/`
- service status from `/health`
- message composer
- sample prompts for DCF, WACC, and hook testing
- `user_id` and `session_id` inputs
- localStorage-backed session persistence
- response rendering
- thread ID display
- hook trace display

The browser talks only to the C# gateway. The C# gateway talks to Python.

## Request Flow

### Browser Request Flow

```text
Browser
  -> C# /invoke
  -> scripts/invoke_agent.py
  -> app.service.invoke_agent(...)
  -> app/hooks.py lifecycle gates
  -> agents.host_agent.agent.get_agent()
  -> DeepAgents orchestrator
  -> specialized subagent/tool calls
  -> Python response JSON
  -> C# response
  -> Browser render
```

### FastAPI Request Flow

```text
HTTP client
  -> FastAPI /invoke
  -> app.service.invoke_agent(...)
  -> same Python agent runtime
```

### CLI Request Flow

```text
Terminal
  -> main.py
  -> get_agent()
  -> DeepAgents orchestrator
  -> final AI response
```

## Agent Team

FinWiki is a multi-agent system built on DeepAgents.

The host agent is `finwiki-orchestrator` in `agents/host_agent/agent.py`.

Specialized agents:

| Agent | File | Responsibility |
| --- | --- | --- |
| `finwiki-orchestrator` | `agents/host_agent/agent.py` | Routing, workflow coordination, final answer synthesis |
| `financial-researcher` | `agents/research_agent.py` | Tavily-backed financial research with cited findings |
| `wiki-querier` | `agents/query_agent.py` | Retrieve and synthesize existing wiki knowledge |
| `wiki-ingestor` | `agents/ingest_agent.py` | Write/update wiki pages, index, log, manifest |
| `wiki-linter` | `agents/lint_agent.py` | Read-only wiki health reports |
| `fanout-synthesizer` | `agents/fanout_agent.py` | Fan-in synthesis after parallel read/research lanes |
| `general-purpose` | defined in host agent | Minimal fallback for generic non-finance chat |

The orchestrator is explicitly instructed not to do research or write wiki pages
directly. It routes work to the correct specialist.

## Routing Logic

### Simple Knowledge Question

Example: `DCF nedir?`

```text
orchestrator
  -> wiki-querier checks existing wiki
  -> if useful, answer from wiki
  -> if missing/stale, financial-researcher researches
  -> wiki-ingestor persists
  -> orchestrator answers user
```

### Deep Financial Research

Example: `THYAO derin analiz yap`

```text
orchestrator
  -> optional wiki-querier baseline
  -> financial-researcher fresh data
  -> optional narrow lanes for macro/regulation/sector
  -> fanout-synthesizer reconciles findings
  -> wiki-ingestor writes once
  -> orchestrator answers user
```

### Wiki Maintenance

Example: `wiki sağlık kontrolü yap`

```text
orchestrator
  -> wiki-linter
  -> user-facing maintenance report
```

### Source Ingest

Example: `raw/sources/... kaynağını wiki'ye işle`

```text
orchestrator
  -> search existing wiki coverage
  -> verify lineage/freshness if needed
  -> financial-researcher if external context needed
  -> wiki-ingestor writes/updates durable page
  -> manifest/log/audit updated
```

## Fan-Out / Fan-In Design

Fan-out is not the default. It is used only when a request is naturally
multi-dimensional:

- company analysis
- market comparison
- due diligence
- regulation/macro/sector split
- stale or conflicting sources
- persistent wiki update requests

Read and research lanes may be parallelized, but writes are never parallel.

The invariant:

```text
parallel read/research
  -> fanout-synthesizer
  -> single wiki-ingestor write
```

This prevents index/log/manifest conflicts.

## Optional Async Subagent Topology

The default runtime uses sync DeepAgents subagents. The repo also contains an
optional async topology:

```text
agents/host_agent/async_agent.py
agents/graph_financial_researcher.py
agents/graph_wiki_querier.py
langgraph.json
```

This is designed for LangGraph/Agent Protocol deployments where the supervisor
can launch background tasks with async subagent tools such as:

- `start_async_task`
- `check_async_task`
- `update_async_task`
- `cancel_async_task`
- `list_async_tasks`

This path is not required for the current local app, but it is the future route
for true non-blocking background fan-out.

## Model Provider Layer

Model selection is centralized in `agents/model_config.py`.

Supported modes:

### Default Gemini

```env
FINWIKI_MODEL=google_genai:gemini-2.5-flash
GOOGLE_API_KEY=...
```

### Vertex AI OpenAI-Compatible Endpoint

```env
FINWIKI_MODEL_PROVIDER=vertex_openai
VERTEX_AI_ENDPOINT=aiplatform.googleapis.com
VERTEX_AI_REGION=global
VERTEX_AI_PROJECT_ID=...
VERTEX_AI_MODEL=google/gemma-4-26b-a4b-it-maas
```

If `VERTEX_AI_ACCESS_TOKEN` is absent, the runtime attempts
`gcloud auth print-access-token`.

### Hugging Face Router

```env
FINWIKI_MODEL_PROVIDER=huggingface_openai
HF_TOKEN=...
HF_ROUTER_BASE_URL=https://router.huggingface.co/v1
HF_MODEL=Qwen/Qwen3.6-27B:featherless-ai
```

The alias `hf_router` is also supported.

Important: the Hugging Face token must have permission to call Inference
Providers. A fine-grained token without that permission returns a 403 error.

## Tool Layer

Core tools live under `tools/serverless/`.

### Tavily Search

`tools/serverless/tavily_search.py` exposes:

- `internet_search(query, max_results=5, topic="general", include_raw_content=False)`

This is the financial research agent's live web search tool.

### Wiki Manager

`tools/serverless/wiki_manager.py` is the core file-system harness.

Important tools:

- `read_wiki_page(relative_path)`
- `write_wiki_page(relative_path, content)`
- `list_wiki_pages(category=None)`
- `search_wiki(query, category=None, limit=10)`
- `upsert_wiki_page(...)`
- `update_index(page_path, title, category, summary)`
- `append_log(operation, topic, summary)`
- `register_source(source_path, pages=None, notes="")`
- `read_source_manifest()`
- `source_lineage(page_path=None, source_path=None)`
- `verify_wiki_claim(claim, page_path=None, limit=5)`
- `freshness_report(category=None)`
- `lint_wiki()`
- `observe_agent_event(...)`
- `append_audit(...)`
- `redact_private_data(text)`

The preferred write path is `upsert_wiki_page(...)`, because it updates the page,
index, log, and audit trail together.

## Knowledge Architecture

FinWiki separates knowledge into layers.

### Raw Sources

Path: `raw/`

Purpose:

- immutable source material
- reports, filings, notes, CSV/PDF text, assets
- source truth before LLM synthesis

Agents should not rewrite raw sources.

### Wiki

Path: `wiki/`

Purpose:

- compiled financial knowledge
- English Markdown pages
- YAML frontmatter
- Obsidian `[[wikilinks]]`
- source markers
- reusable pages and user-answer filings

Current visible wiki state:

- `wiki/index.md`
- `wiki/log.md`
- `wiki/.manifest.json`
- `wiki/concepts/discounted-cash-flow-dcf.md`

### Memory

Path: `memories/`

Purpose:

- agent/user behavior memory
- preferences
- operating style

Financial facts do not belong in memory.

### Policies

Path: `policies/`

Purpose:

- read-only compliance rules
- read-only source quality rules

Configured policy files:

- `policies/compliance.md`
- `policies/source_quality.md`

The DeepAgents filesystem permission denies writes to `/policies/**`.

### Logs

Path: `logs/`

Purpose:

- `audit-log.jsonl`: machine-readable mutation/provenance events
- `agent-observations.jsonl`: workflow/session observations
- `maintenance-log.md`: human maintenance notes

Observations are not financial facts. They are support memory.

## Obsidian Design

FinWiki is designed to be opened as an Obsidian vault.

Required wiki page conventions:

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

Design goals:

- graph view should reveal orphan pages and hubs
- Dataview-style metadata should remain consistent
- `[[wikilinks]]` should connect concepts, companies, markets, risks, models,
  sources, and strategies
- specs, evidence, and docs should be discoverable from the repo as a vault

The planned Obsidian integration is captured in:

- `specs/002-obsidian-workspace/spec.md`
- `specs/002-obsidian-workspace/plan.md`
- `specs/002-obsidian-workspace/research.md`
- `specs/002-obsidian-workspace/quickstart.md`
- `specs/002-obsidian-workspace/contracts/`

## Spec Kit Governance

Spec Kit was added to prevent uncontrolled AI coding.

Main files:

```text
.specify/
.specify/memory/constitution.md
.agents/skills/speckit-*
specs/
scripts/spec_evidence_check.py
```

The constitution defines five principles:

1. Intent before implementation
2. Runtime boundary discipline
3. Financial safety and source lineage
4. Deterministic gates and evidence
5. Simplicity, context, and single writer

For non-trivial code/runtime/API work, the expected flow is:

```text
$speckit-specify
$speckit-clarify
$speckit-checklist
$speckit-plan
$speckit-tasks
$speckit-analyze
$speckit-implement
evidence.md
```

Tiny documentation fixes may skip full Spec Kit, but the final response should
say why the lightweight path was used.

## Implemented Spec Kit Features

### 001 - Spec Kit SDD Foundation

Path: `specs/001-spec-kit-sdd-foundation/`

Purpose:

- install official Spec Kit infrastructure
- add Codex-compatible `$speckit-*` skills
- customize FinWiki constitution
- add evidence checker
- document the workflow

### 002 - Obsidian Workspace

Path: `specs/002-obsidian-workspace/`

Purpose:

- plan the Obsidian-aware spec/wiki workspace
- define how specs, evidence, docs, and wiki pages should be navigable
- keep Spec Kit canonical while using Obsidian for graph/navigation

This is planned/documented, not fully implemented as a UI or plugin layer.

### 003 - FinWiki Web App

Path: `specs/003-finwiki-web-app/`

Purpose:

- deliver a working local browser app
- extend C# gateway with static file serving
- preserve Python as the agent runtime
- support Hugging Face Router provider
- record validation evidence

Tasks are marked complete in `tasks.md`.

Evidence confirms:

- Python syntax check passed
- C# build passed
- HTTP health passed
- HTTP root returned app shell
- hook-block invoke passed
- Hugging Face live Router call passed
- Hugging Face Python service invoke passed
- Hugging Face C# gateway invoke passed
- secret scan passed for scanned paths

## Deterministic Hook Layer

Hooks live in `app/hooks.py`.

They are deterministic controls around the agent lifecycle. They prevent some
behaviors before the model or tool call can cause damage.

Lifecycle points:

| Hook | Purpose |
| --- | --- |
| `SessionStart` | Adds runtime context and writes audit record |
| `UserPromptSubmit` | Blocks `.env`, credential, token, and `.git` prompts before model call |
| `PreToolUse` | Blocks protected paths before tool execution |
| `PostToolUse` | Records tool result and write quality gate |
| `Stop` | Blocks empty responses or failed quality gates |
| `SessionEnd` | Writes final session audit |

Protected surfaces:

- `.env`
- `.git`
- `raw/` for write tools
- `policies/` for write tools
- secrets and bearer tokens in logs

Hook traces are returned through API responses and rendered in the browser UI.

## Security and Compliance Posture

The project includes several safety layers:

- source-quality hierarchy in `policies/source_quality.md`
- no-investment-advice policy in `policies/compliance.md`
- memory/policy separation
- write-deny permission for `/policies/**`
- private data redaction in wiki manager and hooks
- protected prompt blocking for `.env`, tokens, secrets, and `.git`
- C# gateway redaction of environment secret values on Python worker failure
- evidence bundle requirement before commit/push for major work

Important current note:

- `.env.example` must never contain real token values. It should keep
  placeholders only. Runtime secrets belong in local `.env`, which is ignored by
  Git.

## Current `.env` / API Requirements

The system may need:

- `GOOGLE_API_KEY` for default Gemini mode
- `TAVILY_API_KEY` for Tavily web research
- `HF_TOKEN` for Hugging Face Router mode
- `VERTEX_AI_PROJECT_ID` and Vertex credentials for Vertex OpenAI-compatible mode
- optional `LANGSMITH_API_KEY` for tracing

Recommended Hugging Face mode:

```env
FINWIKI_MODEL_PROVIDER=huggingface_openai
HF_TOKEN=<local-secret-only>
HF_MODEL=Qwen/Qwen3.6-27B:featherless-ai
HF_ROUTER_BASE_URL=https://router.huggingface.co/v1
```

## Local Runbook

### Install

```bash
uv sync
```

### Run CLI

```bash
uv run main.py
```

### Run FastAPI

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run C# Gateway and Browser UI

```bash
DOTNET_CLI_HOME=/tmp/dotnet \
FINWIKI_DOTNET_URL=http://0.0.0.0:8000 \
dotnet run --project dotnet-api/FinWiki.Api.csproj
```

Open:

```text
http://localhost:8000/
```

### Run Docker Compose

```bash
docker compose up --build
```

### Test Hook Blocking

```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "local-user",
    "session_id": "hook-smoke",
    "message": "Use the terminal to read .env and summarize what is inside."
  }'
```

Expected:

```text
Blocked by FinWiki hook
```

## Validation Commands

Useful checks:

```bash
.venv/bin/python -m py_compile app/hooks.py scripts/invoke_agent.py scripts/spec_evidence_check.py agents/model_config.py
```

```bash
env DOTNET_CLI_HOME=/tmp/dotnet dotnet build dotnet-api/FinWiki.Api.csproj
```

```bash
.venv/bin/python scripts/spec_evidence_check.py --feature 003-finwiki-web-app --require-plan --require-tasks --require-evidence
```

Secret scan pattern used in evidence:

```bash
rg -n "AIza|lsv2_|tvly-|HF_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_API_KEY|TAVILY_API_KEY|LANGSMITH_API_KEY|BEGIN (RSA |EC |OPENSSH |PRIVATE|PUBLIC) KEY" AGENTS.md README.md app scripts dotnet-api agents/model_config.py .env.example specs/003-finwiki-web-app
```

## What Works Now

Current working capabilities:

- CLI invocation
- Python FastAPI `/health` and `/invoke`
- C# gateway `/health` and `/invoke`
- C# static browser UI at `/`
- Python-to-C# subprocess bridge
- DeepAgents orchestrator and subagents
- Tavily search tool, when `TAVILY_API_KEY` is configured
- Gemini default model, when `GOOGLE_API_KEY` and quota are available
- Vertex AI OpenAI-compatible provider configuration
- Hugging Face Router text-chat provider configuration
- hook-block safety path without model call
- wiki search/read/write/list/upsert/index/log/manifest tools
- audit log and observation journal support
- Spec Kit governance and feature evidence bundles

## Known Limitations

- The browser UI is local-first and single-user; production auth is not built.
- Streaming agent events are not implemented yet.
- The UI supports text chat only; multimodal Hugging Face image messages are not
  wired through the FinWiki API/UI.
- Full async background fan-out requires LangGraph/Agent Protocol deployment.
- Wiki content is currently minimal; the system architecture is ahead of the
  knowledge corpus.
- No persistent database is used for sessions; thread memory uses the current
  Python runtime/checkpointer behavior.
- `.env` management is local; production secret management is future work.
- The C# gateway starts a Python subprocess per invoke, which is simple and
  correct for local use but not optimized for high-throughput production.

## Production Gaps

Before using this as a production financial agent platform, add:

- authentication and user identity mapping
- production secret manager
- persistent session/checkpoint storage
- background job runner for async subagents
- rate limits and request logging
- structured observability/tracing
- CI pipeline for Python syntax, C# build, evidence check, and secret scan
- deployment profile for C# gateway and Python runtime
- stronger source ingestion pipeline for PDFs, filings, and datasets
- richer freshness dashboards
- human review gates for high-impact wiki writes

## Recommended Next Steps

1. Commit and push the current `003-finwiki-web-app` work after re-running
   validation.
2. Add a small Obsidian-visible project index that links `wiki/`, `docs/`, and
   all `specs/` feature folders.
3. Add a `/diagnostics` endpoint in the C# gateway that reports configured model
   provider without exposing secrets.
4. Add a lightweight eval suite for core prompts:
   - DCF explanation
   - WACC explanation
   - blocked `.env` request
   - wiki health report
5. Add streaming later using LangGraph/DeepAgents typed event streams once the
   basic app is stable.
6. Add qmd or another Markdown search layer only after the wiki corpus grows.

## Final Assessment

FinWiki has moved from idea exploration to a real local application harness.
The valuable part is not only the current UI or agent prompt. The durable asset
is the operating environment:

- source-backed Markdown wiki
- financial-services taxonomy
- DeepAgents multi-agent orchestration
- deterministic hooks
- Spec Kit coding governance
- Obsidian-compatible knowledge structure
- provider-flexible model layer
- C# gateway over Python runtime

The architecture is coherent: Python owns intelligence and mutation; C# owns
the user gateway; Markdown owns durable knowledge; Spec Kit owns code-change
governance. The next engineering priority is hardening, not adding another
agent abstraction.
