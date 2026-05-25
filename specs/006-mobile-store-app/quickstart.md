# Quickstart: FinWiki Mobile Store App

This quickstart describes the current implementation workflow for the FinWiki
mobile app scaffold.

## 1. Create the mobile project

The mobile project lives in `mobile/finwiki` and uses Expo + TypeScript.

## 2. Configure API environment

Create mobile environment config for development and production:

```text
FINWIKI_API_BASE_URL=https://api.your-domain.example
```

The Expo public variable is:

```text
EXPO_PUBLIC_FINWIKI_API_BASE_URL=https://api.your-domain.example
```

The production app must use HTTPS and must not use `localhost`.

## 3. Start the backend locally for development

```bash
DOTNET_CLI_HOME=/tmp/dotnet \
FINWIKI_DOTNET_URL=http://0.0.0.0:8000 \
dotnet run --project dotnet-api/FinWiki.Api.csproj
```

For device testing, expose the backend through a secure tunnel or LAN URL.

## 4. Run app locally

```bash
cd mobile/finwiki
npm install
npm run typecheck
npx expo start
```

## 5. Build beta apps

```bash
npx eas build --platform ios --profile preview
npx eas build --platform android --profile preview
```

## 6. Store readiness checklist

Before TestFlight/Google closed testing:

- Privacy policy URL exists.
- Support URL exists.
- Account deletion path exists if accounts are enabled.
- App Privacy and Data Safety mappings are drafted from `docs/store/privacy-inventory.md`.
- Financial services declarations are reviewed.
- Test credentials or guest reviewer mode exists.
- Screenshots and descriptions avoid regulated financial-service claims.

## 7. Submission path

- iOS: TestFlight → external testing → App Store review.
- Android: internal testing → closed testing if required → production review.
