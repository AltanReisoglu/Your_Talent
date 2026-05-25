# Contract: Store Readiness Gate

Before public submission, the feature must produce a release package with the
following evidence.

## Apple App Store

- App Store Connect app record exists.
- Bundle ID, signing, version, and build number are configured.
- Privacy policy URL and support URL exist.
- App Privacy labels are completed and match the privacy inventory.
- If accounts exist, account deletion is available in-app.
- Financial positioning avoids trading, investing, money management, lending,
  brokerage, crypto custody, or personalized advice claims unless licenses are
  supplied.
- TestFlight build is tested.
- Reviewer notes include demo credentials or guest mode instructions.
- Screenshots, age rating, encryption answers, and review contact are complete.

## Google Play

- Play Console app record exists.
- Package name, signing, version code, and release track are configured.
- Data Safety section is completed and matches the privacy inventory.
- Financial features declaration is completed if the app contains financial
  features.
- Account/data deletion web link exists if accounts exist.
- Closed/internal testing requirements are satisfied for the developer account.
- Store listing, content rating, target audience, screenshots, and reviewer
  access are complete.

## Shared FinWiki Gates

- No model/provider keys in mobile app bundle.
- No direct mobile write access to wiki/index/log/manifest.
- Financial safety disclaimer appears in onboarding or first relevant answer.
- Backend hook-block behavior is visible as a readable app error/status.
- App can recover from backend/model downtime.
- Privacy inventory reviewed against actual SDKs and backend logs.
