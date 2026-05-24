# Implementation Plan: FinWiki Working Web Application

**Branch**: `003-finwiki-web-app` | **Date**: 2026-05-23 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/003-finwiki-web-app/spec.md`

## Summary

Deliver a local browser application by extending the existing C# gateway to serve
static UI assets while preserving the Python agent runtime and subprocess bridge.
The UI will call `/health` and `/invoke`, render responses, and expose hook trace
details for observability. Extend Python model configuration so the same agent
runtime can use Hugging Face Router credits through an OpenAI-compatible endpoint.

## Technical Context

**Language/Version**: C#/.NET 10, vanilla HTML/CSS/JavaScript, Python 3.13 bridge

**Primary Dependencies**: ASP.NET Core static files, existing Python
`scripts/invoke_agent.py`, `langchain-openai` for Hugging Face Router

**Storage**: Browser localStorage for user/session IDs; repository Markdown/wiki
files remain unchanged by the UI

**Testing**: `dotnet build`, Python `py_compile`, curl health/root/invoke smoke
tests, Spec evidence checker

**Target Platform**: Local Linux developer machine

**Project Type**: Web app gateway over an AI agent harness

**Performance Goals**: Local UI should load instantly; invoke latency depends on
model/tool calls

**Constraints**: C# must not duplicate agent logic; no secret leakage; no new
frontend build toolchain; no extra runtime service; HF token remains environment
configuration only

**Scale/Scope**: Single-user local development and demo workflow

## Constitution Check

- Runtime Boundary: Passed. C# serves UI/gateway only; Python remains runtime.
- Financial Safety: Passed. UI does not alter financial answer rules.
- Protected Surfaces: Passed. No `.env`, `.git`, `raw/`, or `policies/` writes.
- Single Writer: Passed. UI does not write wiki artifacts directly.
- Evidence: Required before commit/push.

## Project Structure

### Documentation (this feature)

```text
specs/003-finwiki-web-app/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Code

```text
dotnet-api/
├── Program.cs
└── wwwroot/
    ├── index.html
    ├── styles.css
    └── app.js

README.md
agents/model_config.py
.env.example
scripts/spec_evidence_check.py
```

**Structure Decision**: Use static assets under `dotnet-api/wwwroot/` so the
existing .NET gateway can serve the UI without adding Node/Vite/npm.

## FinWiki Constitution Gates

- Runtime Boundary: Python remains the agent runtime; C# remains a gateway.
- Financial Safety: Existing agent/policy/hook behavior remains unchanged.
- Protected Surfaces: No protected files are modified.
- Single Writer: No direct wiki writes from the UI.
- Evidence: `evidence.md` records final validation.

## Complexity Tracking

No constitution violations. Static vanilla frontend is the simplest working app
surface.
