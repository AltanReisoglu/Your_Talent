# Implementation Plan: FinWiki Mobile Store App

**Branch**: `006-mobile-store-app` | **Date**: 2026-05-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-mobile-store-app/spec.md`

## Summary

Build FinWiki as a store-ready iOS and Android mobile app. The mobile app is a
thin product surface for chat, wiki browse/search, note capture, and store-safe
financial education UX. It calls a production HTTPS FinWiki backend; it does not
run Python, DeepAgents, model keys, Obsidian vault mutation, or wiki ingest logic
on device.

The recommended MVP stack is React Native with Expo/EAS for cross-platform app
delivery, backed by the existing FinWiki gateway/runtime boundary: mobile client
→ HTTPS gateway/BFF → Python FinWiki agent runtime → Markdown/Obsidian-backed
knowledge system.

## Technical Context

**Language/Version**: TypeScript + React Native/Expo for mobile; C#/.NET gateway
and Python 3.13 agent runtime remain backend surfaces

**Primary Dependencies**: Expo SDK, React Native, EAS Build/Submit, existing
FinWiki `/invoke` contract, existing Python DeepAgents runtime

**Storage**: Secure client storage for auth/session tokens only; backend
database/object storage for user account/session metadata if accounts are
enabled; durable financial knowledge remains in the FinWiki wiki/backend

**Testing**: Unit/component tests for mobile UI, API contract tests, backend
smoke tests, TestFlight, Google Play internal/closed testing, store-compliance
checklist

**Target Platform**: iOS App Store and Google Play

**Project Type**: Mobile app + hosted AI agent backend

**Performance Goals**: App launch under 3 seconds on modern devices; prompt send
feedback within 500 ms; backend answer latency surfaced with progress state;
knowledge search response under 2 seconds for indexed pages

**Constraints**: No model/API keys in mobile binaries; no local Python runtime on
device; no direct mobile writes to wiki/index/log/manifest; no personalized
investment advice; production mobile app uses HTTPS, not localhost

**Scale/Scope**: MVP for public beta/store submission with chat, wiki browse,
note capture, privacy/account controls, and release artefacts

## Constitution Check

- Runtime Boundary: Passed. Mobile is UI only. Python remains agent runtime.
  C# or an API gateway remains transport/BFF and must not duplicate reasoning.
- Financial Safety: Passed with release-blocking requirements. Store metadata,
  in-app UX, and model behavior must frame output as education/research, not
  regulated advice, brokerage, trading, lending, or money management.
- Protected Surfaces: Passed. Mobile does not modify `.env`, `.git`, `raw/`, or
  `policies/`. Secrets remain server-side.
- Single Writer: Passed. Mobile capture requests go through backend ingest; the
  app never writes wiki/index/log/manifest directly.
- Evidence: Required. Release evidence must include build checks, store-policy
  checklist, privacy inventory, account deletion path, and beta testing status.

## Project Structure

### Documentation (this feature)

```text
specs/006-mobile-store-app/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── mobile-api-contract.md
    └── store-readiness-contract.md
```

### Proposed Source Code

```text
mobile/
└── finwiki/
    ├── app.json
    ├── package.json
    ├── eas.json
    └── src/
        ├── app/
        ├── components/
        ├── features/
        │   ├── chat/
        │   ├── wiki/
        │   ├── capture/
        │   └── account/
        ├── services/
        │   └── finwikiApi.ts
        └── store/

dotnet-api/
└── Program.cs                  # BFF/gateway endpoints; no agent reasoning

app/
└── main.py                     # Optional Python service surface for deployment

docs/
└── store/
    ├── app-store-connect.md
    ├── google-play-console.md
    ├── privacy-inventory.md
    └── release-checklist.md
```

**Structure Decision**: Add a new `mobile/finwiki/` Expo app while keeping agent
logic in backend code. Production release work should also add a store docs
folder so App Store/Google Play declarations are versioned alongside code.

## FinWiki Constitution Gates

- Runtime Boundary: Python remains the agent runtime; mobile remains UI.
- Financial Safety: Must include disclaimers, source/freshness UI, and metadata
  review against regulated financial-service claims.
- Protected Surfaces: Store credentials, signing keys, API keys, and provider
  tokens must not be committed.
- Single Writer: Mobile capture is a request to backend ingest, not a direct wiki
  write.
- Evidence: Store submission is blocked until evidence records technical checks,
  policy checks, skipped checks, and residual risks.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New mobile project | App Store/Google Play require native/mobile packaging, signing, screenshots, and platform metadata | Existing web/Obsidian surfaces cannot be distributed as iOS/Android store apps |
| Hosted backend requirement | Store apps cannot depend on `localhost` or a desktop vault; model keys must stay server-side | Shipping model/API keys or Python runtime in the app would violate security and runtime boundaries |
