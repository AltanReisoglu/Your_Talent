"""
FinWiki File-System Harness
Andrej Karpathy LLM Wiki mantığı için read/write araçları.
"""

import hashlib
import json
import math
import os
import re
import uuid
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from app.hooks import hooked_tool

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_configured_vault_root = os.environ.get(
    "FINWIKI_VAULT_ROOT", os.path.join(_REPO_ROOT, "finwiki-vault")
)
if not os.path.isabs(_configured_vault_root):
    _configured_vault_root = os.path.join(_REPO_ROOT, _configured_vault_root)
_VAULT_ROOT = os.path.abspath(_configured_vault_root)
_WIKI_ROOT = os.path.join(_VAULT_ROOT, "wiki")
_PROJECT_ROOT = _VAULT_ROOT
_MANIFEST_PATH = os.path.join(_WIKI_ROOT, ".manifest.json")
_LOG_ROOT = os.path.join(_PROJECT_ROOT, "logs")
_AUDIT_LOG_PATH = os.path.join(_LOG_ROOT, "audit-log.jsonl")
_OBSERVATION_LOG_PATH = os.path.join(_LOG_ROOT, "agent-observations.jsonl")
_MEMORY_EVENT_LOG_PATH = os.path.join(_LOG_ROOT, "memory-events.jsonl")
_STATE_ROOT = os.path.join(_VAULT_ROOT, "state")
_DAY_STATE_PATH = os.path.join(_STATE_ROOT, "day-state.md")
_MAINTENANCE_ROOT = os.path.join(_WIKI_ROOT, "maintenance")
_EXPIRY_REVIEW_PATH = os.path.join(_MAINTENANCE_ROOT, "expiry-review.md")
_MEMORY_GOVERNANCE_PATH = os.path.join(_MAINTENANCE_ROOT, "memory-governance.md")

_SECRET_PATTERNS = [
    re.compile(
        r"(?:api[_-]?key|secret|token|password|credential|auth)\s*[=:]\s*[\"']?[A-Za-z0-9_\-/.+]{20,}[\"']?",
        re.IGNORECASE,
    ),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-+/=]{20,}", re.IGNORECASE),
    re.compile(r"sk-proj-[A-Za-z0-9\-_]{20,}"),
    re.compile(r"(?:sk|pk|rk|ak)-[A-Za-z0-9][A-Za-z0-9\-_]{19,}"),
    re.compile(r"sk-ant-[A-Za-z0-9\-_]{20,}"),
    re.compile(r"gh[pus]_[A-Za-z0-9]{36,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{22,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[A-Za-z0-9\-_]{35}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
]

_PRIVATE_TAG_RE = re.compile(r"<private>[\s\S]*?</private>", re.IGNORECASE)

_FRESHNESS_THRESHOLDS = {
    "companies": 30,
    "markets": 14,
    "macro": 30,
    "regulation": 45,
    "risk": 60,
    "instruments": 90,
    "strategies": 30,
    "concepts": 180,
    "models": 120,
    "sources": 90,
}

_AUTHORITY_ORDER = {
    "direct_instruction": 800,
    "canonical_policy": 700,
    "day_state": 600,
    "project_memory": 500,
    "sourced_wiki": 450,
    "behavior_memory": 400,
    "retrieval_summary": 250,
    "compressed_summary": 100,
}

_DEFAULT_AUTHORITY_LEVEL = {
    "direct_instruction": "operational",
    "canonical_policy": "canonical",
    "day_state": "operational",
    "project_memory": "memory",
    "sourced_wiki": "sourced",
    "behavior_memory": "memory",
    "retrieval_summary": "summary",
    "compressed_summary": "summary",
}

_DEFAULT_DECISION_SCOPE = {
    "direct_instruction": "final",
    "canonical_policy": "final",
    "day_state": "hint",
    "project_memory": "hint",
    "sourced_wiki": "evidence",
    "behavior_memory": "hint",
    "retrieval_summary": "background",
    "compressed_summary": "background",
}

_MEMORY_V2_FRONTMATTER_DEFAULTS = {
    "authority_level": "synthesis",
    "decision_scope": "evidence",
    "valid_from": "",
    "valid_until": "",
    "freshness_policy": "event_driven",
    "supersedes": [],
    "superseded_by": [],
}

_CATEGORY_HEADINGS = {
    "concepts": "Concepts",
    "instruments": "Instruments",
    "markets": "Markets",
    "companies": "Companies",
    "macro": "Macroeconomics",
    "macroeconomics": "Macroeconomics",
    "regulation": "Regulation",
    "regulations": "Regulation",
    "risk": "Risk",
    "risks": "Risk",
    "models": "Models",
    "sources": "Sources",
    "strategies": "Strategies",
}

_CATEGORY_DIRS = {
    "concepts": "concepts",
    "instruments": "instruments",
    "markets": "markets",
    "companies": "companies",
    "macro": "macro",
    "macroeconomics": "macro",
    "regulation": "regulation",
    "regulations": "regulation",
    "risk": "risk",
    "risks": "risk",
    "models": "models",
    "sources": "sources",
    "strategies": "strategies",
}


def _resolve_path(relative_path: str) -> str:
    # Güvenlik: sadece WIKI_ROOT altına yaz
    clean = relative_path.strip("/\\")
    clean = os.path.normpath(clean)
    full = os.path.abspath(os.path.join(_WIKI_ROOT, clean))
    if not full.startswith(_WIKI_ROOT + os.sep) and full != _WIKI_ROOT:
        raise ValueError("Invalid wiki path: outside wiki root")
    return full


def _normalize_category(category: str) -> str:
    clean = category.strip().lower().replace(" ", "-")
    if clean not in _CATEGORY_HEADINGS:
        valid = ", ".join(sorted(_CATEGORY_DIRS))
        raise ValueError(f"Invalid category '{category}'. Valid categories: {valid}")
    return clean


def _slugify(value: str) -> str:
    slug = value.strip().lower()
    slug = slug.replace("&", " and ")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "untitled"


def _frontmatter_list(values: Optional[List[str]]) -> str:
    if not values:
        return "[]"
    lines = []
    for value in values:
        escaped = value.replace('"', '\\"')
        lines.append(f'  - "{escaped}"')
    return "\n" + "\n".join(lines)


def _coerce_list(value: object) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        clean = value.strip()
        if not clean or clean == "[]":
            return []
        if clean.startswith("[") and clean.endswith("]"):
            return [
                item.strip().strip('"').strip("'")
                for item in clean[1:-1].split(",")
                if item.strip()
            ]
        return [clean]
    return [str(value)]


def _split_frontmatter(content: str) -> Tuple[Dict[str, object], str]:
    if not content.startswith("---"):
        return {}, content
    match = re.match(r"---\n(.*?)\n---\n?", content, re.DOTALL)
    if not match:
        return {}, content
    fields = _extract_frontmatter(content)
    body = content[match.end():]
    return fields, body


def _render_frontmatter_value(key: str, value: object) -> List[str]:
    if isinstance(value, list):
        if not value:
            return [f"{key}: []"]
        lines = [f"{key}:"]
        for item in value:
            escaped = str(item).replace('"', '\\"')
            lines.append(f'  - "{escaped}"')
        return lines
    if value is None:
        return [f"{key}: "]
    if isinstance(value, bool):
        return [f"{key}: {'true' if value else 'false'}"]
    return [f"{key}: {value}"]


def _render_frontmatter(fields: Dict[str, object]) -> str:
    preferred_order = [
        "title",
        "tags",
        "domain",
        "last_updated",
        "review_status",
        "authority_level",
        "decision_scope",
        "valid_from",
        "valid_until",
        "freshness_policy",
        "aliases",
        "sources",
        "related",
        "supersedes",
        "superseded_by",
        "stale_reason",
    ]
    lines = ["---"]
    rendered = set()
    for key in preferred_order:
        if key in fields:
            lines.extend(_render_frontmatter_value(key, fields[key]))
            rendered.add(key)
    for key in sorted(k for k in fields if k not in rendered):
        lines.extend(_render_frontmatter_value(key, fields[key]))
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def _update_frontmatter(content: str, updates: Dict[str, object]) -> str:
    fields, body = _split_frontmatter(content)
    fields.update(updates)
    return _render_frontmatter(fields) + body.lstrip("\n")


def _parse_date(value: object) -> Optional[datetime]:
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _validity_status(fields: Dict[str, object]) -> Tuple[str, Optional[int]]:
    review_status = str(fields.get("review_status", "")).strip().lower()
    if review_status in {"expired", "superseded", "stale"}:
        return review_status, None
    valid_until = _parse_date(fields.get("valid_until"))
    if valid_until:
        delta = (datetime.now() - valid_until).days
        if delta > 0:
            return "expired", delta
    return "active", None


def _page_memory_status(content: str) -> Tuple[str, Optional[int]]:
    fields = _extract_frontmatter(content)
    status, days = _validity_status(fields)
    if status != "active":
        return status, days
    age = _page_age_days(content)
    if age is None:
        return "missing-last-updated", None
    threshold = _FRESHNESS_THRESHOLDS.get(
        _page_category(str(fields.get("page_path", ""))), 60
    )
    if age > threshold * 2:
        return "critical-stale", age
    if age > threshold:
        return "stale", age
    return "fresh", age


def _read_manifest() -> Dict[str, Dict[str, object]]:
    if not os.path.exists(_MANIFEST_PATH):
        return {"sources": {}}
    with open(_MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_manifest(manifest: Dict[str, Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(_MANIFEST_PATH), exist_ok=True)
    with open(_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")


def _append_jsonl(path: str, entry: Dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True))
        f.write("\n")


def _redact_value(value: object) -> object:
    if isinstance(value, str):
        return redact_private_data(value)
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _redact_value(item) for key, item in value.items()}
    return value


def _now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def _tokenize(text: str) -> List[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9][a-z0-9_\-./]*", text.lower())
        if len(token) > 1
    ]


def _extract_frontmatter(content: str) -> Dict[str, object]:
    if not content.startswith("---"):
        return {}
    match = re.match(r"---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fields: Dict[str, object] = {}
    current_key: Optional[str] = None
    for raw_line in match.group(1).splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            fields.setdefault(current_key, [])
            if isinstance(fields[current_key], list):
                fields[current_key].append(line[4:].strip().strip('"'))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        current_key = key.strip()
        clean_value = value.strip()
        if clean_value == "[]":
            fields[current_key] = []
        elif clean_value.startswith("[") and clean_value.endswith("]"):
            fields[current_key] = [
                item.strip().strip('"')
                for item in clean_value[1:-1].split(",")
                if item.strip()
            ]
        elif clean_value:
            fields[current_key] = clean_value.strip('"')
        else:
            fields[current_key] = []
    return fields


def _extract_sources_from_page(content: str) -> List[str]:
    sources = []
    frontmatter = _extract_frontmatter(content)
    fm_sources = frontmatter.get("sources")
    if isinstance(fm_sources, list):
        sources.extend(str(source) for source in fm_sources)
    elif isinstance(fm_sources, str):
        sources.append(fm_sources)
    sources.extend(re.findall(r"\[(?:Source|Kaynak):\s*([^\]]+)\]", content))
    for line in content.splitlines():
        if line.strip().lower().startswith("- [source:"):
            sources.append(line.split(":", 1)[1].strip(" ]"))
    return sorted({source.strip() for source in sources if source.strip()})


def _page_category(page_path: str) -> str:
    return page_path.split("/", 1)[0] if "/" in page_path else "concepts"


def _page_age_days(content: str) -> Optional[int]:
    match = re.search(r"last_updated:\s*(\d{4}-\d{2}-\d{2})", content)
    if not match:
        return None
    updated = datetime.strptime(match.group(1), "%Y-%m-%d")
    return (datetime.now() - updated).days


def redact_private_data(text: str) -> str:
    """Redact secrets and private blocks before durable logs or source notes.

    This is inspired by agentmemory's pre-store privacy filter. It is not a
    compliance boundary by itself; it prevents accidental leakage into local
    wiki support logs.
    """
    result = _PRIVATE_TAG_RE.sub("[REDACTED]", text)
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub("[REDACTED_SECRET]", result)
    return result


def append_audit(
    operation: str,
    target: str,
    details: Optional[Dict[str, object]] = None,
    actor: str = "finwiki",
) -> str:
    """Append a structured audit event for wiki/memory mutations.

    This is separate from `/wiki/log.md`: log.md is human chronology, while
    audit-log.jsonl is machine-readable provenance for mutations.
    """
    event = {
        "id": f"aud_{uuid.uuid4().hex[:16]}",
        "timestamp": _now_iso(),
        "operation": operation,
        "target": target,
        "actor": actor,
        "details": _redact_value(details or {}),
    }
    _append_jsonl(_AUDIT_LOG_PATH, event)
    return f"[WikiManager] Audit logged: {operation} | {target}"


def observe_agent_event(
    event_type: str,
    summary: str,
    payload: Optional[Dict[str, object]] = None,
    sources: Optional[List[str]] = None,
    related_pages: Optional[List[str]] = None,
    importance: int = 5,
) -> str:
    """Record an agent observation without promoting it to wiki fact.

    Use for session lessons, routing decisions, tool outcomes, and workflow
    signals. Financial facts still go through wiki ingest and source manifest.
    """
    clean_importance = max(1, min(10, int(importance)))
    event = {
        "id": f"obs_{uuid.uuid4().hex[:16]}",
        "timestamp": _now_iso(),
        "event_type": event_type,
        "summary": redact_private_data(summary),
        "payload": _redact_value(payload or {}),
        "sources": sources or [],
        "related_pages": related_pages or [],
        "importance": clean_importance,
    }
    _append_jsonl(_OBSERVATION_LOG_PATH, event)
    append_audit("observe", event["id"], {"event_type": event_type})
    return f"[WikiManager] Observation recorded: {event['id']}"


@hooked_tool
def emit_memory_event(
    event_type: str,
    target: str,
    payload: Optional[Dict[str, object]] = None,
    actor: str = "finwiki",
) -> str:
    """Append an event-sourced memory governance record.

    The event log is the machine-readable proof layer behind the Obsidian
    vault. It is intentionally lightweight: JSONL is enough for replay,
    projection, and audit without adding another runtime dependency.
    """
    event = {
        "event_id": f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:10]}",
        "created_at": _now_iso(),
        "event_type": event_type,
        "target": target,
        "actor": actor,
        "payload": _redact_value(payload or {}),
    }
    _append_jsonl(_MEMORY_EVENT_LOG_PATH, event)
    append_audit(
        "emit_memory_event",
        target,
        {"event_type": event_type, "event_id": event["event_id"]},
        actor=actor,
    )
    return str(event["event_id"])


def _read_memory_events(limit: Optional[int] = None) -> Tuple[List[Dict[str, object]], List[str]]:
    if not os.path.exists(_MEMORY_EVENT_LOG_PATH):
        return [], []
    events: List[Dict[str, object]] = []
    errors: List[str] = []
    with open(_MEMORY_EVENT_LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    selected = lines[-limit:] if limit else lines
    offset = len(lines) - len(selected)
    for index, line in enumerate(selected, start=offset + 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {index}: {exc.msg}")
            continue
        if isinstance(value, dict):
            events.append(value)
        else:
            errors.append(f"line {index}: event is not an object")
    return events, errors


def _memory_event_projection(limit: int = 50) -> Dict[str, object]:
    events, errors = _read_memory_events(limit)
    nodes: Dict[str, Dict[str, object]] = {}
    relations: List[Dict[str, str]] = []
    stale_items: List[str] = []
    contradictions: List[str] = []
    recent_decisions: List[str] = []

    def node(node_id: str, node_type: str, data: Optional[Dict[str, object]] = None) -> None:
        nodes.setdefault(node_id, {"id": node_id, "type": node_type, "data": {}})
        if data:
            existing = nodes[node_id].setdefault("data", {})
            if isinstance(existing, dict):
                existing.update(data)

    for event in events:
        event_type = str(event.get("event_type", "unknown"))
        target = str(event.get("target", "unknown"))
        event_id = str(event.get("event_id", ""))
        payload = event.get("payload", {})
        payload_dict = payload if isinstance(payload, dict) else {}
        node(event_id, "event", {"event_type": event_type, "target": target})

        if event_type.startswith("source."):
            node(target, "source", payload_dict)
            relations.append({"from": event_id, "to": target, "type": "records"})
        elif event_type.startswith("page."):
            node(target, "wiki_page", payload_dict)
            relations.append({"from": event_id, "to": target, "type": "updates"})
            for source in _coerce_list(payload_dict.get("sources")):
                node(source, "source", {})
                relations.append({"from": source, "to": target, "type": "supports"})
            if event_type in {"page.stale", "page.superseded"}:
                stale_items.append(target)
                relations.append({"from": target, "to": event_id, "type": "requires_review"})
                for replacement in _coerce_list(payload_dict.get("replacement")):
                    node(replacement, "wiki_page", {})
                    relations.append({"from": target, "to": replacement, "type": "superseded_by"})
        elif event_type.startswith("claim."):
            node(target, "claim", payload_dict)
            relations.append({"from": event_id, "to": target, "type": "records"})
            if event_type in {"claim.expired", "claim.stale", "page.stale", "page.superseded"}:
                stale_items.append(target)
            for replacement in _coerce_list(payload_dict.get("replacement")):
                node(replacement, "claim_or_page", {})
                relations.append({"from": target, "to": replacement, "type": "superseded_by"})
            if payload_dict.get("contradiction"):
                contradictions.append(target)
        elif event_type == "authority.decision":
            node(target, "authority_decision", payload_dict)
            relations.append({"from": event_id, "to": target, "type": "decides"})
            recent_decisions.append(target)
        elif event_type == "day_state.updated":
            node(target, "day_state", payload_dict)
            relations.append({"from": event_id, "to": target, "type": "updates"})
        elif event_type.startswith("maintenance."):
            node(target, "maintenance_issue", payload_dict)
            relations.append({"from": event_id, "to": target, "type": "requires_review"})

    return {
        "nodes": nodes,
        "relations": relations,
        "stale_items": stale_items,
        "contradictions": contradictions,
        "recent_decisions": recent_decisions,
        "errors": errors,
        "generated_at": _now_iso(),
    }


def _write_expiry_review_page(projection: Optional[Dict[str, object]] = None) -> None:
    projection = projection or _memory_event_projection(limit=200)
    os.makedirs(_MAINTENANCE_ROOT, exist_ok=True)
    stale_items = projection.get("stale_items", [])
    if not isinstance(stale_items, list):
        stale_items = []
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "---",
        "title: Memory Expiry Review",
        "tags:",
        "  - finance",
        "  - memory-governance",
        "domain: financial-services",
        f"last_updated: {today}",
        "review_status: active",
        "authority_level: operational",
        "decision_scope: hint",
        "valid_from: ",
        "valid_until: ",
        "freshness_policy: daily",
        "aliases: []",
        'sources:',
        '  - "memory-events.jsonl"',
        "related:",
        '  - "memory-governance"',
        "supersedes: []",
        "superseded_by: []",
        "---",
        "",
        "# Memory Expiry Review",
        "",
        "This page is generated from FinWiki memory governance events.",
        "",
        "## Open Stale / Expired Items",
    ]
    if stale_items:
        lines.extend(f"- [[{str(item).removesuffix('.md')}]] — review required" for item in stale_items)
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Review Rule",
            "",
            "Expired or stale memory can provide context, but it cannot make a final financial claim without refresh.",
        ]
    )
    with open(_EXPIRY_REVIEW_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")


def _write_memory_governance_page(projection: Optional[Dict[str, object]] = None) -> None:
    projection = projection or _memory_event_projection(limit=100)
    os.makedirs(_MAINTENANCE_ROOT, exist_ok=True)
    nodes = projection.get("nodes", {})
    relations = projection.get("relations", [])
    errors = projection.get("errors", [])
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "---",
        "title: Memory Governance",
        "tags:",
        "  - finance",
        "  - memory-governance",
        "domain: financial-services",
        f"last_updated: {today}",
        "review_status: active",
        "authority_level: operational",
        "decision_scope: hint",
        "valid_from: ",
        "valid_until: ",
        "freshness_policy: daily",
        "aliases: []",
        'sources:',
        '  - "memory-events.jsonl"',
        "related:",
        '  - "expiry-review"',
        '  - "day-state"',
        "supersedes: []",
        "superseded_by: []",
        "---",
        "",
        "# Memory Governance",
        "",
        "FinWiki uses Remember, Cite, Forget as the trust contract.",
        "",
        "## Projection Summary",
        f"- Nodes: {len(nodes) if isinstance(nodes, dict) else 0}",
        f"- Relations: {len(relations) if isinstance(relations, list) else 0}",
        f"- Generated at: {projection.get('generated_at', 'unknown')}",
        "",
        "## Layers",
        "- Remember: direct instruction, canonical policy, day-state, project memory, sourced wiki, behavior memory, retrieval summary, compressed summary.",
        "- Cite: final claims require source path, authority, and freshness metadata.",
        "- Forget: stale facts are demoted, expired, or superseded without deleting historical evidence.",
        "",
        "## Projection Errors",
    ]
    if errors:
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("- None")
    with open(_MEMORY_GOVERNANCE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")


def _source_fingerprint(source_path: str) -> Dict[str, object]:
    absolute = os.path.abspath(os.path.join(_PROJECT_ROOT, source_path))
    if os.path.exists(absolute) and os.path.isfile(absolute):
        digest = hashlib.sha256()
        with open(absolute, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
        stat = os.stat(absolute)
        return {
            "kind": "file",
            "path": os.path.relpath(absolute, _PROJECT_ROOT),
            "sha256": digest.hexdigest(),
            "mtime": int(stat.st_mtime),
            "size": stat.st_size,
        }
    return {
        "kind": "external",
        "path": source_path,
        "sha256": hashlib.sha256(source_path.encode("utf-8")).hexdigest(),
    }


def _attempts_policy_weaken(content: str) -> bool:
    lower = content.lower()
    weak_terms = [
        "ignore citation",
        "ignore citations",
        "skip citation",
        "without citation",
        "ignore compliance",
        "bypass compliance",
        "override policy",
        "disable policy",
        "ignore policy",
    ]
    return any(term in lower for term in weak_terms)


def _normalize_memory_candidate(candidate: Dict[str, object], index: int = 0) -> Dict[str, object]:
    layer = str(candidate.get("layer") or candidate.get("type") or "retrieval_summary")
    candidate_id = str(candidate.get("id") or f"candidate-{index + 1}")
    content = str(candidate.get("content") or candidate.get("text") or candidate.get("summary") or "")
    source_path = str(candidate.get("source_path") or candidate.get("source") or "").strip()
    authority_level = str(
        candidate.get("authority_level") or _DEFAULT_AUTHORITY_LEVEL.get(layer, "unknown")
    )
    decision_scope = str(
        candidate.get("decision_scope") or _DEFAULT_DECISION_SCOPE.get(layer, "background")
    )
    normalized = {
        "id": candidate_id,
        "layer": layer,
        "content": content,
        "source_path": source_path,
        "created_at": candidate.get("created_at") or candidate.get("last_updated") or "",
        "observed_at": _now_iso(),
        "authority_level": authority_level,
        "decision_scope": decision_scope,
        "valid_from": candidate.get("valid_from") or "",
        "valid_until": candidate.get("valid_until") or "",
        "freshness_policy": candidate.get("freshness_policy") or "none",
        "stale_reason": candidate.get("stale_reason") or "",
    }
    status, expired_days = _validity_status(normalized)
    normalized["freshness_status"] = status
    if expired_days is not None:
        normalized["expired_days"] = expired_days

    missing_source = not source_path and layer not in {"direct_instruction", "compressed_summary"}
    normalized["missing_source"] = missing_source
    if missing_source and decision_scope == "final":
        normalized["decision_scope"] = "hint"
    if status in {"expired", "stale", "superseded"} and normalized["decision_scope"] == "final":
        normalized["decision_scope"] = "hint"
    if layer == "direct_instruction" and _attempts_policy_weaken(content):
        normalized["policy_weakening"] = True
        normalized["decision_scope"] = "background"
    return normalized


def _candidate_score(candidate: Dict[str, object]) -> int:
    layer = str(candidate.get("layer", "retrieval_summary"))
    score = _AUTHORITY_ORDER.get(layer, 0)
    if candidate.get("policy_weakening"):
        score -= 650
    if candidate.get("freshness_status") in {"expired", "stale", "superseded"}:
        score -= 250
    if candidate.get("missing_source"):
        score -= 150
    if candidate.get("authority_level") == "canonical":
        score += 40
    if candidate.get("authority_level") == "sourced":
        score += 25
    return score


def _candidate_from_page(page_path: str, index: int) -> Optional[Dict[str, object]]:
    content = read_wiki_page(page_path)
    if content.startswith("[WikiManager] Page not found"):
        return None
    fields = _extract_frontmatter(content)
    title = fields.get("title") or page_path
    sources = _extract_sources_from_page(content)
    return {
        "id": f"page-{index + 1}",
        "layer": "sourced_wiki",
        "content": str(title),
        "source_path": page_path if sources else "",
        "created_at": fields.get("last_updated") or "",
        "authority_level": fields.get("authority_level") or "sourced",
        "decision_scope": fields.get("decision_scope") or "evidence",
        "valid_from": fields.get("valid_from") or "",
        "valid_until": fields.get("valid_until") or "",
        "freshness_policy": fields.get("freshness_policy") or "event_driven",
        "stale_reason": fields.get("stale_reason") or "",
    }


@hooked_tool
def resolve_memory_authority(
    query: str,
    candidates: Optional[List[Dict[str, object]]] = None,
    page_paths: Optional[List[str]] = None,
) -> str:
    """Rank memory candidates before they influence an answer.

    This is the Cite layer of the Memory v2 contract: it reports which memory
    can affect the final decision, which memory is only background, and whether
    refresh or human confirmation is needed.
    """
    raw_candidates = list(candidates or [])
    for index, page_path in enumerate(page_paths or []):
        page_candidate = _candidate_from_page(page_path, index)
        if page_candidate:
            raw_candidates.append(page_candidate)

    normalized = [
        _normalize_memory_candidate(candidate, index)
        for index, candidate in enumerate(raw_candidates)
    ]
    ranked = sorted(normalized, key=lambda item: (-_candidate_score(item), str(item["id"])))
    selected = ranked[0] if ranked else None
    rejected = ranked[1:] if selected else ranked

    requires_refresh = not selected or selected.get("freshness_status") in {
        "expired",
        "stale",
        "superseded",
    }
    requires_citation = bool(selected and selected.get("decision_scope") in {"final", "evidence"})
    requires_human_confirmation = bool(
        selected and selected.get("missing_source") and selected.get("decision_scope") != "background"
    )

    decision_payload = {
        "query": query,
        "selected": selected,
        "rejected": [
            {
                "id": item.get("id"),
                "layer": item.get("layer"),
                "reason": (
                    "policy weakening"
                    if item.get("policy_weakening")
                    else "expired/stale"
                    if item.get("freshness_status") in {"expired", "stale", "superseded"}
                    else "lower authority"
                ),
            }
            for item in rejected
        ],
        "requires_citation": requires_citation,
        "requires_refresh": requires_refresh,
        "requires_human_confirmation": requires_human_confirmation,
    }
    emit_memory_event("authority.decision", query[:120] or "query", decision_payload)

    lines = ["## Memory Authority Decision", f"- Query: {query}"]
    if selected:
        lines.extend(
            [
                f"- Selected: `{selected.get('id')}` ({selected.get('layer')})",
                f"- Decision scope: {selected.get('decision_scope')}",
                f"- Authority level: {selected.get('authority_level')}",
                f"- Freshness: {selected.get('freshness_status')}",
                f"- Source: {selected.get('source_path') or 'missing'}",
            ]
        )
    else:
        lines.append("- Selected: none")
    lines.extend(
        [
            f"- Requires citation: {'yes' if requires_citation else 'no'}",
            f"- Requires refresh: {'yes' if requires_refresh else 'no'}",
            f"- Requires human confirmation: {'yes' if requires_human_confirmation else 'no'}",
            "",
            "### Rejected / Background Candidates",
        ]
    )
    if rejected:
        for item in rejected:
            reasons = []
            if item.get("policy_weakening"):
                reasons.append("attempts to weaken policy")
            if item.get("missing_source"):
                reasons.append("missing source")
            if item.get("freshness_status") in {"expired", "stale", "superseded"}:
                reasons.append(str(item.get("freshness_status")))
            reasons.append("lower authority")
            lines.append(
                f"- `{item.get('id')}` ({item.get('layer')}): {', '.join(dict.fromkeys(reasons))}"
            )
    else:
        lines.append("- None")
    return "\n".join(lines)


@hooked_tool
def read_wiki_page(relative_path: str) -> str:
    """Read a wiki markdown page.

    Args:
        relative_path: Wiki-relative path, e.g. 'index.md', 'concepts/dcf.md'

    Returns:
        Page content or a 'not found' message.
    """
    full = _resolve_path(relative_path)
    if not os.path.exists(full):
        return f"[WikiManager] Page not found: {relative_path}"
    with open(full, "r", encoding="utf-8") as f:
        return f.read()


@hooked_tool
def write_wiki_page(relative_path: str, content: str) -> str:
    """Write or overwrite a wiki markdown page.

    Args:
        relative_path: Wiki-relative path, e.g. 'concepts/dcf.md'
        content: Full markdown content (frontmatter + body)

    Returns:
        Success confirmation with path.
    """
    full = _resolve_path(relative_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    append_audit(
        "write_wiki_page",
        relative_path,
        {
            "bytes": len(content.encode("utf-8")),
            "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        },
    )
    return f"[WikiManager] Written: {relative_path}"


def suggest_wiki_path(title: str, category: str) -> str:
    """Suggest the canonical wiki path for a title and category.

    Args:
        title: Human-readable page title.
        category: concepts, instruments, markets, companies, macro, regulation,
            risk, models, sources, strategies.

    Returns:
        A wiki-relative path such as 'concepts/dcf-valuation.md'.
    """
    clean_category = _normalize_category(category)
    directory = _CATEGORY_DIRS[clean_category]
    return f"{directory}/{_slugify(title)}.md"


@hooked_tool
def upsert_wiki_page(
    title: str,
    category: str,
    summary: str,
    body: str,
    sources: Optional[List[str]] = None,
    related: Optional[List[str]] = None,
    operation: str = "ingest",
) -> str:
    """Create or update a durable FinWiki page and bookkeeping files.

    This is the preferred high-level LLM Wiki tool. It writes a markdown page,
    updates index.md, and appends log.md in one transaction-like operation.

    Args:
        title: Human-readable page title.
        category: concepts, instruments, markets, companies, macro, regulation,
            risk, models, sources, strategies.
        summary: One or two sentence summary for the page and index.
        body: Markdown body without YAML frontmatter.
        sources: Source URLs or source identifiers.
        related: Related page titles or slugs for wikilinks.
        operation: Log operation, usually ingest, update, query, or synthesis.

    Returns:
        Confirmation with the page path and any quality warnings.
    """
    clean_category = _normalize_category(category)
    page_path = suggest_wiki_path(title, clean_category)
    today = datetime.now().strftime("%Y-%m-%d")
    source_values = sources or ["LLM synthesis"]
    related_values = related or []

    normalized_body = body.strip()
    if not normalized_body.startswith("# "):
        normalized_body = f"# {title}\n{summary.strip()}\n\n{normalized_body}"

    if "## Sources" not in normalized_body:
        normalized_body += "\n\n## Sources\n"
        for source in source_values:
            normalized_body += f"- [Source: {source}]\n"

    if "## See Also" not in normalized_body and related_values:
        links = " | ".join(f"[[{item}]]" for item in related_values)
        normalized_body += f"\n## See Also\n{links}\n"

    frontmatter = (
        "---\n"
        f"title: {title}\n"
        f"tags: [finance, {clean_category}]\n"
        "domain: financial-services\n"
        f"last_updated: {today}\n"
        "review_status: draft\n"
        f"authority_level: {_MEMORY_V2_FRONTMATTER_DEFAULTS['authority_level']}\n"
        f"decision_scope: {_MEMORY_V2_FRONTMATTER_DEFAULTS['decision_scope']}\n"
        f"valid_from: {today}\n"
        "valid_until: \n"
        f"freshness_policy: {_MEMORY_V2_FRONTMATTER_DEFAULTS['freshness_policy']}\n"
        "aliases: []\n"
        f"sources:{_frontmatter_list(source_values)}\n"
        f"related:{_frontmatter_list(related_values)}\n"
        "supersedes: []\n"
        "superseded_by: []\n"
        "---\n\n"
    )
    content = frontmatter + normalized_body.rstrip() + "\n"

    write_wiki_page(page_path, content)
    update_index(page_path, title, clean_category, summary)
    append_log(operation, title, summary)
    append_audit(
        "upsert_wiki_page",
        page_path,
        {
            "title": title,
            "category": clean_category,
            "operation": operation,
            "sources": source_values,
            "related": related_values,
        },
    )
    emit_memory_event(
        "page.upserted",
        page_path,
        {
            "title": title,
            "category": clean_category,
            "operation": operation,
            "sources": source_values,
            "authority_level": _MEMORY_V2_FRONTMATTER_DEFAULTS["authority_level"],
            "decision_scope": _MEMORY_V2_FRONTMATTER_DEFAULTS["decision_scope"],
        },
    )

    warnings = []
    wikilink_count = len(re.findall(r"\[\[[^\]]+\]\]", content))
    if wikilink_count < 3:
        warnings.append(f"only {wikilink_count} wikilinks found; target is >= 3")
    if "[Source:" not in content and "[Kaynak:" not in content:
        warnings.append("no inline source markers found")

    suffix = f" Warnings: {'; '.join(warnings)}" if warnings else ""
    return f"[WikiManager] Upserted: {page_path}.{suffix}"


@hooked_tool
def list_wiki_pages(category: Optional[str] = None) -> List[str]:
    """List wiki pages. If category is given, restrict to that subdirectory.

    Args:
        category: e.g. 'concepts', 'markets', 'companies'

    Returns:
        List of relative paths like ['concepts/dcf.md', ...].
    """
    root = _WIKI_ROOT if category is None else os.path.join(_WIKI_ROOT, category)
    if not os.path.isdir(root):
        return []
    results = []
    for dirpath, _dirs, files in os.walk(root):
        for fname in files:
            if fname.endswith(".md"):
                full = os.path.join(dirpath, fname)
                rel = os.path.relpath(full, _WIKI_ROOT)
                results.append(rel)
    return sorted(results)


@hooked_tool
def update_index(page_path: str, title: str, category: str, summary: str = "") -> str:
    """Add or update a page entry in /wiki/index.md.

    Args:
        page_path: Relative path, e.g. 'concepts/dcf.md'
        title: Human-readable title
        category: concepts, instruments, markets, companies, macro, regulation,
            risk, models, sources, strategies
        summary: Optional one-line page summary.

    Returns:
        Success or error message.
    """
    index_path = os.path.join(_WIKI_ROOT, "index.md")
    if not os.path.exists(index_path):
        # Yedek oluştur
        base = """---
title: FinWiki Index
last_updated: {date}
total_pages: 0
---

# FinWiki — Knowledge Base Index

## Concepts

## Instruments

## Markets

## Companies

## Macroeconomics

## Regulation

## Risk

## Models

## Sources

## Strategies
"""
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(base.format(date=datetime.now().strftime("%Y-%m-%d")))

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    clean_category = _normalize_category(category)

    # Kategori başlığını bul (## Concepts, ## Instruments, ...)
    cat_heading = f"## {_CATEGORY_HEADINGS[clean_category]}"
    if cat_heading not in content:
        return f"[WikiManager] Category '{category}' not found in index.md"

    # Giriş satırı
    clean_summary = " ".join(summary.split())
    entry_line = f"- [{title}]({page_path})"
    if clean_summary:
        entry_line += f" — {clean_summary}"

    # Kategori bloğunun sonuna ekle (sonraki ## başlığına kadar)
    pattern = rf"({re.escape(cat_heading)}.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return "[WikiManager] Could not locate category block"

    block = match.group(1)
    # Eğer aynı page_path varsa title'ı güncelle, yoksa ekle
    lines = block.splitlines()
    new_lines = []
    replaced = False
    for line in lines:
        if f"({page_path})" in line:
            new_lines.append(entry_line)
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        new_lines.append(entry_line)

    new_block = "\n".join(new_lines) + "\n"
    content = content.replace(block, new_block)

    # total_pages & last_updated güncelle
    all_pages = list_wiki_pages()
    # index.md ve log.md hariç
    total = len([p for p in all_pages if p not in ("index.md", "log.md")])
    content = re.sub(
        r"total_pages:\s*\d+", f"total_pages: {total}", content
    )
    content = re.sub(
        r"last_updated:\s*\d{4}-\d{2}-\d{2}",
        f"last_updated: {datetime.now().strftime('%Y-%m-%d')}",
        content,
    )

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    append_audit(
        "update_index",
        "wiki/index.md",
        {"page_path": page_path, "title": title, "category": clean_category},
    )
    return f"[WikiManager] Index updated: {title} under {category}"


@hooked_tool
def append_log(operation: str, topic: str, summary: str) -> str:
    """Append an entry to /wiki/log.md.

    Args:
        operation: e.g. 'ingest', 'update', 'query', 'lint'
        topic: e.g. 'DCF Valuation'
        summary: Short description

    Returns:
        Confirmation.
    """
    log_path = os.path.join(_WIKI_ROOT, "log.md")
    date_str = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n## [{date_str}] {operation} | {topic}\n{summary}\n"

    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("---\ntitle: FinWiki Activity Log\n---\n\n# FinWiki Activity Log\n")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)

    append_audit(
        "append_log",
        "wiki/log.md",
        {"operation": operation, "topic": topic},
    )
    return f"[WikiManager] Logged: {operation} | {topic}"


@hooked_tool
def register_source(source_path: str, pages: Optional[List[str]] = None, notes: str = "") -> str:
    """Register an ingested raw source in the FinWiki manifest.

    Args:
        source_path: Local source path relative to the project root, or a URL.
        pages: Wiki pages created or updated from this source.
        notes: Short ingestion note.

    Returns:
        Confirmation with source status: new, changed, or unchanged.
    """
    manifest = _read_manifest()
    manifest.setdefault("sources", {})
    fingerprint = _source_fingerprint(source_path)
    key = fingerprint["path"]
    previous = manifest["sources"].get(key)
    status = "new"
    if previous:
        status = "unchanged" if previous.get("sha256") == fingerprint["sha256"] else "changed"

    manifest["sources"][key] = {
        **fingerprint,
        "last_ingested": datetime.now().strftime("%Y-%m-%d"),
        "pages": pages or [],
        "notes": redact_private_data(notes),
    }
    _write_manifest(manifest)
    append_audit(
        "register_source",
        key,
        {"status": status, "pages": pages or [], "kind": fingerprint["kind"]},
    )
    emit_memory_event(
        "source.registered",
        key,
        {"status": status, "pages": pages or [], "kind": fingerprint["kind"]},
    )
    return f"[WikiManager] Source registered: {key} ({status})"


@hooked_tool
def read_source_manifest() -> str:
    """Read the source ingestion manifest as formatted JSON."""
    return json.dumps(_read_manifest(), indent=2, sort_keys=True)


@hooked_tool
def source_lineage(page_path: Optional[str] = None, source_path: Optional[str] = None) -> str:
    """Trace raw source -> manifest -> wiki page lineage.

    Args:
        page_path: Optional wiki-relative page path.
        source_path: Optional raw source path or external URL.

    Returns:
        Markdown lineage report.
    """
    manifest = _read_manifest()
    sources = manifest.get("sources", {})
    if not isinstance(sources, dict):
        sources = {}

    rows = []
    for key, value in sources.items():
        if not isinstance(value, dict):
            continue
        pages = value.get("pages", [])
        pages_list = pages if isinstance(pages, list) else []
        if page_path and page_path not in pages_list:
            continue
        if source_path and key != source_path and value.get("path") != source_path:
            continue
        rows.append(
            {
                "source": key,
                "kind": value.get("kind", "unknown"),
                "sha256": str(value.get("sha256", ""))[:16],
                "last_ingested": value.get("last_ingested", "unknown"),
                "pages": pages_list,
                "notes": value.get("notes", ""),
            }
        )

    if not rows:
        filters = []
        if page_path:
            filters.append(f"page_path={page_path}")
        if source_path:
            filters.append(f"source_path={source_path}")
        suffix = f" for {', '.join(filters)}" if filters else ""
        return f"## Source Lineage\n- No manifest entries found{suffix}."

    lines = ["## Source Lineage"]
    for row in rows:
        page_links = ", ".join(f"`{page}`" for page in row["pages"]) or "None"
        lines.extend(
            [
                f"### {row['source']}",
                f"- Kind: {row['kind']}",
                f"- SHA-256: `{row['sha256']}`",
                f"- Last ingested: {row['last_ingested']}",
                f"- Pages: {page_links}",
            ]
        )
        if row["notes"]:
            lines.append(f"- Notes: {row['notes']}")
    return "\n".join(lines)


def _expiry_state_for_page(page_path: str, content: str) -> Tuple[str, Optional[int], int]:
    fields = _extract_frontmatter(content)
    status, expired_days = _validity_status(fields)
    if status != "active":
        return status, expired_days, 3 if status in {"expired", "superseded"} else 2
    age = _page_age_days(content)
    cat = _page_category(page_path)
    threshold = _FRESHNESS_THRESHOLDS.get(cat, 60)
    if age is None:
        return "missing-last-updated", None, 2
    if age > threshold * 2:
        return "critical-stale", age, 3
    if age > threshold:
        return "stale", age, 2
    return "fresh", age, 1


@hooked_tool
def search_wiki(query: str, category: Optional[str] = None, limit: int = 10) -> List[str]:
    """Run local BM25-style search over wiki markdown pages.

    This stays dependency-free but is closer to agentmemory/qmd than the old
    substring counter. It searches frontmatter, title, body, sources, and
    wikilinks, then returns ranked snippets.

    Args:
        query: Search query.
        category: Optional category directory.
        limit: Maximum result count.

    Returns:
        Ranked snippets in 'path: snippet' format.
    """
    query_terms = _tokenize(query)
    if not query_terms:
        return []

    documents = []
    doc_freq: Dict[str, int] = defaultdict(int)
    for page in list_wiki_pages(category):
        if page in ("index.md", "log.md"):
            continue
        content = read_wiki_page(page)
        frontmatter = _extract_frontmatter(content)
        page_text = " ".join(
            [
                page,
                str(frontmatter.get("title", "")),
                str(frontmatter.get("aliases", "")),
                str(frontmatter.get("tags", "")),
                content,
            ]
        )
        tokens = _tokenize(page_text)
        token_counts = Counter(tokens)
        unique_tokens = set(token_counts)
        for term in set(query_terms):
            if term in unique_tokens:
                doc_freq[term] += 1
        documents.append((page, content, token_counts, len(tokens)))

    if not documents:
        return []

    avg_len = sum(length for *_rest, length in documents) / len(documents)
    k1 = 1.2
    b = 0.75
    scored = []
    for page, content, token_counts, doc_len in documents:
        score = 0.0
        for term in query_terms:
            tf = token_counts.get(term, 0)
            if tf <= 0:
                continue
            df = doc_freq.get(term, 0)
            idf = math.log((len(documents) - df + 0.5) / (df + 0.5) + 1)
            denom = tf + k1 * (1 - b + b * (doc_len / max(avg_len, 1)))
            score += idf * ((tf * (k1 + 1)) / denom)

        if score <= 0:
            continue
        lower = content.lower()
        first_hit = min((lower.find(term) for term in query_terms if term in lower), default=0)
        start = max(0, first_hit - 120)
        end = min(len(content), first_hit + 240)
        snippet = " ".join(content[start:end].split())
        age = _page_age_days(content)
        freshness = "unknown" if age is None else f"{age}d old"
        scored.append((score, page, freshness, snippet))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [
        f"{page} | score={score:.3f} | freshness={freshness}: {snippet}"
        for score, page, freshness, snippet in scored[:limit]
    ]


@hooked_tool
def verify_wiki_claim(claim: str, page_path: Optional[str] = None, limit: int = 5) -> str:
    """Trace a claim to candidate wiki pages and registered sources.

    This is a FinWiki analogue of agentmemory's `memory_verify`: it does not
    prove truth; it reports source-backed evidence and lineage so the agent can
    decide whether a claim is supported, stale, or needs research.
    """
    candidate_pages = [page_path] if page_path else [
        result.split(" | ", 1)[0] for result in search_wiki(claim, limit=limit)
    ]
    candidate_pages = [page for page in candidate_pages if page and page not in ("index.md", "log.md")]
    manifest = _read_manifest().get("sources", {})
    if not isinstance(manifest, dict):
        manifest = {}

    lines = [f"## Claim Verification", f"Claim: {claim}"]
    if not candidate_pages:
        lines.append("- No candidate wiki pages found. Fresh research is required.")
        return "\n".join(lines)

    claim_terms = set(_tokenize(claim))
    for page in candidate_pages[:limit]:
        content = read_wiki_page(page)
        if content.startswith("[WikiManager] Page not found"):
            continue
        page_terms = set(_tokenize(content))
        overlap = sorted(claim_terms & page_terms)
        sources = _extract_sources_from_page(content)
        frontmatter = _extract_frontmatter(content)
        validity_status, validity_age = _validity_status(frontmatter)
        lineage_sources = []
        for source_key, value in manifest.items():
            if not isinstance(value, dict):
                continue
            pages = value.get("pages", [])
            if isinstance(pages, list) and page in pages:
                lineage_sources.append(source_key)
        age = _page_age_days(content)
        freshness = "unknown" if age is None else f"{age} days since last_updated"

        lines.extend(
            [
                f"### `{page}`",
                f"- Term overlap: {', '.join(overlap[:12]) or 'low'}",
                f"- Freshness: {freshness}",
                f"- Validity: {validity_status}"
                + (f" ({validity_age} days past valid_until)" if validity_age is not None else ""),
                f"- Authority level: {frontmatter.get('authority_level', 'unknown')}",
                f"- Decision scope: {frontmatter.get('decision_scope', 'unknown')}",
                f"- Page sources: {', '.join(sources) if sources else 'None found'}",
                f"- Manifest lineage: {', '.join(lineage_sources) if lineage_sources else 'None found'}",
            ]
        )
        if validity_status in {"expired", "stale", "superseded"}:
            lines.append("- Verification status: stale/expired; refresh or replacement required before final use.")
        elif not sources and not lineage_sources:
            lines.append("- Verification status: weak; no explicit source lineage.")
        elif age is not None and age > _FRESHNESS_THRESHOLDS.get(_page_category(page), 60):
            lines.append("- Verification status: source-backed but stale; refresh recommended.")
        else:
            lines.append("- Verification status: candidate support found; inspect cited sources for final judgment.")

    append_audit("verify_claim", page_path or "wiki", {"claim": claim, "pages": candidate_pages[:limit]})
    emit_memory_event(
        "claim.verified",
        page_path or "wiki",
        {"claim": claim, "pages": candidate_pages[:limit]},
    )
    return "\n".join(lines)


@hooked_tool
def freshness_report(category: Optional[str] = None) -> str:
    """Report stale wiki pages using finance-specific freshness thresholds."""
    pages = [page for page in list_wiki_pages(category) if page not in ("index.md", "log.md")]
    rows = []
    for page in pages:
        content = read_wiki_page(page)
        cat = _page_category(page)
        threshold = _FRESHNESS_THRESHOLDS.get(cat, 60)
        status, age, severity = _expiry_state_for_page(page, content)
        rows.append((severity, status, age, threshold, page))

    rows.sort(key=lambda item: (-item[0], item[4]))
    lines = [f"## Freshness Report — {datetime.now().strftime('%Y-%m-%d')}"]
    if not rows:
        lines.append("- No wiki pages found.")
        return "\n".join(lines)

    for severity, status, age, threshold, page in rows:
        age_text = "unknown" if age is None else f"{age}d"
        lines.append(f"- `{page}` — {status}; age={age_text}; threshold={threshold}d")

    append_audit("freshness_report", category or "wiki", {"page_count": len(rows)})
    return "\n".join(lines)


@hooked_tool
def mark_wiki_memory_stale(
    page_path: str,
    reason: str,
    replacement: Optional[str] = None,
    claim_id: Optional[str] = None,
) -> str:
    """Mark a wiki page or claim stale/superseded without deleting history."""
    full = _resolve_path(page_path)
    if not os.path.exists(full):
        return f"[WikiManager] Page not found: {page_path}"
    with open(full, "r", encoding="utf-8") as f:
        content = f.read()

    today = datetime.now().strftime("%Y-%m-%d")
    updates: Dict[str, object] = {
        "review_status": "superseded" if replacement else "stale",
        "last_updated": today,
        "valid_until": today,
        "stale_reason": redact_private_data(reason),
    }
    if replacement:
        fields = _extract_frontmatter(content)
        existing = _coerce_list(fields.get("superseded_by"))
        if replacement not in existing:
            existing.append(replacement)
        updates["superseded_by"] = existing

    updated = _update_frontmatter(content, updates)
    marker = "## Memory Governance Updates"
    note = (
        f"\n- {today}: Marked "
        f"{'claim `' + claim_id + '` ' if claim_id else 'page '}"
        f"as {'superseded' if replacement else 'stale'}."
        f" Reason: {redact_private_data(reason)}"
        + (f" Replacement: `{replacement}`." if replacement else "")
    )
    if marker in updated:
        updated = updated.rstrip() + note + "\n"
    else:
        updated = updated.rstrip() + f"\n\n{marker}\n{note}\n"

    with open(full, "w", encoding="utf-8") as f:
        f.write(updated)

    append_log("memory-stale", page_path, reason)
    append_audit(
        "mark_wiki_memory_stale",
        page_path,
        {"reason": reason, "replacement": replacement, "claim_id": claim_id},
    )
    emit_memory_event(
        "page.superseded" if replacement else "page.stale",
        claim_id or page_path,
        {"page_path": page_path, "reason": reason, "replacement": replacement},
    )
    projection = _memory_event_projection(limit=200)
    _write_expiry_review_page(projection)
    return (
        f"[WikiManager] Marked {page_path} as "
        f"{'superseded' if replacement else 'stale'}; history preserved."
    )


@hooked_tool
def update_day_state(
    summary: str,
    next_actions: Optional[List[str]] = None,
    supersedes: Optional[List[str]] = None,
    status: str = "current",
) -> str:
    """Update FinWiki's short-lived operational whiteboard."""
    os.makedirs(_STATE_ROOT, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    entry_id = f"day_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
    old_content = ""
    if os.path.exists(_DAY_STATE_PATH):
        with open(_DAY_STATE_PATH, "r", encoding="utf-8") as f:
            old_content = f.read()

    old_summary = ""
    match = re.search(r"## Current\n\n(.+?)(?=\n## |\Z)", old_content, re.DOTALL)
    if match:
        old_summary = " ".join(match.group(1).split())

    superseded_lines = []
    if old_summary and old_summary != summary.strip():
        superseded_lines.append(f"- {today}: {old_summary}")
    for item in supersedes or []:
        superseded_lines.append(f"- {today}: supersedes `{item}`")
    if old_content and "## Superseded Entries" in old_content:
        previous = old_content.split("## Superseded Entries", 1)[1].strip()
        if previous:
            previous = re.split(r"\n## ", previous, maxsplit=1)[0].strip()
            for line in previous.splitlines():
                if line.startswith("- ") and line != "- None" and line not in superseded_lines:
                    superseded_lines.append(line)

    actions = next_actions or []
    content_lines = [
        "---",
        "title: FinWiki Day State",
        "tags:",
        "  - memory",
        "  - operational",
        "domain: financial-services",
        f"last_updated: {today}",
        "review_status: active",
        "authority_level: operational",
        "decision_scope: hint",
        f"entry_id: {entry_id}",
        "sources:",
        '  - "operator-session"',
        "related:",
        '  - "wiki/maintenance/memory-governance"',
        "---",
        "",
        "# FinWiki Day State",
        "",
        "Day-state is today's operating whiteboard. It is not a source for financial facts.",
        "",
        "## Current",
        "",
        summary.strip(),
        "",
        "## Next Actions",
    ]
    content_lines.extend(f"- {item}" for item in actions) if actions else content_lines.append("- None")
    content_lines.extend(["", "## Superseded Entries"])
    content_lines.extend(superseded_lines or ["- None"])
    with open(_DAY_STATE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(content_lines).rstrip() + "\n")

    emit_memory_event(
        "day_state.updated",
        "state/day-state.md",
        {
            "entry_id": entry_id,
            "status": status,
            "summary": summary,
            "next_actions": actions,
            "supersedes": supersedes or [],
        },
    )
    return f"[WikiManager] Day-state updated: {entry_id}"


@hooked_tool
def memory_event_graph_report(limit: int = 50) -> str:
    """Replay memory events into a lightweight graph projection report."""
    clean_limit = max(1, min(int(limit), 1000))
    projection = _memory_event_projection(clean_limit)
    _write_memory_governance_page(projection)
    _write_expiry_review_page(projection)

    nodes = projection.get("nodes", {})
    relations = projection.get("relations", [])
    stale_items = projection.get("stale_items", [])
    contradictions = projection.get("contradictions", [])
    recent_decisions = projection.get("recent_decisions", [])
    errors = projection.get("errors", [])

    lines = [
        f"## Memory Event Graph Report — {datetime.now().strftime('%Y-%m-%d')}",
        f"- Nodes: {len(nodes) if isinstance(nodes, dict) else 0}",
        f"- Relations: {len(relations) if isinstance(relations, list) else 0}",
        f"- Stale/expired items: {len(stale_items) if isinstance(stale_items, list) else 0}",
        f"- Contradictions: {len(contradictions) if isinstance(contradictions, list) else 0}",
        "",
        "### Recent Authority Decisions",
    ]
    if recent_decisions:
        lines.extend(f"- {item}" for item in recent_decisions[-10:])
    else:
        lines.append("- None")
    lines.append("")
    lines.append("### Stale / Expired Items")
    if stale_items:
        lines.extend(f"- `{item}`" for item in stale_items)
    else:
        lines.append("- None")
    lines.append("")
    lines.append("### Projection Errors")
    if errors:
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("- None")
    return "\n".join(lines)


@hooked_tool
def lint_wiki() -> str:
    """Run a deterministic read-only wiki health check."""
    pages = [page for page in list_wiki_pages() if page not in ("index.md", "log.md")]
    page_slugs = {os.path.splitext(os.path.basename(page))[0]: page for page in pages}
    index_content = read_wiki_page("index.md")
    inbound = {page: 0 for page in pages}
    missing_refs = []
    low_links = []
    stale_pages = []
    missing_from_index = []

    today = datetime.now()
    for page in pages:
        content = read_wiki_page(page)
        links = re.findall(r"\[\[([^\]]+)\]\]", content)
        if len(links) < 3:
            low_links.append(f"- `{page}` — {len(links)} wikilinks")

        for link in links:
            slug = _slugify(link.split("|", 1)[0])
            target = page_slugs.get(slug)
            if target:
                inbound[target] += 1
            else:
                missing_refs.append(f"- `{page}` links to `[[{link}]]`")

        updated_match = re.search(r"last_updated:\s*(\d{4}-\d{2}-\d{2})", content)
        if updated_match:
            updated = datetime.strptime(updated_match.group(1), "%Y-%m-%d")
            age = (today - updated).days
            if age > 30:
                stale_pages.append(f"- `{page}` — last_updated {updated_match.group(1)} ({age} days)")

        if f"({page})" not in index_content:
            missing_from_index.append(f"- `{page}`")

    orphan_pages = [f"- `{page}` — inbound links {count}" for page, count in inbound.items() if count == 0]
    indexed_paths = set(re.findall(r"\]\(([^)]+\.md)\)", index_content))
    orphan_index_entries = [f"- `{path}`" for path in sorted(indexed_paths) if path not in pages]

    def section(title: str, rows: List[str]) -> str:
        body = "\n".join(rows) if rows else "- None"
        return f"### {title}\n{body}"

    return "\n\n".join(
        [
            f"## Lint Report — {today.strftime('%Y-%m-%d')}",
            section("Orphan Pages", orphan_pages),
            section("Missing Cross-References", low_links),
            section("Stale Pages", stale_pages),
            section("Dead Wikilinks", missing_refs),
            section("Index Issues", missing_from_index + orphan_index_entries),
        ]
    )
