# Research: Obsidian-Integrated Spec Workspace

## Decision: Use repository root as the Obsidian vault

**Rationale**: The project knowledge surface spans `wiki/`, `specs/`, `docs/`,
`logs/`, and selected `raw/assets/` links. Opening only `wiki/` would hide Spec
Kit artifacts; opening only `specs/` would hide FinWiki knowledge. The root gives
Obsidian a complete graph while keeping canonical file locations unchanged.

**Alternatives considered**:
- `wiki/` as vault only: simpler, but disconnects specs/evidence from knowledge.
- Separate generated vault: cleaner UX, but duplicates content and creates drift.

## Decision: Keep Spec Kit artifacts canonical

**Rationale**: Spec Kit already defines canonical feature directories under
`specs/NNN-feature-name/`. Obsidian pages should link to those artifacts, not
move or copy them. This preserves compatibility with `$speckit-plan`,
`$speckit-tasks`, and future Spec Kit upgrades.

**Alternatives considered**:
- Move specs into `wiki/project/`: improves graph visibility but breaks Spec Kit
  assumptions.
- Generate duplicated summary pages only: useful later, but initial design should
  avoid duplicate truth.

## Decision: Markdown-first, plugin-optional

**Rationale**: The stable asset is the Markdown structure, not any specific
Obsidian plugin. YAML frontmatter and wikilinks provide a durable base. Dataview,
graph filters, and canvas can be optional enhancements.

**Alternatives considered**:
- Require Dataview from day one: more powerful queries, but adds plugin lock-in.
- Build a custom UI first: unnecessary before the Markdown knowledge graph is
  stable.

## Decision: Evidence bundles are first-class graph nodes

**Rationale**: AI-generated code often looks plausible without being verified.
`evidence.md` captures checks run, skipped checks, and residual risk. Linking
evidence to specs and wiki concepts makes review state visible in Obsidian.

**Alternatives considered**:
- Keep evidence only in final chat summaries: easy to lose and not queryable.
- Put evidence in logs only: machine-readable but weaker for human review.

## Decision: Create a project navigation layer under `wiki/project/`

**Rationale**: `specs/` holds canonical workflow artifacts, but users need entry
points. `wiki/project/` can contain Obsidian-friendly index pages that link to
features, decisions, evidence, architecture docs, and methodology notes.

**Alternatives considered**:
- Use only `wiki/index.md`: too broad; mixes financial knowledge and project
  engineering knowledge.
- Use only README: not graph-friendly and not focused on knowledge navigation.
