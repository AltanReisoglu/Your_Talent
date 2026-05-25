"""JSON bridge for mobile-safe FinWiki wiki operations.

This script is intentionally a thin transport adapter. It exposes existing
FinWiki filesystem harness capabilities to non-Python frontends without moving
agent reasoning, model credentials, or direct wiki mutation logic into mobile
or C# code.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.serverless.wiki_manager import (  # noqa: E402
    append_audit,
    read_wiki_page,
    redact_private_data,
    search_wiki,
)


def _vault_root() -> Path:
    configured = os.environ.get("FINWIKI_VAULT_ROOT", "finwiki-vault")
    root = Path(configured)
    if not root.is_absolute():
        root = REPO_ROOT / root
    return root.resolve()


def _state_path(name: str) -> Path:
    path = _vault_root() / "state" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        f.write("\n")


def _split_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---\n"):
        return {}, content
    end = content.find("\n---", 4)
    if end == -1:
        return {}, content

    frontmatter: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in content[4:end].splitlines():
        line = raw_line.rstrip()
        if line.startswith("  - ") and current_key:
            frontmatter.setdefault(current_key, [])
            value = frontmatter[current_key]
            if isinstance(value, list):
                value.append(line[4:].strip().strip('"'))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        current_key = key.strip()
        clean = value.strip()
        if clean == "[]":
            frontmatter[current_key] = []
        elif clean.startswith("[") and clean.endswith("]"):
            frontmatter[current_key] = [
                item.strip().strip('"')
                for item in clean[1:-1].split(",")
                if item.strip()
            ]
        elif clean:
            frontmatter[current_key] = clean.strip('"')
        else:
            frontmatter[current_key] = []

    body_start = content.find("\n", end + 4)
    body = content[body_start + 1 :] if body_start != -1 else ""
    return frontmatter, body.lstrip()


def _coerce_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _page_summary(path: str, snippet: str = "") -> dict[str, Any]:
    content = read_wiki_page(path)
    if content.startswith("[WikiManager] Page not found"):
        return {
            "path": path,
            "title": path,
            "summary": snippet,
            "category": path.split("/", 1)[0] if "/" in path else "wiki",
            "last_updated": "",
            "review_status": "missing",
            "related": [],
        }
    frontmatter, body = _split_frontmatter(content)
    title = str(frontmatter.get("title") or path.rsplit("/", 1)[-1].replace(".md", ""))
    body_summary = " ".join(body.replace("#", " ").split())[:240]
    clean_snippet = " ".join(snippet.split())
    if clean_snippet.startswith("---") or "last_updated:" in clean_snippet[:160]:
        clean_snippet = ""
    return {
        "path": path,
        "title": title,
        "summary": clean_snippet or body_summary,
        "category": path.split("/", 1)[0] if "/" in path else "wiki",
        "last_updated": str(frontmatter.get("last_updated") or ""),
        "review_status": str(frontmatter.get("review_status") or "unknown"),
        "related": _coerce_list(frontmatter.get("related")),
    }


def _search(payload: dict[str, Any]) -> dict[str, Any]:
    query = str(payload.get("query") or payload.get("q") or "").strip()
    if not query:
        return {"results": []}
    category = payload.get("category")
    clean_category = str(category).strip() if category else None
    limit = int(payload.get("limit") or 10)
    raw_results = search_wiki(query=query, category=clean_category, limit=limit)

    results = []
    for raw in raw_results:
        path, _, rest = raw.partition(" | ")
        snippet = rest.split(":", 1)[1].strip() if ":" in rest else rest
        results.append(_page_summary(path.strip(), snippet=snippet))
    return {"results": results}


def _page(payload: dict[str, Any]) -> dict[str, Any]:
    path = str(payload.get("path") or "").strip()
    if not path:
        raise ValueError("path is required")
    content = read_wiki_page(path)
    if content.startswith("[WikiManager] Page not found"):
        return {
            "error": {
                "code": "wiki_page_not_found",
                "message": f"Wiki page not found: {path}",
                "retryable": False,
            }
        }
    frontmatter, body = _split_frontmatter(content)
    return {
        "page": {
            "path": path,
            "title": str(frontmatter.get("title") or path),
            "content": body,
            "frontmatter": frontmatter,
            "sources": _coerce_list(frontmatter.get("sources")),
            "related": _coerce_list(frontmatter.get("related")),
            "last_updated": str(frontmatter.get("last_updated") or ""),
            "review_status": str(frontmatter.get("review_status") or "unknown"),
        }
    }


def _ingest_submission(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id") or "mobile-guest").strip()
    submission_type = str(payload.get("type") or "note").strip().lower()
    content = redact_private_data(str(payload.get("content") or "").strip())
    notes = redact_private_data(str(payload.get("notes") or "").strip())
    if submission_type not in {"note", "url", "excerpt", "attachment"}:
        return {
            "error": {
                "code": "invalid_ingest_type",
                "message": "type must be note, url, excerpt, or attachment",
                "retryable": False,
            }
        }
    if not content:
        return {
            "error": {
                "code": "empty_ingest_content",
                "message": "content is required",
                "retryable": False,
            }
        }

    submission_id = f"ing_{uuid.uuid4().hex[:16]}"
    record = {
        "submission_id": submission_id,
        "created_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "user_id": user_id,
        "type": submission_type,
        "content": content,
        "notes": notes,
        "status": "queued",
    }
    _append_jsonl(_state_path("mobile-ingest-submissions.jsonl"), record)
    append_audit(
        "mobile_ingest_submission",
        submission_id,
        {"user_id": user_id, "type": submission_type, "status": "queued"},
        actor="mobile-api",
    )
    return {
        "submission_id": submission_id,
        "status": "queued",
        "message": "FinWiki ingest request queued",
    }


def _account_delete(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id") or "").strip()
    confirmation = bool(payload.get("confirmation"))
    if not user_id or not confirmation:
        return {
            "error": {
                "code": "delete_confirmation_required",
                "message": "user_id and confirmation=true are required",
                "retryable": False,
            }
        }

    effective_after = (datetime.utcnow() + timedelta(days=30)).date().isoformat()
    record = {
        "request_id": f"del_{uuid.uuid4().hex[:16]}",
        "created_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "user_id": user_id,
        "status": "requested",
        "effective_after": effective_after,
    }
    _append_jsonl(_state_path("account-deletion-requests.jsonl"), record)
    append_audit(
        "account_delete_requested",
        user_id,
        {"effective_after": effective_after},
        actor="mobile-api",
    )
    return {
        "status": "requested",
        "effective_after": effective_after,
        "retained_data_notice": "Security/audit records may be retained where legally required.",
    }


def handle(payload: dict[str, Any]) -> dict[str, Any]:
    operation = str(payload.get("operation") or "").strip()
    if operation == "search":
        return _search(payload)
    if operation == "page":
        return _page(payload)
    if operation == "ingest_submission":
        return _ingest_submission(payload)
    if operation == "account_delete":
        return _account_delete(payload)
    return {
        "error": {
            "code": "unknown_operation",
            "message": f"Unknown wiki API operation: {operation}",
            "retryable": False,
        }
    }


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    result = handle(payload)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
