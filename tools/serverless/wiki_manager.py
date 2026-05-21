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
from typing import Dict, List, Optional

from app.hooks import hooked_tool

_WIKI_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "wiki")
)
_PROJECT_ROOT = os.path.abspath(os.path.join(_WIKI_ROOT, ".."))
_MANIFEST_PATH = os.path.join(_WIKI_ROOT, ".manifest.json")
_LOG_ROOT = os.path.join(_PROJECT_ROOT, "logs")
_AUDIT_LOG_PATH = os.path.join(_LOG_ROOT, "audit-log.jsonl")
_OBSERVATION_LOG_PATH = os.path.join(_LOG_ROOT, "agent-observations.jsonl")

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
        "aliases: []\n"
        f"sources:{_frontmatter_list(source_values)}\n"
        f"related:{_frontmatter_list(related_values)}\n"
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
                f"- Page sources: {', '.join(sources) if sources else 'None found'}",
                f"- Manifest lineage: {', '.join(lineage_sources) if lineage_sources else 'None found'}",
            ]
        )
        if not sources and not lineage_sources:
            lines.append("- Verification status: weak; no explicit source lineage.")
        elif age is not None and age > _FRESHNESS_THRESHOLDS.get(_page_category(page), 60):
            lines.append("- Verification status: source-backed but stale; refresh recommended.")
        else:
            lines.append("- Verification status: candidate support found; inspect cited sources for final judgment.")

    append_audit("verify_claim", page_path or "wiki", {"claim": claim, "pages": candidate_pages[:limit]})
    return "\n".join(lines)


@hooked_tool
def freshness_report(category: Optional[str] = None) -> str:
    """Report stale wiki pages using finance-specific freshness thresholds."""
    pages = [page for page in list_wiki_pages(category) if page not in ("index.md", "log.md")]
    rows = []
    for page in pages:
        content = read_wiki_page(page)
        age = _page_age_days(content)
        cat = _page_category(page)
        threshold = _FRESHNESS_THRESHOLDS.get(cat, 60)
        if age is None:
            status = "missing-last-updated"
            severity = 2
        elif age > threshold * 2:
            status = "critical-stale"
            severity = 3
        elif age > threshold:
            status = "stale"
            severity = 2
        else:
            status = "fresh"
            severity = 1
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
