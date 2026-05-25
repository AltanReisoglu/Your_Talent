# Implementation Plan: FinWiki Obsidian Agent Plugin

**Branch**: `005-obsidian-agent-plugin` | **Date**: 2026-05-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-obsidian-agent-plugin/spec.md`

## Summary

Deliver a local-first Obsidian plugin that calls the existing FinWiki C# gateway `/invoke` endpoint from inside the vault. The plugin provides command palette actions for asking FinWiki, asking with selected note context, ingesting the active note, and running wiki lint. It does not implement agent reasoning or wiki mutation logic.

## Technical Context

**Language/Version**: JavaScript for Obsidian desktop plugin runtime; Python 3.13 and C#/.NET 10 remain existing runtime surfaces

**Primary Dependencies**: Obsidian desktop plugin API, existing C# gateway `/invoke`, existing Python agent bridge

**Storage**: Obsidian plugin settings stored by Obsidian; no new database

**Testing**: JSON validation, `node --check`, Python syntax check for install helper, optional gateway smoke request

**Target Platform**: Obsidian desktop vault at `finwiki-vault`

**Project Type**: Local Obsidian plugin over existing agent gateway

**Performance Goals**: Plugin loads without build step; command execution overhead should be negligible compared with agent latency

**Constraints**: Python remains runtime; C# remains gateway; plugin must not read protected files as note context; writes to notes only after explicit user action

**Scale/Scope**: Single local FinWiki vault and one local gateway endpoint

## Constitution Check

- Runtime Boundary: Passed. Plugin is a UI/transport surface and calls C# `/invoke`; Python remains agent runtime.
- Financial Safety: Passed. Plugin does not generate financial content itself; it delegates to existing FinWiki hooks and agent policy.
- Protected Surfaces: Passed. Plugin refuses hidden/protected active paths and does not inspect `.env`, `.git`, or raw internals.
- Single Writer: Passed. Plugin does not write wiki/index/log/manifest directly. Note append is explicit user editing of the active Markdown note.
- Evidence: Required. Add `evidence.md` with manifest syntax, JS syntax, install helper syntax, and smoke-test status.

## Project Structure

### Documentation (this feature)

```text
specs/005-obsidian-agent-plugin/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── invoke-contract.md
├── tasks.md
└── evidence.md
```

### Source Code (repository root)

```text
obsidian-plugin/
└── finwiki-agent/
    ├── manifest.json
    ├── main.js
    ├── styles.css
    └── README.md

scripts/
└── install_obsidian_plugin.py

finwiki-vault/
└── .obsidian/
    └── plugins/
        └── finwiki-agent/
            ├── manifest.json
            ├── main.js
            └── styles.css
```

**Structure Decision**: Keep the canonical plugin source under `obsidian-plugin/finwiki-agent/` and provide an install helper that copies runtime plugin files into the local vault. This avoids adding a Node build pipeline for v1.

## FinWiki Constitution Gates

- Runtime Boundary: Python remains the agent runtime; C# remains a gateway.
- Financial Safety: User-facing financial behavior remains governed by the existing FinWiki agent/hook system.
- Protected Surfaces: `.env`, `.git`, `raw/`, and `policies/` are not modified.
- Single Writer: Wiki/index/log/manifest writes remain serialized through the agent and wiki-ingestor path.
- Evidence: `evidence.md` records checks run, skipped checks, and residual risk.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
