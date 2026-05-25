# FinWiki Agent Obsidian Plugin

Local Obsidian plugin for operating FinWiki from inside the vault.

The plugin is intentionally thin:

- It sends prompts to the existing C# gateway `/invoke`.
- It can include selected text or the active note as context.
- It can ask the agent to ingest the current note.
- It can ask the agent to run a wiki lint/health check.
- It can append a displayed answer to the active Markdown note by explicit user action.

It does not implement agent reasoning, memory, query, ingest, or lint logic.

## Install Into Local Vault

From the repository root:

```bash
.venv/bin/python scripts/install_obsidian_plugin.py
```

This installs runtime files into:

```text
finwiki-vault/.obsidian/plugins/finwiki-agent/
```

Then open the vault in Obsidian and enable **FinWiki Agent** under Community plugins.

## Start Gateway

```bash
DOTNET_CLI_HOME=/tmp/dotnet \
FINWIKI_DOTNET_URL=http://0.0.0.0:8000 \
dotnet run --project dotnet-api/FinWiki.Api.csproj
```

Default plugin endpoint:

```text
http://127.0.0.1:8000/invoke
```

## Commands

- `FinWiki: Ask FinWiki`
- `FinWiki: Ask FinWiki about selection/current note`
- `FinWiki: Ingest current note`
- `FinWiki: Run wiki lint`

## Settings

- Invoke endpoint
- User ID
- Session prefix
- Max context characters
