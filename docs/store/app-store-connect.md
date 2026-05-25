# App Store Connect Runbook

## Product Positioning

FinWiki is submitted as a financial education and knowledge-base assistant. It
must not be described as a broker, lender, trading tool, money manager, crypto
wallet, or personalized investment adviser.

## Required Before TestFlight

- Apple Developer account is active.
- Bundle ID matches `com.altanreisoglu.finwiki` or an approved production ID.
- EAS/iOS signing credentials are configured outside git.
- Privacy policy URL and support URL are live.
- App Privacy details match `docs/store/privacy-inventory.md`.
- Reviewer can use guest mode or supplied test credentials.
- Financial safety disclaimer is visible in the app.
- Account deletion is available if account creation is enabled.

## Required Before App Review

- Screenshots for required device classes are prepared.
- App description avoids regulated financial-service claims.
- Age rating and encryption answers are completed.
- Review notes explain that model/API keys are server-side and the app is an
  educational knowledge assistant.
- TestFlight build has been exercised against the production-like HTTPS backend.

## Reviewer Notes Draft

FinWiki is a financial education and knowledge-base assistant. It provides
source-aware explanations and wiki browsing. It does not execute trades, manage
money, provide lending, custody assets, or provide personalized investment
advice. Demo access can be used without connecting any financial accounts.
