"""Shared model configuration for FinWiki agents."""

import os
import subprocess

from langchain_core.language_models.chat_models import BaseChatModel

DEFAULT_FINWIKI_MODEL = "google_genai:gemini-2.5-flash"
VERTEX_OPENAI_PROVIDER = "vertex_openai"


def _truthy(value: str | None) -> bool:
    return (value or "").lower() in {"1", "true", "yes", "on"}


def _vertex_access_token() -> str:
    token = os.environ.get("VERTEX_AI_ACCESS_TOKEN")
    if token:
        return token

    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        raise RuntimeError(
            "Vertex AI OpenAI-compatible mode requires either "
            "VERTEX_AI_ACCESS_TOKEN or a working `gcloud auth print-access-token`."
        ) from exc

    return result.stdout.strip()


def _vertex_openai_model() -> BaseChatModel:
    from langchain_openai import ChatOpenAI

    endpoint = os.environ.get("VERTEX_AI_ENDPOINT") or os.environ.get(
        "ENDPOINT", "aiplatform.googleapis.com"
    )
    region = os.environ.get("VERTEX_AI_REGION") or os.environ.get("REGION", "global")
    project_id = (
        os.environ.get("VERTEX_AI_PROJECT_ID")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
        or os.environ.get("PROJECT_ID")
    )
    model = os.environ.get("VERTEX_AI_MODEL", "google/gemma-4-26b-a4b-it-maas")

    if not project_id:
        raise RuntimeError(
            "Vertex AI OpenAI-compatible mode requires VERTEX_AI_PROJECT_ID "
            "or GOOGLE_CLOUD_PROJECT."
        )

    base_url = (
        f"https://{endpoint}/v1/projects/{project_id}/locations/{region}"
        "/endpoints/openapi"
    )

    extra_body = {}
    if _truthy(os.environ.get("VERTEX_AI_ENABLE_THINKING", "true")):
        extra_body["chat_template_kwargs"] = {"enable_thinking": True}

    return ChatOpenAI(
        model=model,
        api_key=_vertex_access_token,
        base_url=base_url,
        timeout=float(os.environ.get("VERTEX_AI_TIMEOUT", "120")),
        max_retries=int(os.environ.get("VERTEX_AI_MAX_RETRIES", "2")),
        extra_body=extra_body or None,
    )


def finwiki_model() -> str | BaseChatModel:
    """Return the configured chat model for all FinWiki agents."""
    provider = os.environ.get("FINWIKI_MODEL_PROVIDER", "").lower()
    model = os.environ.get("FINWIKI_MODEL", DEFAULT_FINWIKI_MODEL)
    if provider == VERTEX_OPENAI_PROVIDER or model == VERTEX_OPENAI_PROVIDER:
        return _vertex_openai_model()
    return model
