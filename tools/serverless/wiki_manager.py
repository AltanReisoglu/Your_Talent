"""
FinWiki File-System Harness
Andrej Karpathy LLM Wiki mantığı için read/write araçları.
"""

import hashlib
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

_WIKI_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "wiki")
)
_PROJECT_ROOT = os.path.abspath(os.path.join(_WIKI_ROOT, ".."))
_MANIFEST_PATH = os.path.join(_WIKI_ROOT, ".manifest.json")

_CATEGORY_HEADINGS = {
    "concepts": "Concepts",
    "instruments": "Instruments",
    "markets": "Markets",
    "companies": "Companies",
    "macro": "Macroeconomics",
    "macroeconomics": "Macroeconomics",
    "strategies": "Strategies",
}

_CATEGORY_DIRS = {
    "concepts": "concepts",
    "instruments": "instruments",
    "markets": "markets",
    "companies": "companies",
    "macro": "macro",
    "macroeconomics": "macro",
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
    return f"[WikiManager] Written: {relative_path}"


def suggest_wiki_path(title: str, category: str) -> str:
    """Suggest the canonical wiki path for a title and category.

    Args:
        title: Human-readable page title.
        category: concepts, instruments, markets, companies, macro, strategies.

    Returns:
        A wiki-relative path such as 'concepts/dcf-valuation.md'.
    """
    clean_category = _normalize_category(category)
    directory = _CATEGORY_DIRS[clean_category]
    return f"{directory}/{_slugify(title)}.md"


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
        category: concepts, instruments, markets, companies, macro, strategies.
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
        f"last_updated: {today}\n"
        f"sources:{_frontmatter_list(source_values)}\n"
        f"related:{_frontmatter_list(related_values)}\n"
        "---\n\n"
    )
    content = frontmatter + normalized_body.rstrip() + "\n"

    write_wiki_page(page_path, content)
    update_index(page_path, title, clean_category, summary)
    append_log(operation, title, summary)

    warnings = []
    wikilink_count = len(re.findall(r"\[\[[^\]]+\]\]", content))
    if wikilink_count < 3:
        warnings.append(f"only {wikilink_count} wikilinks found; target is >= 3")
    if "[Source:" not in content and "[Kaynak:" not in content:
        warnings.append("no inline source markers found")

    suffix = f" Warnings: {'; '.join(warnings)}" if warnings else ""
    return f"[WikiManager] Upserted: {page_path}.{suffix}"


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


def update_index(page_path: str, title: str, category: str, summary: str = "") -> str:
    """Add or update a page entry in /wiki/index.md.

    Args:
        page_path: Relative path, e.g. 'concepts/dcf.md'
        title: Human-readable title
        category: concepts, instruments, markets, companies, macro, strategies
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

    return f"[WikiManager] Index updated: {title} under {category}"


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

    return f"[WikiManager] Logged: {operation} | {topic}"


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
        "notes": notes,
    }
    _write_manifest(manifest)
    return f"[WikiManager] Source registered: {key} ({status})"


def read_source_manifest() -> str:
    """Read the source ingestion manifest as formatted JSON."""
    return json.dumps(_read_manifest(), indent=2, sort_keys=True)


def search_wiki(query: str, category: Optional[str] = None, limit: int = 10) -> List[str]:
    """Run a lightweight local search over wiki markdown pages.

    This is a small built-in fallback before adopting qmd/BM25/vector search.

    Args:
        query: Search query.
        category: Optional category directory.
        limit: Maximum result count.

    Returns:
        Ranked snippets in 'path: snippet' format.
    """
    terms = [term for term in re.findall(r"[a-z0-9]+", query.lower()) if len(term) > 1]
    if not terms:
        return []

    results = []
    for page in list_wiki_pages(category):
        if page in ("index.md", "log.md"):
            continue
        content = read_wiki_page(page)
        lower = content.lower()
        score = sum(lower.count(term) for term in terms)
        if score <= 0:
            continue
        first_hit = min((lower.find(term) for term in terms if term in lower), default=0)
        start = max(0, first_hit - 120)
        end = min(len(content), first_hit + 240)
        snippet = " ".join(content[start:end].split())
        results.append((score, page, snippet))

    results.sort(key=lambda item: (-item[0], item[1]))
    return [f"{page}: {snippet}" for score, page, snippet in results[:limit]]


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
