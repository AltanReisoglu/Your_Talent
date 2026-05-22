# Evidence Bundle: Spec Kit SDD Foundation

**Feature Branch**: `001-spec-kit-sdd-foundation`
**Spec**: `specs/001-spec-kit-sdd-foundation/spec.md`
**Plan**: `specs/001-spec-kit-sdd-foundation/plan.md`
**Tasks**: `specs/001-spec-kit-sdd-foundation/tasks.md`
**Date**: 2026-05-23

## Summary

The repository was initialized with GitHub Spec Kit's Codex integration. FinWiki
now has a project constitution, Spec Kit skills/templates, README and AGENTS
workflow guidance, runtime hook context for coding requests, and an evidence
checker.

## Checks Run

| Check | Command | Result | Notes |
|-------|---------|--------|-------|
| Spec Kit init | `uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --integration codex --script sh --ignore-agent-tools` | passed | Installed official Spec Kit files |
| Python syntax | `.venv/bin/python -m py_compile app/hooks.py scripts/spec_evidence_check.py` | passed | No syntax errors |
| Evidence checker | `.venv/bin/python scripts/spec_evidence_check.py --require-evidence` | passed | This feature contains evidence.md |
| Spec Kit script | `bash .specify/scripts/bash/check-prerequisites.sh --help` | passed | Script is executable and prints help |
| C# build | `env DOTNET_CLI_HOME=/tmp/dotnet dotnet build dotnet-api/FinWiki.Api.csproj` | passed | 0 warnings, 0 errors |
| Secret scan | `rg -n "AIza|lsv2_|tvly-|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_API_KEY|TAVILY_API_KEY|LANGSMITH_API_KEY|BEGIN (RSA |EC |OPENSSH |PRIVATE|PUBLIC) KEY" AGENTS.md README.md app scripts .agents .specify` | passed | Only env var names and redaction regex references found |

## Checks Not Run

- Full agent invoke was not run; this change is workflow/documentation plus a
  hook-context update, not model behavior.
- Spec Kit feature branch creation was not run; the integration was initialized
  on the existing branch per user request.

## Residual Risks

- `.agents/skills/` is committed as project workflow code. If a future tool stores
  private runtime state under `.agents/`, that subpath must be added to
  `.gitignore` without ignoring checked-in skills.
- Official Spec Kit templates may change upstream; local FinWiki additions should
  be reviewed during future Spec Kit upgrades.

## Changed Artifacts

- `.agents/skills/speckit-*`
- `.specify/`
- `AGENTS.md`
- `README.md`
- `app/hooks.py`
- `scripts/spec_evidence_check.py`
- `specs/001-spec-kit-sdd-foundation/`

## Reviewer Notes

- The custom FinWiki evidence bundle is an additive policy on top of official
  Spec Kit. It does not replace Spec Kit's spec, plan, tasks, analyze, or
  implement flow.
