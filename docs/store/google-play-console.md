# Google Play Console Runbook

## Product Positioning

FinWiki is a financial education and research knowledge-base assistant. Store
metadata must avoid claims of trading, brokerage, lending, crypto custody,
regulated financial advice, or guaranteed investment outcomes.

## Required Before Internal / Closed Testing

- Google Play developer account is active.
- Android package matches `com.altanreisoglu.finwiki` or an approved production
  package name.
- App signing is configured outside git.
- Privacy policy URL and support URL are live.
- Data Safety form is drafted from `docs/store/privacy-inventory.md`.
- Financial features declaration is reviewed.
- Guest reviewer mode or test credentials are available.
- Closed testing requirements are understood for the developer account.

## Required Before Production Review

- Store listing, short description, full description, screenshots, feature
  graphic, content rating, target audience, and contact details are complete.
- Account/data deletion web link exists if accounts are enabled.
- No model/provider keys are bundled into the Android artifact.
- Backend downtime and hook-blocked states are visible as readable app errors.

## Financial Features Declaration Notes

If future versions add portfolio import, trading, lending, payments, crypto,
wallet, or personalized recommendations, create a separate spec before enabling
the feature. That changes the Play policy and compliance surface.
