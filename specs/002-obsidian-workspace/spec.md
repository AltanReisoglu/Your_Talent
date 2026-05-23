# Feature Specification: Obsidian-Integrated Spec Workspace

**Feature Branch**: `002-obsidian-workspace`

**Created**: 2026-05-23

**Status**: Draft

**Input**: User description: "I want Spec Kit to work tightly with Obsidian, because the 'build the environment, not just the agent' idea convinced me."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate AI coding intent in Obsidian (Priority: P1)

A developer can open the repository as an Obsidian workspace and navigate from a
feature idea to its spec, plan, tasks, evidence, related FinWiki pages, and
architecture notes without searching Slack/chat history.

**Why this priority**: The main value is turning AI coding intent into a durable
workspace instead of transient chat context.

**Independent Test**: Open the repo in Obsidian and follow links from the project
index to this feature's spec, plan, and evidence without using terminal search.

**Acceptance Scenarios**:

1. **Given** a new Spec Kit feature, **When** the developer opens Obsidian,
   **Then** the feature appears in a navigable project/spec index.
2. **Given** a feature page, **When** the developer follows related links,
   **Then** they can reach relevant FinWiki concepts, architecture decisions,
   and evidence.

---

### User Story 2 - Keep Spec Kit as execution source of truth (Priority: P1)

Spec Kit remains the authoritative workflow for feature specs, plans, tasks, and
implementation. Obsidian provides navigation, backlinks, and knowledge context
without replacing `.specify/` or `specs/`.

**Why this priority**: Obsidian must strengthen the official Spec Kit workflow,
not fork it into a parallel documentation system.

**Independent Test**: Confirm that generated Spec Kit artifacts stay under
`specs/NNN-feature-name/` and `.specify/`, while Obsidian-facing pages only link
to or summarize them.

**Acceptance Scenarios**:

1. **Given** a feature plan, **When** Obsidian integration is added, **Then** the
   original `spec.md`, `plan.md`, `tasks.md`, and `evidence.md` stay in place.
2. **Given** an Obsidian project page, **When** it summarizes a feature, **Then**
   it links back to canonical Spec Kit artifacts.

---

### User Story 3 - Preserve project knowledge as infrastructure (Priority: P2)

The repository accumulates domain-specific methodology, decisions, risks, and
evidence as a reusable knowledge environment. AI models may change, but the
project's structured context remains valuable.

**Why this priority**: This turns FinWiki from "an agent feature" into an
environment that agents can read, maintain, and improve over time.

**Independent Test**: A future agent can answer "why was this feature designed
this way?" by reading Obsidian-linked spec/evidence/decision artifacts.

**Acceptance Scenarios**:

1. **Given** an accepted implementation, **When** evidence is completed, **Then**
   residual risks and skipped checks are discoverable from the Obsidian graph.
2. **Given** related wiki concepts, **When** a developer reviews a feature,
   **Then** they can see the concept links that shaped the implementation.

---

### User Story 4 - Avoid tool or plugin lock-in (Priority: P3)

The integration uses Markdown, YAML frontmatter, and wikilinks as the stable
surface. Optional Obsidian plugins can improve UX, but the core workflow remains
usable without them.

**Why this priority**: The project should own the knowledge structure, not depend
on a specific Obsidian plugin or SaaS feature.

**Independent Test**: Browse and validate the artifacts with plain files and CLI
tools even if Obsidian is not installed.

**Acceptance Scenarios**:

1. **Given** no Obsidian plugins installed, **When** the repo is opened as a
   vault, **Then** core links and Markdown pages remain readable.
2. **Given** optional Dataview or graph plugins installed, **When** the user
   enables them, **Then** they enhance navigation without becoming required.

### Edge Cases

- Obsidian may hide dot-directories such as `.specify/`; canonical user-facing
  navigation must not depend on browsing hidden infrastructure.
- Spec Kit feature branches may exist without completed tasks or evidence; the
  Obsidian index must represent draft/in-progress status clearly.
- Wiki pages are English while user discussion may be Turkish; navigation labels
  must remain understandable in both contexts.
- Large raw sources and assets must stay under `raw/`; Obsidian pages should link
  to them rather than duplicating content.
- The integration must not encourage writing financial facts into memory files.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST define an Obsidian-compatible navigation model for
  Spec Kit feature artifacts under `specs/`.
- **FR-002**: The system MUST keep Spec Kit artifacts canonical and avoid moving
  or duplicating `.specify/` workflow files.
- **FR-003**: The system MUST define frontmatter fields for project/spec/evidence
  pages so Obsidian graph and Dataview-style tooling can index them later.
- **FR-004**: The system MUST link Spec Kit feature artifacts to relevant FinWiki
  wiki pages, architecture docs, and evidence bundles.
- **FR-005**: The system MUST provide a quickstart for opening the repo or wiki
  as an Obsidian workspace.
- **FR-006**: The system MUST support plain Markdown/CLI use when Obsidian is not
  installed.
- **FR-007**: The system MUST document optional plugin enhancements separately
  from required behavior.
- **FR-008**: The system MUST preserve existing FinWiki rules for source lineage,
  no-advice language, raw-source immutability, and policy read-only memory.

### Key Entities *(include if feature involves data)*

- **Obsidian Workspace**: The repository opened as a Markdown vault, with `wiki/`,
  `specs/`, `docs/`, and `logs/` as primary visible surfaces.
- **Spec Feature**: A `specs/NNN-feature-name/` directory with canonical Spec Kit
  artifacts.
- **Evidence Bundle**: `evidence.md` inside a feature directory, recording checks
  run, skipped checks, and residual risks.
- **Project Index Page**: An Obsidian-readable index that links features, wiki
  concepts, decisions, and architecture notes.
- **Knowledge Link**: A wikilink or relative Markdown link connecting specs,
  evidence, wiki pages, sources, or architecture docs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can open the repo in Obsidian and navigate to all
  feature specs from a single project/spec index page.
- **SC-002**: Each completed feature can link to its `spec.md`, `plan.md`,
  `tasks.md`, and `evidence.md` from Obsidian-visible navigation.
- **SC-003**: The integration introduces no new runtime dependency for Python or
  C# execution.
- **SC-004**: The workflow remains valid using only Markdown files and
  `.venv/bin/python scripts/spec_evidence_check.py --require-evidence`.
- **SC-005**: Existing FinWiki wiki pages remain Obsidian-compatible and are not
  moved.

## Assumptions

- The repository root will be the primary Obsidian vault for development, because
  it exposes both `wiki/` and `specs/`.
- `.specify/` is hidden infrastructure and not the primary navigation surface.
- The first implementation should be Markdown-first; plugin-specific automation
  can be added later.
- This feature plans the integration before implementation. It does not yet
  generate all Obsidian index pages.
