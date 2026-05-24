# Evidence Bundle: Obsidian-Integrated Spec Workspace

**Feature Branch**: `002-obsidian-workspace`  
**Spec**: `specs/002-obsidian-workspace/spec.md`  
**Plan**: `specs/002-obsidian-workspace/plan.md`  
**Tasks**: `specs/002-obsidian-workspace/tasks.md`  
**Date**: 2026-05-23

## Summary

Implemented Markdown-first Obsidian support for FinWiki. The repository root can
now be used as an Obsidian vault with a project navigation layer under
`wiki/project/`. Spec Kit artifacts remain canonical under `specs/`; Obsidian
pages link and summarize but do not replace execution artifacts.

Added a dependency-free generator script that scans feature directories and
updates project index, feature summary, methodology, architecture, and evidence
navigation pages.

## Checks Run

| Check | Command | Result | Notes |
| --- | --- | --- | --- |
| Spec prerequisite check | `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` | passed | Script resolved active branch to `003-finwiki-web-app`; implementation intentionally targeted `002-obsidian-workspace` per user request |
| Obsidian generator | `.venv/bin/python scripts/update_obsidian_project_index.py` | passed | Generated project navigation for 3 feature(s) |
| Python syntax | `.venv/bin/python -m py_compile scripts/update_obsidian_project_index.py` | passed | Standard library only |
| Markdown link review | `rg -n "\\]\\([^)]*\\)" wiki/project/index.md wiki/project/specs.md wiki/project/features/001-spec-kit-sdd-foundation.md wiki/project/features/002-obsidian-workspace.md wiki/project/features/003-finwiki-web-app.md` | passed | Links were listed for manual review |
| Secret scan | `rg -n "AIza|lsv2_|tvly-|hf_[A-Za-z0-9]|OPENAI_API_KEY=.+|ANTHROPIC_API_KEY=.+|GOOGLE_API_KEY=.+|TAVILY_API_KEY=.+|LANGSMITH_API_KEY=.+|BEGIN (RSA |EC |OPENSSH |PRIVATE|PUBLIC) KEY" wiki/project docs/obsidian_workspace.md scripts/update_obsidian_project_index.py` | passed | No matches |
| Spec evidence check | `.venv/bin/python scripts/spec_evidence_check.py --feature 002-obsidian-workspace --require-plan --require-tasks --require-evidence` | passed | Feature has plan, tasks, and evidence |

## Checks Not Run

- Obsidian desktop visual inspection was not run from this environment.
- Dataview plugin execution was not run because plugin support is intentionally
  optional and non-required.
- Browser/UI tests were not run because this feature only changes Markdown
  navigation and a helper script.

## Residual Risks

- Generated project pages must be regenerated after future feature status,
  task, or evidence changes.
- Obsidian may hide dot-directories such as `.specify/`; project navigation links
  still point to canonical paths but user display depends on Obsidian settings.
- Markdown link review listed links for manual inspection; it did not execute a
  full graph-aware Obsidian validation pass.

## Changed Artifacts

- `docs/obsidian_workspace.md`
- `scripts/update_obsidian_project_index.py`
- `wiki/project/index.md`
- `wiki/project/specs.md`
- `wiki/project/architecture.md`
- `wiki/project/features/001-spec-kit-sdd-foundation.md`
- `wiki/project/features/002-obsidian-workspace.md`
- `wiki/project/features/003-finwiki-web-app.md`
- `wiki/project/evidence/index.md`
- `wiki/project/methodology/spec-kit-workflow.md`
- `wiki/project/methodology/finwiki-environment.md`
- `wiki.config.md`
- `AGENTS.md`
- `README.md`
- `.dockerignore`
- `specs/002-obsidian-workspace/tasks.md`
- `specs/002-obsidian-workspace/evidence.md`

## Reviewer Notes

- The Obsidian layer is navigation-only. It does not move or replace
  `specs/NNN-feature-name/` artifacts.
- The generator script writes only under `wiki/project/`.
- No new runtime dependency was added to Python, C#, or the browser app.
