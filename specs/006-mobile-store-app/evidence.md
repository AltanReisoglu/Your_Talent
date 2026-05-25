# Evidence: FinWiki Mobile Store App

**Feature**: `006-mobile-store-app`

**Date**: 2026-05-25

## Summary

Implemented a store-targeted FinWiki mobile MVP scaffold:

- Expo/React Native mobile app under `mobile/finwiki`
- C# gateway endpoints for mobile wiki/search/page/ingest/account flows
- Python JSON bridge over the existing FinWiki wiki harness
- Store readiness docs for Apple App Store and Google Play
- Privacy inventory and release checklist
- Python contract tests for the wiki API bridge
- App shell lives under `mobile/finwiki/src/shell/` to avoid Expo Router
  auto-detecting `src/app/` as a router root.

The mobile app remains a thin client. Python remains the agent runtime and wiki
harness owner. The app does not contain model/provider keys and does not write
wiki/index/log/manifest directly.

## Checks Run

| Check | Command | Result |
|-------|---------|--------|
| Python bridge tests | `.venv/bin/python -m pytest tests/test_wiki_api_bridge.py` | Passed: 2 tests |
| Python syntax | `.venv/bin/python -m py_compile scripts/wiki_api.py scripts/invoke_agent.py` | Passed |
| C# gateway build | `dotnet build dotnet-api/FinWiki.Api.csproj` | Passed: 0 warnings, 0 errors |
| Diff whitespace | `git diff --check` | Passed |
| Mobile dependency lock | `npm install --package-lock-only --ignore-scripts --fetch-timeout=30000 --fetch-retries=1` in `mobile/finwiki` | Passed after network escalation |
| Mobile dependency install | `npm install --ignore-scripts --fetch-timeout=30000 --fetch-retries=1` in `mobile/finwiki` | Passed after network escalation |
| Mobile TypeScript | `npm run typecheck` in `mobile/finwiki` | Passed |
| npm high/critical audit | `npm audit --audit-level=high` in `mobile/finwiki` | Passed for high/critical; reported 11 moderate Expo-chain advisories |
| C# HTTP smoke: health | `curl -sS http://127.0.0.1:8001/health` | Passed |
| C# HTTP smoke: search | `curl -sS 'http://127.0.0.1:8001/wiki/search?q=DCF&limit=2'` | Passed |
| C# HTTP smoke: page | `curl -sS 'http://127.0.0.1:8001/wiki/page?path=concepts/discounted-cash-flow-dcf.md'` | Passed |

## Checks Not Run

| Check | Reason |
|-------|--------|
| `npx expo start` interactive session | Requires interactive device/simulator workflow. Static TypeScript validation passed. |
| EAS iOS build | Requires Expo account, Apple Developer account, signing credentials, and store identifiers. |
| EAS Android build | Requires Expo account and Android signing/release credentials. |
| TestFlight submission | Requires Apple Developer/App Store Connect setup. |
| Google Play internal/closed testing | Requires Play Console setup and tester track configuration. |
| Real `/invoke` model answer through mobile app | Depends on production model quota and backend deployment URL. Existing gateway contract is preserved; local model invocation is covered outside this feature. |

## Residual Risk

- `npm audit --audit-level=high` found no high/critical issues, but npm reports
  11 moderate advisories in the Expo dependency chain. The suggested automated
  fix is a breaking upgrade to Expo 56. Re-evaluate and upgrade Expo before
  public store submission.
- Store release still requires real privacy/support URLs, app icons,
  screenshots, reviewer credentials or guest reviewer mode, developer account
  setup, and signing credentials.
- The mobile account deletion endpoint currently records a deletion request; a
  production deployment must connect this to the actual user/session store.
- Ingest submissions are queued into backend state. Production ingest execution
  still depends on the existing FinWiki single-writer workflow.
- The app is finance-adjacent. Store metadata must remain educational/research
  focused and must avoid brokerage, trading, lending, crypto custody,
  money-management, or personalized advisory claims unless licenses are supplied.

## Store Readiness Artefacts

- `docs/store/privacy-inventory.md`
- `docs/store/app-store-connect.md`
- `docs/store/google-play-console.md`
- `docs/store/release-checklist.md`

## Boundary Verification

- No model/provider keys were added to `mobile/finwiki`.
- No mobile code writes directly to `wiki/`, `finwiki-vault/wiki/`,
  `index.md`, `log.md`, or `.manifest.json`.
- C# gateway changes remain transport-only and call Python bridge scripts.
- Python bridge uses existing wiki harness functions for retrieval and writes
  mobile ingest/account requests to backend state, not wiki pages.
