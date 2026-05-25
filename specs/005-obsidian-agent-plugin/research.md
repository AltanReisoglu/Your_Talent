# Research: FinWiki Obsidian Agent Plugin

## Decision: Ship a buildless local Obsidian plugin

**Rationale**: Obsidian loads local plugins from a folder containing `manifest.json`, `main.js`, and optionally `styles.css`. A buildless JavaScript plugin keeps v1 small and avoids adding npm dependencies or a TypeScript build chain.

**Alternatives considered**:
- TypeScript + esbuild starter: better for long-term plugin development, but adds dependency installation and build steps.
- Browser-only web app: already exists, but does not let the user operate from inside Obsidian.

## Decision: Use the existing C# gateway `/invoke`

**Rationale**: The project constitution says Python owns agent behavior and C# is the gateway. The plugin should be another UI surface over the same contract, not a second agent runtime.

**Alternatives considered**:
- Call Python scripts directly from the plugin: violates runtime boundary and couples Obsidian to local shell execution.
- Reimplement query/ingest/lint in plugin code: violates single-writer and memory boundaries.

## Decision: Explicit append-only note writes

**Rationale**: Obsidian note mutation from a plugin is useful but should be user-triggered. The plugin displays answers first, then appends only when the user clicks a button.

**Alternatives considered**:
- Automatically write every answer: too risky and noisy.
- Never write answers: misses the LLM Wiki workflow where useful answers become durable Markdown.

## Decision: Protect hidden/internal paths from context collection

**Rationale**: Active note context should not read hidden configuration, secrets, `.git`, or protected raw/policy material. The plugin should only send normal Markdown note context.

**Alternatives considered**:
- Let agent hooks block sensitive prompts later: useful but too late; the plugin should avoid collecting protected context in the first place.
