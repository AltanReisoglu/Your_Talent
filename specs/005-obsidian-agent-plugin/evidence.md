# Evidence: FinWiki Obsidian Agent Plugin

**Feature**: `005-obsidian-agent-plugin`
**Date**: 2026-05-25
**Status**: Passed with noted runtime limitation

## Summary

Implemented a local Obsidian plugin for FinWiki. The plugin is a thin UI and
transport layer over the existing C# gateway `/invoke` endpoint. Python remains
the agent runtime and the plugin does not duplicate query, ingest, lint, memory,
or wiki mutation logic.

## Checks Run

| Check | Command | Result | Notes |
|-------|---------|--------|-------|
| Source plugin JS syntax | `node --check obsidian-plugin/finwiki-agent/main.js` | passed | No syntax errors |
| Installed plugin JS syntax | `node --check finwiki-vault/.obsidian/plugins/finwiki-agent/main.js` | passed | Installed copy parses |
| Plugin manifest JSON | `.venv/bin/python -m json.tool obsidian-plugin/finwiki-agent/manifest.json` | passed | Valid JSON |
| Installed manifest JSON | `.venv/bin/python -m json.tool finwiki-vault/.obsidian/plugins/finwiki-agent/manifest.json` | passed | Valid JSON |
| Install helper syntax | `.venv/bin/python -m py_compile scripts/install_obsidian_plugin.py` | passed | No syntax errors |
| Install helper execution | `.venv/bin/python scripts/install_obsidian_plugin.py` | passed | Installed into `finwiki-vault/.obsidian/plugins/finwiki-agent` |
| C# gateway build | `env DOTNET_CLI_HOME=/tmp/dotnet dotnet build dotnet-api/FinWiki.Api.csproj` | passed | 0 warnings, 0 errors |
| Gateway health smoke | `curl -sS http://127.0.0.1:8000/health` | passed | Returned `{"status":"ok","service":"finwiki-dotnet-api"}` |
| Gateway invoke smoke | `curl -sS -X POST http://127.0.0.1:8000/invoke ...` | passed | Hook-block request returned `Blocked by FinWiki hook` |

## Checks Not Run

- Obsidian GUI plugin load was not automated. Obsidian desktop does not expose a
  stable headless test harness in this repo.
- Full live LLM request from the plugin was not run. The gateway invoke smoke
  used a deterministic hook-block request to validate the route without quota or
  model dependency.
- Public Obsidian marketplace packaging was not run. This is a local repository
  plugin for the FinWiki vault.

## Residual Risk

- Obsidian API behavior should be manually verified in the desktop app after
  enabling the plugin.
- The plugin depends on the local C# gateway being started separately.
- The installed plugin copy under `finwiki-vault/.obsidian/plugins/` is a local
  generated install artifact; canonical source lives under
  `obsidian-plugin/finwiki-agent/`.

## Files Changed

- `obsidian-plugin/finwiki-agent/manifest.json`
- `obsidian-plugin/finwiki-agent/main.js`
- `obsidian-plugin/finwiki-agent/styles.css`
- `obsidian-plugin/finwiki-agent/README.md`
- `scripts/install_obsidian_plugin.py`
- `README.md`
- `docs/obsidian_workspace.md`
- `AGENTS.md`
- `specs/005-obsidian-agent-plugin/*`
