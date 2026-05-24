# Evidence Bundle: FinWiki Working Web Application

**Feature Branch**: `003-finwiki-web-app`
**Spec**: `specs/003-finwiki-web-app/spec.md`
**Plan**: `specs/003-finwiki-web-app/plan.md`
**Tasks**: `specs/003-finwiki-web-app/tasks.md`
**Date**: 2026-05-23

## Summary

Implemented a working local browser application for FinWiki. The C# gateway now
serves static UI assets at `/`, keeps `/health` and `/invoke`, and continues to
delegate agent execution to the existing Python bridge. The UI renders response
text, request metadata, sample prompts, localStorage-backed session IDs, and hook
trace JSON. The Python model configuration now supports Hugging Face Router via
`FINWIKI_MODEL_PROVIDER=huggingface_openai` or `hf_router`.

## Checks Run

| Check | Command | Result | Notes |
|-------|---------|--------|-------|
| Python syntax | `.venv/bin/python -m py_compile app/hooks.py scripts/invoke_agent.py scripts/spec_evidence_check.py agents/model_config.py` | passed | No syntax errors |
| C# build | `env DOTNET_CLI_HOME=/tmp/dotnet dotnet build dotnet-api/FinWiki.Api.csproj` | passed | 0 warnings, 0 errors |
| HTTP health | `curl -sS http://127.0.0.1:8002/health` | passed | Returned `{"status":"ok","service":"finwiki-dotnet-api"}` |
| HTTP root | `curl -sS http://127.0.0.1:8002/` | passed | Returned FinWiki HTML app shell |
| Hook-block invoke | `curl -sS -X POST http://127.0.0.1:8002/invoke ...` | passed | Returned `Blocked by FinWiki hook` without model call |
| HF missing-token check | `env -u HF_TOKEN -u HUGGINGFACEHUB_API_TOKEN FINWIKI_MODEL_PROVIDER=huggingface_openai .venv/bin/python -c ...` | passed | Returned clear `HF_TOKEN or HUGGINGFACEHUB_API_TOKEN` requirement |
| HF live Router call | `env FINWIKI_MODEL_PROVIDER=huggingface_openai .venv/bin/python -c ...` | passed | Returned `TAMAM` from Hugging Face Router |
| HF Python service invoke | `env FINWIKI_MODEL_PROVIDER=huggingface_openai .venv/bin/python -c "from app.service import invoke_agent ..."` | passed | Returned `TAMAM` through FinWiki service + hooks |
| HF C# gateway invoke | `curl -sS -X POST http://127.0.0.1:8003/invoke ...` | passed | Returned `TAMAM` through browser gateway path |
| Secret scan | `rg -n "AIza|lsv2_|tvly-|HF_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_API_KEY|TAVILY_API_KEY|LANGSMITH_API_KEY|BEGIN (RSA |EC |OPENSSH |PRIVATE|PUBLIC) KEY" AGENTS.md README.md app scripts dotnet-api agents/model_config.py .env.example specs/003-finwiki-web-app` | passed | Only env var names and redaction regex references found |

## Checks Not Run

- Full live model invoke was not run to avoid quota/cost during UI smoke testing.
  The hook-block request validates the full browser-to-C#-to-Python path without
  calling the model.
- Multimodal Hugging Face image-url request was not run through FinWiki because
  the current app only exposes text chat messages.
- Browser visual screenshot automation was not run; HTTP root returned the full
  app shell and the UI uses static HTML/CSS/JS.

## Residual Risks

- This is a local single-user app surface. Production auth, multi-user tenancy,
  streaming, and persistent server-side sessions remain future work.
- If the Python model provider is misconfigured or out of quota, normal `/invoke`
  calls will return gateway errors; hook-block smoke tests still pass.
- Hugging Face Router model availability and multimodal support depend on the
  selected `HF_MODEL` and router provider backend. Text chat is confirmed.

## Changed Artifacts

- `dotnet-api/Program.cs`
- `dotnet-api/wwwroot/index.html`
- `dotnet-api/wwwroot/styles.css`
- `dotnet-api/wwwroot/app.js`
- `app/hooks.py`
- `agents/model_config.py`
- `.env.example`
- `README.md`
- `AGENTS.md`
- `specs/003-finwiki-web-app/`

## Reviewer Notes

- The C# layer remains a gateway/UI layer. Agent reasoning, hooks, memory, and
  wiki mutation stay in Python.
- Local smoke tests used `127.0.0.1:8002`; README keeps `8000` as the default and
  documents `FINWIKI_DOTNET_URL` for port overrides.
