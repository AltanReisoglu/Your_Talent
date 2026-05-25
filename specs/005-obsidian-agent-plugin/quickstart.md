# Quickstart: FinWiki Obsidian Agent Plugin

## 1. Install plugin into the local vault

```bash
.venv/bin/python scripts/install_obsidian_plugin.py
```

## 2. Start the FinWiki C# gateway

```bash
DOTNET_CLI_HOME=/tmp/dotnet \
FINWIKI_DOTNET_URL=http://0.0.0.0:8000 \
dotnet run --project dotnet-api/FinWiki.Api.csproj
```

## 3. Enable the plugin in Obsidian

Open `/home/altan/Desktop/Your_Talent/finwiki-vault` in Obsidian.

Go to Settings → Community plugins → Installed plugins → enable **FinWiki Agent**.

## 4. Run commands

Open the command palette and run:

- `FinWiki: Ask FinWiki`
- `FinWiki: Ask FinWiki about selection/current note`
- `FinWiki: Ingest current note`
- `FinWiki: Run wiki lint`

## 5. Validate expected behavior

- A successful request displays the FinWiki answer in a modal.
- The append button writes only to the active Markdown note.
- If the gateway is down, the plugin shows a connection error and does not modify notes.
