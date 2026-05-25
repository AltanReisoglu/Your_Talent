# Research: FinWiki Mobile Store App

## Decision: React Native + Expo/EAS for the mobile client

**Rationale**: FinWiki needs one codebase for iOS and Android with fast store
iteration, build signing, preview builds, and a UI stack suitable for chat,
knowledge browsing, note capture, and account settings. Expo/EAS gives a
practical app-store path without introducing separate native teams for Swift and
Kotlin on day one.

**Alternatives considered**:
- Flutter: strong cross-platform option, but adds Dart and a separate UI stack
  from the existing web/JS ecosystem.
- .NET MAUI: aligns with C#, but the existing C# code is intentionally a gateway,
  and MAUI store iteration would still require native signing/build operations.
- PWA wrapped for stores: lower effort, but weaker store-native UX and review
  posture for a finance-adjacent app.

## Decision: Mobile app calls a hosted HTTPS FinWiki gateway

**Rationale**: App store binaries must not contain model provider keys, local
Python, or Obsidian vault mutation logic. The mobile app should call a backend
that owns authentication, rate limits, policy hooks, agent invocation, and
single-writer ingest.

**Alternatives considered**:
- Direct model provider calls from device: rejected because secrets and policy
  enforcement would move client-side.
- Local-only desktop bridge: rejected because App Store/Google Play users need a
  remote production service.

## Decision: Position as educational/research knowledge assistant, not a regulated financial service

**Rationale**: Apple App Store Review Guideline 3.2.1(viii) says apps used for
financial trading, investing, or money management should be submitted by the
financial institution performing those services. Google Play's financial
services policy covers financial products/services and says apps with financial
features may need declarations and regulatory compliance. FinWiki should not
claim trading execution, money management, lending, brokerage, crypto custody,
or personalized advice in MVP.

**Sources**:
- Apple App Store Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Google Play Financial Services policy: https://support.google.com/googleplay/android-developer/answer/9876821

**Alternatives considered**:
- Add portfolio/brokerage integration in MVP: rejected because it changes the
  licensing and store-policy risk profile.
- Personalized recommendations: rejected for MVP because it increases financial
  advice, suitability, and liability risk.

## Decision: Privacy inventory before store metadata

**Rationale**: Apple requires app privacy details in App Store Connect for
submission and updates. Google Play requires a completed Data safety section for
all apps, including apps that collect no user data. The app must track every
data type, purpose, linkage, sharing, and SDK/backend processor before
submission.

**Sources**:
- Apple App Privacy Details: https://developer.apple.com/app-store/app-privacy-details/
- Google Play Data Safety: https://support.google.com/googleplay/android-developer/answer/10787469

**Alternatives considered**:
- Fill store forms after implementation: rejected because SDK choices and
  backend logging directly affect disclosures.

## Decision: Account deletion is a release blocker if accounts exist

**Rationale**: Apple requires apps that support account creation to also allow
account deletion from within the app. Google Play requires developers to provide
data deletion information and a web link for account/data deletion where
applicable. FinWiki should avoid mandatory accounts for MVP if possible; if
accounts are added, deletion must be designed before release.

**Sources**:
- Apple account deletion guidance: https://developer.apple.com/support/offering-account-deletion-in-your-app/
- Google Play User Data policy: https://support.google.com/googleplay/android-developer/answer/10144311

**Alternatives considered**:
- Manual email-only deletion: rejected as the only path because store reviewers
  expect in-app and web-accessible deletion flows depending on platform.

## Decision: Plan beta tracks before public launch

**Rationale**: Apple TestFlight is the normal pre-release path for iOS review and
external testing. Google Play supports internal/closed testing, and new personal
developer accounts may need closed testing with at least 20 testers for 14 days
before production access.

**Sources**:
- Apple TestFlight overview: https://developer.apple.com/testflight/
- Google Play closed testing requirements: https://support.google.com/googleplay/android-developer/answer/14151465

**Alternatives considered**:
- Submit directly to production: rejected because finance-adjacent AI behavior
  needs beta evidence and reviewer notes before public release.
