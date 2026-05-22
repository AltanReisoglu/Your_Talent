# Feature Specification: Spec Kit SDD Foundation

**Feature Branch**: `001-spec-kit-sdd-foundation`
**Created**: 2026-05-23
**Status**: Implemented
**Input**: User description: "Add GitHub Spec Kit guidance to the project so AI-assisted coding uses specs."

## User Scenarios & Testing

### User Story 1 - Start AI coding from a spec (Priority: P1)

A developer working with an AI coding agent can use the official Spec Kit
workflow to create a feature specification before code is changed.

**Why this priority**: This is the core behavior that moves the project away
from vague prompts and toward executable intent.

**Independent Test**: Confirm `.agents/skills/speckit-*`, `.specify/`, and
`.specify/memory/constitution.md` exist and are documented in README.

**Acceptance Scenarios**:

1. **Given** a non-trivial code change, **When** the developer asks the coding
   agent to use Spec Kit, **Then** the agent has local `$speckit-*` skills and
   project templates available.
2. **Given** an AI-generated plan, **When** it is reviewed, **Then** it checks
   FinWiki constitution gates before implementation.

---

### User Story 2 - Preserve FinWiki-specific governance (Priority: P1)

The project constitution encodes FinWiki's runtime boundaries, financial safety
rules, protected surfaces, and single-writer wiki mutation policy.

**Why this priority**: Generic Spec Kit rules are insufficient for this project;
the agent must preserve existing architecture and financial compliance rules.

**Independent Test**: Read `.specify/memory/constitution.md` and verify no
template placeholders remain.

**Acceptance Scenarios**:

1. **Given** a feature touches the runtime, **When** the plan is generated,
   **Then** Python remains the agent runtime and C# remains a gateway unless a
   spec explicitly justifies a boundary change.
2. **Given** a feature touches financial output, **When** the plan is generated,
   **Then** source lineage, freshness, and no-advice rules are considered.

---

### User Story 3 - Record evidence before completion (Priority: P2)

A developer can capture what was checked, what was skipped, and residual risk
before committing or pushing a change.

**Why this priority**: Evidence bundles close the gap between plausible AI
output and verified AI output.

**Independent Test**: Run `scripts/spec_evidence_check.py --require-evidence`.

**Acceptance Scenarios**:

1. **Given** a feature directory, **When** `evidence.md` is missing and evidence
   is required, **Then** the checker reports failure.
2. **Given** a completed feature directory, **When** all required files and
   evidence exist, **Then** the checker passes.

## Edge Cases

- Tiny typo or small README edits may intentionally skip full SDD, but the final
  response must state why the lightweight path was used.
- Emergency hotfixes may defer full SDD, but evidence must still record what was
  checked and what remains risky.
- Generated Spec Kit files must not contain secrets or local credentials.

## Requirements

### Functional Requirements

- **FR-001**: The repository MUST include official Spec Kit infrastructure under
  `.specify/`.
- **FR-002**: The repository MUST include Codex-compatible Spec Kit skills under
  `.agents/skills/`.
- **FR-003**: The constitution MUST be customized for FinWiki rather than left as
  a template.
- **FR-004**: The README MUST document the Spec Kit workflow and feature artifact
  layout.
- **FR-005**: AGENTS.md MUST tell future AI coding agents to use Spec Kit for
  non-trivial code/runtime/API changes.
- **FR-006**: The project MUST provide an evidence bundle template and checker.
- **FR-007**: Runtime hook context SHOULD remind coding-related requests to use
  Spec Kit artifacts.

### Key Entities

- **Constitution**: Project-level AI coding governance file at
  `.specify/memory/constitution.md`.
- **Feature Artifact Directory**: A `specs/NNN-feature-name/` folder containing
  spec, plan, tasks, and evidence.
- **Evidence Bundle**: A Markdown record of checks run, checks skipped, and
  residual risk.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Spec Kit prerequisite script prints help successfully.
- **SC-002**: Python syntax checks pass for modified Python files.
- **SC-003**: C# gateway builds successfully after documentation and hook changes.
- **SC-004**: Evidence checker passes for this feature.

## Assumptions

- The project uses GitHub Spec Kit's official CLI initialization output as the
  baseline rather than a hand-rolled `.specs/` structure.
- Codex local skills installed under `.agents/skills/` are project assets and
  should be committed.
- `.agents/` may contain private runtime state in other tools, but this repo
  currently stores only checked-in Spec Kit skills there.
