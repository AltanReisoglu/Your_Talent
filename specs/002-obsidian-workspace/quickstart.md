# Quickstart: Obsidian-Integrated Spec Workspace

## 1. Open the vault

Open the repository root in Obsidian:

```text
/home/altan/Desktop/Your_Talent
```

Use the repository root, not only `wiki/`, so `specs/`, `docs/`, and evidence
files are visible alongside the FinWiki vault.

## 2. Start from the main surfaces

Primary navigation surfaces:

- `wiki/index.md` for financial knowledge
- `specs/` for Spec Kit feature artifacts
- `docs/` for architecture documentation
- `logs/maintenance-log.md` for maintenance decisions
- `.specify/memory/constitution.md` for AI coding governance

## 3. Create a new feature with Spec Kit

Use the Spec Kit skills in Codex:

```text
$speckit-specify
$speckit-plan
$speckit-tasks
$speckit-implement
```

Artifacts appear under:

```text
specs/NNN-feature-name/
```

## 4. Link feature artifacts into Obsidian

For each important feature, create or update a project navigation page that links
to:

- `spec.md`
- `plan.md`
- `tasks.md`
- `evidence.md`
- related `wiki/` pages
- related `docs/` architecture notes

## 5. Complete evidence before commit/push

Run:

```bash
.venv/bin/python scripts/spec_evidence_check.py --require-evidence
```

If a feature is complete, `evidence.md` must record:

- checks run
- checks intentionally skipped
- residual risks
- changed artifacts

## 6. Optional Obsidian enhancements

The core workflow does not require plugins. Later, Dataview can be used to query
feature statuses, evidence completeness, and related wiki concepts from
frontmatter.
