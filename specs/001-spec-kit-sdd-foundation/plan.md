# Implementation Plan: Spec Kit SDD Foundation

**Branch**: `001-spec-kit-sdd-foundation` | **Date**: 2026-05-23 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/001-spec-kit-sdd-foundation/spec.md`

## Summary

Initialize GitHub Spec Kit with Codex integration, customize FinWiki's
constitution, document the workflow, add an evidence bundle convention, and make
runtime hooks aware of coding-related Spec Kit context.

## Technical Context

**Language/Version**: Python 3.13, C#/.NET 10

**Primary Dependencies**: GitHub Spec Kit, DeepAgents, FastAPI, Mirage, .NET

**Storage**: Local Markdown files and repository templates

**Testing**: Python `py_compile`, Spec Kit bash script help, evidence checker,
`dotnet build`

**Target Platform**: Local Linux development, GitHub repository

**Project Type**: Multi-runtime agent harness with Python runtime and C# gateway

**Performance Goals**: Not performance-sensitive; workflow reliability matters

**Constraints**: Do not expose secrets; do not overwrite FinWiki operating
instructions; preserve existing runtime boundaries

**Scale/Scope**: Project-level workflow foundation

## Constitution Check

*GATE: Passed before implementation.*

- Runtime Boundary: Python remains the agent runtime; C# remains a gateway.
- Financial Safety: Constitution preserves no-advice and source-lineage rules.
- Protected Surfaces: No `.env`, `.git`, `raw/`, or `policies/` writes.
- Single Writer: No wiki mutation path changes.
- Evidence: This feature includes `evidence.md`.

## Project Structure

### Documentation (this feature)

```text
specs/001-spec-kit-sdd-foundation/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Code and Workflow Artifacts

```text
.agents/skills/
.specify/
AGENTS.md
README.md
app/hooks.py
scripts/spec_evidence_check.py
```

**Structure Decision**: Use official Spec Kit structure. Do not create a custom
`.specs/changes` workflow.

## Complexity Tracking

No constitution violations.
