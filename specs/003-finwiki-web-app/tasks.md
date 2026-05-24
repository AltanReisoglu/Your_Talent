# Tasks: FinWiki Working Web Application

**Input**: Design documents from `specs/003-finwiki-web-app/`

**Prerequisites**: spec.md, plan.md

## Phase 1: Gateway UI Foundation

- [x] T001 Enable static file serving in `dotnet-api/Program.cs`
- [x] T002 Add browser UI shell in `dotnet-api/wwwroot/index.html`
- [x] T003 Add responsive UI styles in `dotnet-api/wwwroot/styles.css`
- [x] T004 Add invoke/health client logic in `dotnet-api/wwwroot/app.js`

## Phase 2: Runtime Observability

- [x] T005 Render response metadata and hook trace in the browser UI
- [x] T006 Add sample prompts and localStorage session persistence

## Phase 3: Documentation

- [x] T007 Update `README.md` with web app run and smoke-test workflow
- [x] T007a Add Hugging Face Router provider configuration to `agents/model_config.py`
- [x] T007b Document `HF_TOKEN`, `HF_MODEL`, and `FINWIKI_MODEL_PROVIDER=huggingface_openai`

## Phase 4: Validation

- [x] T008 Run Python syntax check
- [x] T009 Run C# build
- [x] T010 Run local health/root/invoke smoke tests
- [x] T011 Run secret scan
- [x] T012 Complete `evidence.md`
