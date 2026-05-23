# Data Model: Obsidian-Integrated Spec Workspace

## Entity: ObsidianWorkspace

Represents the repository opened as an Obsidian vault.

**Fields**
- `root_path`: repository root
- `visible_surfaces`: `wiki/`, `specs/`, `docs/`, `logs/`, selected `raw/assets/`
- `hidden_infrastructure`: `.specify/`, `.git/`, `.venv/`, build outputs
- `required_plugins`: none
- `optional_plugins`: Dataview, Canvas, graph filters

## Entity: SpecFeature

Represents a Spec Kit feature directory.

**Fields**
- `feature_id`: numeric prefix, e.g. `002`
- `slug`: human-readable feature slug
- `status`: draft, planned, tasks-ready, implemented, archived
- `spec_path`: path to `spec.md`
- `plan_path`: path to `plan.md`
- `tasks_path`: path to `tasks.md`
- `evidence_path`: path to `evidence.md`
- `related_wiki_pages`: list of wikilinks
- `related_docs`: list of relative Markdown links

## Entity: EvidenceBundle

Represents validation state for a feature.

**Fields**
- `feature_id`
- `checks_run`: command/result/notes rows
- `checks_not_run`: skipped checks with rationale
- `residual_risks`: known risks and follow-up items
- `changed_artifacts`: relevant files/modules
- `reviewer_notes`

## Entity: ProjectIndexPage

Represents an Obsidian-friendly navigation page.

**Fields**
- `title`
- `type`: project-index, feature-index, decision-index, evidence-index
- `tags`
- `last_updated`
- `links`: related specs, wiki pages, docs, evidence
- `query_blocks`: optional Dataview snippets

## Entity: KnowledgeLink

Represents a relationship between artifacts.

**Fields**
- `source_path`
- `target_path`
- `link_type`: spec-to-wiki, spec-to-evidence, spec-to-doc, decision-to-feature,
  source-to-page
- `rationale`

## State Transitions

```text
SpecFeature
  draft -> planned -> tasks-ready -> implemented -> archived

EvidenceBundle
  missing -> partial -> complete -> superseded

ProjectIndexPage
  absent -> generated -> maintained
```

## Validation Rules

- Every completed `SpecFeature` must have an `EvidenceBundle`.
- Project index pages must link to canonical Spec Kit artifacts, not duplicate
  their content as source of truth.
- Financial facts remain in `wiki/`; workflow observations remain in `logs/` or
  evidence files.
- Links to `raw/` must reference sources/assets without modifying them.
