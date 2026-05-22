<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles:
- [PRINCIPLE_1_NAME] -> I. Intent Before Implementation
- [PRINCIPLE_2_NAME] -> II. Runtime Boundary Discipline
- [PRINCIPLE_3_NAME] -> III. Financial Safety and Source Lineage
- [PRINCIPLE_4_NAME] -> IV. Deterministic Gates and Evidence
- [PRINCIPLE_5_NAME] -> V. Simplicity, Context, and Single Writer
Added sections:
- Architecture Constraints
- Development Workflow
- Governance
Removed sections:
- Template placeholder sections only
Templates requiring updates:
- Updated: .specify/templates/plan-template.md
- Updated: .specify/templates/tasks-template.md
- Reviewed: .specify/templates/spec-template.md
- Added: .specify/templates/evidence-template.md
Follow-up TODOs:
- None
-->

# FinWiki Constitution

## Core Principles

### I. Intent Before Implementation

Every non-trivial code change MUST begin with a Spec Kit feature artifact before
implementation. The specification captures what users or operators need and why;
it MUST avoid premature implementation detail. The implementation plan then maps
the accepted specification to concrete architecture, constraints, and validation
strategy. Tasks MUST be small, file-specific, independently reviewable, and tied
back to the spec and plan.

### II. Runtime Boundary Discipline

Python remains the agent runtime and source of orchestration behavior. C# remains
an input/output gateway and MUST NOT duplicate agent reasoning, memory, or wiki
mutation logic. FastAPI may remain as a thin compatibility surface. DeepAgents,
Mirage, wiki tools, hooks, and model configuration stay in the Python layer
unless a spec explicitly justifies a boundary change.

### III. Financial Safety and Source Lineage

FinWiki MUST preserve the separation between raw sources, wiki facts, behavior
memory, and read-only policy memory. Financial user-facing output MUST be framed
as research, education, scenario analysis, or risk discussion, never direct
personalized buy/sell advice. Durable financial claims MUST retain source,
freshness, and lineage through raw source, manifest, wiki page, and user answer
where applicable.

### IV. Deterministic Gates and Evidence

Hooks, tests, lint checks, secret scans, and evidence bundles supersede model
memory. A change is not complete until the evidence bundle records what was
checked, what was not checked, and residual risks. Secrets, `.env`, `.git`,
`raw/`, and `policies/` are protected surfaces; changes touching them require an
explicit spec, stated risk, and human approval.

### V. Simplicity, Context, and Single Writer

Prefer the smallest design that satisfies the current spec. Avoid speculative
abstractions, duplicate runtimes, and parallel writes to shared wiki artifacts.
Read/research lanes may fan out, but `wiki-ingestor` remains the single writer
for wiki, index, log, and manifest mutations. Large features MUST be split into
phases so the active agent context stays focused.

## Architecture Constraints

- Agent orchestration lives under `agents/` and Python service glue under `app/`.
- C# code under `dotnet-api/` is a transport gateway over the Python bridge.
- Wiki knowledge lives under `wiki/`; immutable evidence lives under `raw/`.
- Agent/user memory lives under `memories/`; shared policies live under
  `policies/` and are read-only.
- Spec Kit infrastructure lives under `.specify/`; feature artifacts live under
  `specs/NNN-feature-name/`.
- Project-specific runtime rules remain in `AGENTS.md`; this constitution
  governs AI-assisted code change workflow.
- Wiki pages are written in English; user responses follow the user's language.

## Development Workflow

Use the Spec Kit workflow for non-trivial changes:

1. `$speckit-specify` defines the user need, acceptance criteria, and measurable
   success criteria.
2. `$speckit-clarify` is used when requirements contain ambiguity.
3. `$speckit-checklist` validates requirement quality before planning.
4. `$speckit-plan` creates the technical plan and constitution check.
5. `$speckit-tasks` creates file-specific, dependency-aware tasks.
6. `$speckit-analyze` checks consistency across spec, plan, and tasks before
   implementation.
7. `$speckit-implement` executes tasks in small increments.
8. An `evidence.md` bundle records validation results before commit or push.

Tiny documentation edits, typo fixes, and emergency hotfixes may skip full SDD,
but the final response MUST state that the change intentionally used the
lightweight path and why.

## Governance

This constitution supersedes ad-hoc prompts for code change workflow. Amendments
require updating this file, reviewing dependent Spec Kit templates, and recording
the version bump reason in the Sync Impact Report. Versioning follows semantic
rules: MAJOR for incompatible governance changes, MINOR for new or expanded
principles, PATCH for clarifications. Reviews MUST verify constitution
compliance, evidence completeness, and absence of secret leakage before push.

**Version**: 1.0.0 | **Ratified**: 2026-05-23 | **Last Amended**: 2026-05-23
