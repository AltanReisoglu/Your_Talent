"""Deterministic hooks for the FinWiki agent harness.

Hooks live outside the model's memory. They enforce repeatable controls around
API invocations and tool calls, then leave auditable state on disk.
"""

from __future__ import annotations

import inspect
import json
import os
import re
import time
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK_STATE_DIR = REPO_ROOT / ".hook-state"
REPORTS_DIR = REPO_ROOT / "reports"
HOOK_AUDIT_LOG = REPORTS_DIR / "hook-audit.log"
LAST_QUALITY_GATE = HOOK_STATE_DIR / "last_quality_gate.json"

BLOCKED_PROMPT_PATTERNS = [
    re.compile(r"\b(cat|less|more|head|tail|print|read|show|summarize)\b.*\.env\b", re.I),
    re.compile(r"\b(api[_-]?key|secret|password|credential|access token|bearer token)\b", re.I),
    re.compile(r"\.git(?:/|\\|$)", re.I),
]

FINANCE_CONTEXT_TERMS = {
    "bist",
    "hisse",
    "stock",
    "valuation",
    "değerleme",
    "dcf",
    "wacc",
    "finans",
    "yatırım",
    "portfolio",
    "risk",
    "kap",
    "tcmb",
    "spk",
}

CODE_CHANGE_CONTEXT_TERMS = {
    "api",
    "build",
    "c#",
    "code",
    "commit",
    "deploy",
    "dotnet",
    "endpoint",
    "feature",
    "fix",
    "hook",
    "implement",
    "kod",
    "push",
    "refactor",
    "runtime",
    "test",
}

WRITE_TOOLS = {
    "write_wiki_page",
    "upsert_wiki_page",
    "update_index",
    "append_log",
    "register_source",
}

PATH_KEYS = {
    "path",
    "file_path",
    "relative_path",
    "page_path",
    "source_path",
    "target",
}


class HookBlocked(RuntimeError):
    """Raised when a hook blocks an action before it happens."""


@dataclass
class HookTrace:
    session_id: str
    user_id: str
    events: list[dict[str, Any]] = field(default_factory=list)

    def add(self, event: str, outcome: str, details: dict[str, Any] | None = None) -> None:
        self.events.append(
            {
                "timestamp": _now(),
                "event": event,
                "outcome": outcome,
                "details": _redact(details or {}),
            }
        )

    def summary(self) -> dict[str, Any]:
        return {
            "events": self.events,
            "last_quality_gate": _read_json(LAST_QUALITY_GATE),
        }


T = TypeVar("T", bound=Callable[..., Any])


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _ensure_dirs() -> None:
    HOOK_STATE_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)


def _append_audit(event: str, outcome: str, details: dict[str, Any] | None = None) -> None:
    _ensure_dirs()
    record = {
        "timestamp": _now(),
        "event": event,
        "outcome": outcome,
        "details": _redact(details or {}),
    }
    with HOOK_AUDIT_LOG.open("a", encoding="utf-8") as log:
        log.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"status": "invalid", "path": str(path)}


def _redact(value: Any) -> Any:
    secret_values = [
        os.environ.get("GOOGLE_API_KEY"),
        os.environ.get("TAVILY_API_KEY"),
        os.environ.get("LANGSMITH_API_KEY"),
        os.environ.get("VERTEX_AI_ACCESS_TOKEN"),
    ]
    if isinstance(value, str):
        for secret in secret_values:
            if secret:
                value = value.replace(secret, "[redacted]")
        value = re.sub(r"Bearer\s+[A-Za-z0-9._\-+/=]{20,}", "Bearer [redacted]", value)
        value = re.sub(r"AIza[A-Za-z0-9\-_]{35}", "[redacted-google-api-key]", value)
        return value
    if isinstance(value, dict):
        return {str(key): _redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _looks_financial(prompt: str) -> bool:
    lower = prompt.lower()
    return any(term in lower for term in FINANCE_CONTEXT_TERMS)


def _looks_code_change(prompt: str) -> bool:
    lower = prompt.lower()
    return any(term in lower for term in CODE_CHANGE_CONTEXT_TERMS)


def _iter_path_values(payload: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key, value in payload.items():
        if key in PATH_KEYS and isinstance(value, str):
            paths.append(value)
        elif isinstance(value, dict):
            paths.extend(_iter_path_values(value))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    paths.extend(_iter_path_values(item))
                elif isinstance(item, str) and ("/" in item or item.startswith(".")):
                    paths.append(item)
    return paths


def session_start(user_id: str, session_id: str) -> tuple[HookTrace, str]:
    trace = HookTrace(session_id=session_id, user_id=user_id)
    context = (
        "FinWiki hook context: enforce no secret exposure, keep raw sources "
        "immutable, preserve policy memory as read-only, cite financial claims, "
        "avoid personalized investment advice, and use Spec Kit artifacts for "
        "non-trivial AI-assisted code changes."
    )
    trace.add("SessionStart", "context_added", {"context": context})
    _append_audit("SessionStart", "context_added", {"user_id": user_id, "session_id": session_id})
    return trace, context


def user_prompt_submit(prompt: str, trace: HookTrace) -> str:
    for pattern in BLOCKED_PROMPT_PATTERNS:
        if pattern.search(prompt):
            reason = "Prompt requests secrets, credentials, .env, or .git access."
            trace.add("UserPromptSubmit", "blocked", {"reason": reason})
            _append_audit("UserPromptSubmit", "blocked", {"reason": reason})
            raise HookBlocked(reason)

    contexts = []
    if _looks_financial(prompt):
        contexts.append(
            "Financial request detected: provide research/education framing, "
            "include risks and assumptions, and do not give direct buy/sell advice."
        )

    if _looks_code_change(prompt):
        contexts.append(
            "Code-change request detected: follow the Spec Kit workflow in "
            ".specify/memory/constitution.md. Use specs/<feature>/spec.md, "
            "plan.md, tasks.md, and evidence.md for non-trivial changes."
        )

    if contexts:
        trace.add("UserPromptSubmit", "context_added", {"contexts": contexts})
        hook_context = "\n".join(f"- {item}" for item in contexts)
        return f"<hook_context>\n{hook_context}\n</hook_context>\n\n{prompt}"

    trace.add("UserPromptSubmit", "allowed", {})
    return prompt


def pre_tool_use(tool_name: str, tool_input: dict[str, Any]) -> None:
    paths = _iter_path_values(tool_input)
    for raw_path in paths:
        normalized = raw_path.replace("\\", "/").strip()
        lower = normalized.lower()
        if ".env" in lower or lower.startswith(".git/") or "/.git/" in lower:
            reason = f"{raw_path} is protected by FinWiki hooks."
            _append_audit("PreToolUse", "blocked", {"tool": tool_name, "reason": reason})
            raise HookBlocked(reason)
        if tool_name in WRITE_TOOLS and (lower.startswith("raw/") or lower.startswith("/raw/")):
            reason = "raw sources are immutable; write to wiki or manifest instead."
            _append_audit("PreToolUse", "blocked", {"tool": tool_name, "reason": reason})
            raise HookBlocked(reason)
        if tool_name in WRITE_TOOLS and (lower.startswith("policies/") or lower.startswith("/policies/")):
            reason = "policies are read-only memory."
            _append_audit("PreToolUse", "blocked", {"tool": tool_name, "reason": reason})
            raise HookBlocked(reason)

    _append_audit("PreToolUse", "allowed", {"tool": tool_name, "paths": paths})


def post_tool_use(tool_name: str, tool_input: dict[str, Any], result: Any, status: str) -> None:
    _ensure_dirs()
    record = {
        "timestamp": _now(),
        "tool": tool_name,
        "status": status,
        "input": _redact(tool_input),
        "result_preview": _redact(str(result)[:500]),
    }
    if tool_name in WRITE_TOOLS:
        LAST_QUALITY_GATE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _append_audit("PostToolUse", status, {"tool": tool_name})


def stop(response: str, trace: HookTrace) -> str:
    if not response.strip():
        reason = "Agent produced an empty response."
        trace.add("Stop", "blocked", {"reason": reason})
        _append_audit("Stop", "blocked", {"reason": reason})
        raise HookBlocked(reason)

    last_gate = _read_json(LAST_QUALITY_GATE)
    if last_gate and last_gate.get("status") == "failed":
        reason = "Last quality gate failed. Resolve it before completing."
        trace.add("Stop", "blocked", {"reason": reason, "last_quality_gate": last_gate})
        _append_audit("Stop", "blocked", {"reason": reason})
        raise HookBlocked(reason)

    trace.add("Stop", "allowed", {"response_length": len(response)})
    _append_audit("Stop", "allowed", {"response_length": len(response)})
    return response


def session_end(trace: HookTrace, status: str, error: str | None = None) -> None:
    details = {
        "user_id": trace.user_id,
        "session_id": trace.session_id,
        "status": status,
        "error": error,
        "events": trace.events,
    }
    trace.add("SessionEnd", status, {"error": error})
    _append_audit("SessionEnd", status, details)


def hooked_tool(func: T) -> T:
    signature = inspect.signature(func)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = signature.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        tool_input = dict(bound.arguments)
        pre_tool_use(func.__name__, tool_input)
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            post_tool_use(func.__name__, tool_input, exc, "failed")
            raise
        post_tool_use(func.__name__, tool_input, result, "passed")
        return result

    return wrapper  # type: ignore[return-value]
