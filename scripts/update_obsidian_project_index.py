"""Generate Obsidian project navigation pages for FinWiki.

This script is deliberately Markdown-first and dependency-free. It scans Spec
Kit feature directories under `specs/` and writes navigation pages under
`wiki/project/` without moving or modifying canonical Spec Kit artifacts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPECS_DIR = REPO_ROOT / "specs"
PROJECT_DIR = REPO_ROOT / "wiki" / "project"
FEATURES_DIR = PROJECT_DIR / "features"
EVIDENCE_DIR = PROJECT_DIR / "evidence"
METHODOLOGY_DIR = PROJECT_DIR / "methodology"


@dataclass(frozen=True)
class Feature:
    feature_id: str
    slug: str
    title: str
    status: str
    spec_path: Path
    plan_path: Path | None
    tasks_path: Path | None
    evidence_path: Path | None
    task_total: int
    task_done: int
    residual_risks: list[str]

    @property
    def directory(self) -> Path:
        return self.spec_path.parent

    @property
    def feature_name(self) -> str:
        return f"{self.feature_id}-{self.slug}"

    @property
    def evidence_status(self) -> str:
        if not self.evidence_path:
            return "missing"
        if self.residual_risks:
            return "complete-with-risks"
        return "complete"

    @property
    def task_status(self) -> str:
        if not self.tasks_path:
            return "missing"
        if self.task_total == 0:
            return "empty"
        if self.task_total == self.task_done:
            return "complete"
        return f"{self.task_done}/{self.task_total}"


def rel(path: Path | None) -> str:
    if path is None:
        return ""
    return path.relative_to(REPO_ROOT).as_posix()


def read_text(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def title_from_spec(spec_text: str, fallback: str) -> str:
    match = re.search(r"^#\s+Feature Specification:\s*(.+)$", spec_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^#\s+(.+)$", spec_text, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def status_from_spec(spec_text: str, tasks_path: Path | None, evidence_path: Path | None) -> str:
    match = re.search(r"\*\*Status\*\*:\s*(.+)", spec_text)
    explicit = match.group(1).strip().lower() if match else ""
    if explicit and explicit not in {"draft", "planned"}:
        return explicit
    if evidence_path and evidence_path.exists():
        return "implemented"
    if tasks_path and tasks_path.exists():
        return "tasks-ready"
    return explicit or "draft"


def task_counts(tasks_text: str) -> tuple[int, int]:
    total = 0
    done = 0
    for line in tasks_text.splitlines():
        if re.match(r"- \[[ xX]\] T\d{3}", line):
            total += 1
            if re.match(r"- \[[xX]\] T\d{3}", line):
                done += 1
    return total, done


def residual_risks(evidence_text: str) -> list[str]:
    if not evidence_text:
        return []
    match = re.search(
        r"^## Residual Risks\s*(.*?)(?:^## |\Z)",
        evidence_text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        return []
    risks: list[str] = []
    current: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            if current:
                risks.append(" ".join(current).strip())
            current = [line[2:].strip()]
        elif current and line:
            current.append(line)
    if current:
        risks.append(" ".join(current).strip())
    return risks


def discover_features() -> list[Feature]:
    features: list[Feature] = []
    for directory in sorted(SPECS_DIR.glob("[0-9][0-9][0-9]-*")):
        if not directory.is_dir():
            continue
        spec_path = directory / "spec.md"
        if not spec_path.exists():
            continue

        feature_id, slug = directory.name.split("-", 1)
        spec_text = read_text(spec_path)
        tasks_path = directory / "tasks.md"
        plan_path = directory / "plan.md"
        evidence_path = directory / "evidence.md"
        tasks_path = tasks_path if tasks_path.exists() else None
        plan_path = plan_path if plan_path.exists() else None
        evidence_path = evidence_path if evidence_path.exists() else None
        task_total, task_done = task_counts(read_text(tasks_path))
        risks = residual_risks(read_text(evidence_path))

        features.append(
            Feature(
                feature_id=feature_id,
                slug=slug,
                title=title_from_spec(spec_text, directory.name),
                status=status_from_spec(spec_text, tasks_path, evidence_path),
                spec_path=spec_path,
                plan_path=plan_path,
                tasks_path=tasks_path,
                evidence_path=evidence_path,
                task_total=task_total,
                task_done=task_done,
                residual_risks=risks,
            )
        )
    return features


def yaml_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "\n" + "\n".join(f"  - {value}" for value in values)


def frontmatter(
    title: str,
    page_type: str,
    tags: list[str],
    status: str = "active",
    related: list[str] | None = None,
    extra: dict[str, str] | None = None,
) -> str:
    lines = [
        "---",
        f"title: {title}",
        f"type: {page_type}",
        "tags:" + yaml_list(tags),
        f"last_updated: {date.today().isoformat()}",
        f"status: {status}",
    ]
    for key, value in (extra or {}).items():
        if value:
            lines.append(f"{key}: {value}")
    lines.append("related:" + yaml_list(related or []))
    lines.append("---")
    return "\n".join(lines) + "\n"


def md_link(label: str, target: Path | None, from_dir: Path) -> str:
    if target is None:
        return "missing"
    relative = target.relative_to(from_dir, walk_up=True).as_posix()
    return f"[{label}]({relative})"


def render_project_index(features: list[Feature]) -> str:
    return (
        frontmatter(
            "FinWiki Project Index",
            "project-index",
            ["project", "obsidian", "finwiki"],
            related=["specs", "architecture", "evidence"],
        )
        + """
# FinWiki Project Index

This is the Obsidian entry point for FinWiki's engineering and agent-workflow
knowledge. Canonical financial knowledge remains in `wiki/`; canonical Spec Kit
execution artifacts remain in `specs/`.

## Start Here

- [Spec Kit Feature Index](specs.md)
- [Architecture Map](architecture.md)
- [Evidence Index](evidence/index.md)
- [Spec Kit Workflow](methodology/spec-kit-workflow.md)
- [FinWiki Environment Thesis](methodology/finwiki-environment.md)
- [Full Project Report](../../docs/finwiki_project_full_report.md)

## Primary Surfaces

- [README](../../README.md)
- [AGENTS](../../AGENTS.md)
- [Constitution](../../.specify/memory/constitution.md)
- [Financial Wiki Index](../index.md)
- [Maintenance Log](../../logs/maintenance-log.md)

## Feature Summaries

"""
        + "\n".join(
            f"- [{feature.feature_name}](features/{feature.feature_name}.md) - {feature.status}"
            for feature in features
        )
        + """

## Plain Markdown Fallback

These pages are ordinary Markdown. Obsidian graph view and Dataview can improve
navigation, but the core workflow works in any editor and through CLI checks.
"""
    ).strip() + "\n"


def render_specs_index(features: list[Feature]) -> str:
    rows = [
        "| Feature | Status | Tasks | Evidence | Canonical Artifacts |",
        "| --- | --- | --- | --- | --- |",
    ]
    for feature in features:
        from_dir = PROJECT_DIR
        artifacts = ", ".join(
            [
                md_link("spec", feature.spec_path, from_dir),
                md_link("plan", feature.plan_path, from_dir),
                md_link("tasks", feature.tasks_path, from_dir),
                md_link("evidence", feature.evidence_path, from_dir),
            ]
        )
        rows.append(
            f"| [{feature.feature_name}](features/{feature.feature_name}.md) "
            f"| {feature.status} | {feature.task_status} | {feature.evidence_status} | {artifacts} |"
        )
    return (
        frontmatter(
            "Spec Kit Feature Index",
            "feature-index",
            ["project", "spec-kit", "obsidian"],
            related=["index", "evidence"],
        )
        + """
# Spec Kit Feature Index

Spec Kit artifacts under `specs/` are canonical. This page is navigation only.
Do not move or duplicate `spec.md`, `plan.md`, `tasks.md`, or `evidence.md`
into `wiki/project/`.

"""
        + "\n".join(rows)
        + "\n"
    )


def render_architecture_page() -> str:
    return (
        frontmatter(
            "FinWiki Architecture Map",
            "methodology",
            ["project", "architecture", "finwiki"],
            related=["index", "specs"],
        )
        + """
# FinWiki Architecture Map

## Core Documents

- [README](../../README.md)
- [AGENTS](../../AGENTS.md)
- [Full Project Report](../../docs/finwiki_project_full_report.md)
- [Financial Services LLM Wiki Architecture](../../docs/financial_services_llm_wiki_architecture.md)
- [Spec Kit Constitution](../../.specify/memory/constitution.md)

## Runtime Boundaries

- Python agent runtime: `agents/`, `app/`, `tools/`
- C# gateway and browser UI: `dotnet-api/`
- Durable financial knowledge: `wiki/`
- Immutable source layer: `raw/`
- Behavior memory: `memories/`
- Read-only policy memory: `policies/`

## Operational Logs

- [Maintenance Log](../../logs/maintenance-log.md)
- [Audit Log](../../logs/audit-log.jsonl)
- [Agent Observations](../../logs/agent-observations.jsonl)
"""
    )


def render_feature_summary(feature: Feature) -> str:
    from_dir = FEATURES_DIR
    risks = feature.residual_risks or ["None recorded."]
    return (
        frontmatter(
            feature.title,
            "feature-summary",
            ["project", "spec-kit", "feature"],
            status=feature.status,
            related=["specs", "evidence", "architecture"],
            extra={
                "feature_id": feature.feature_name,
                "spec_path": rel(feature.spec_path),
                "plan_path": rel(feature.plan_path),
                "tasks_path": rel(feature.tasks_path),
                "evidence_path": rel(feature.evidence_path),
            },
        )
        + f"""
# {feature.title}

## Status

- Feature: `{feature.feature_name}`
- Status: `{feature.status}`
- Tasks: `{feature.task_status}`
- Evidence: `{feature.evidence_status}`

## Canonical Artifacts

- {md_link("spec.md", feature.spec_path, from_dir)}
- {md_link("plan.md", feature.plan_path, from_dir)}
- {md_link("tasks.md", feature.tasks_path, from_dir)}
- {md_link("evidence.md", feature.evidence_path, from_dir)}

## Related Project Pages

- [Spec Kit Feature Index](../specs.md)
- [Evidence Index](../evidence/index.md)
- [Architecture Map](../architecture.md)

## Related FinWiki Concepts

- [[discounted-cash-flow-dcf]]
- [[spec-kit-workflow]]
- [[finwiki-environment]]

## Residual Risks

"""
        + "\n".join(f"- {risk}" for risk in risks)
        + """

## Canonical Rule

This page is an Obsidian navigation summary. The authoritative execution
artifacts remain under `specs/`.
"""
    )


def render_evidence_index(features: list[Feature]) -> str:
    rows = [
        "| Feature | Evidence | Status | Residual Risks |",
        "| --- | --- | --- | --- |",
    ]
    for feature in features:
        risk_summary = "None recorded" if not feature.residual_risks else f"{len(feature.residual_risks)} risk item(s)"
        rows.append(
            f"| [{feature.feature_name}](../features/{feature.feature_name}.md) "
            f"| {md_link('evidence.md', feature.evidence_path, EVIDENCE_DIR)} "
            f"| {feature.evidence_status} | {risk_summary} |"
        )
    return (
        frontmatter(
            "Evidence Index",
            "evidence-index",
            ["project", "evidence", "spec-kit"],
            related=["specs", "index"],
        )
        + """
# Evidence Index

Evidence bundles record what was checked, what was skipped, and what risk
remains before a feature is treated as complete.

"""
        + "\n".join(rows)
        + "\n"
    )


def render_spec_kit_methodology() -> str:
    return (
        frontmatter(
            "Spec Kit Workflow",
            "methodology",
            ["project", "spec-kit", "methodology"],
            related=["specs", "evidence"],
        )
        + """
# Spec Kit Workflow

FinWiki uses Spec Kit to keep AI-assisted coding anchored to durable intent.

## Flow

1. `$speckit-specify` captures the user need and acceptance criteria.
2. `$speckit-plan` maps the spec to architecture and constitution checks.
3. `$speckit-tasks` breaks the work into executable, file-specific tasks.
4. `$speckit-implement` applies the tasks in dependency order.
5. `evidence.md` records checks, skipped checks, and residual risk.

## Local Constitution

See [FinWiki Constitution](../../../.specify/memory/constitution.md).

## Rule

Obsidian pages improve navigation. They do not replace Spec Kit artifacts under
`specs/`.
"""
    )


def render_environment_thesis() -> str:
    return (
        frontmatter(
            "FinWiki Environment Thesis",
            "methodology",
            ["project", "finwiki", "methodology"],
            related=["architecture", "specs"],
        )
        + """
# FinWiki Environment Thesis

FinWiki's durable value is the operating environment around the agent, not a
single model call.

## Layers

- `raw/`: immutable evidence
- `wiki/`: compiled financial knowledge
- `memories/`: behavior and preference memory
- `policies/`: read-only compliance and source-quality policy
- `logs/`: audit, observation, and maintenance history
- `specs/`: AI coding intent, plans, tasks, and evidence
- `dotnet-api/`: user gateway
- `agents/` and `tools/`: Python agent runtime

## Principle

Models can change. The local context structure, source lineage, task evidence,
and Markdown knowledge graph remain the reusable asset.
"""
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    features = discover_features()
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    METHODOLOGY_DIR.mkdir(parents=True, exist_ok=True)

    write(PROJECT_DIR / "index.md", render_project_index(features))
    write(PROJECT_DIR / "specs.md", render_specs_index(features))
    write(PROJECT_DIR / "architecture.md", render_architecture_page())
    write(EVIDENCE_DIR / "index.md", render_evidence_index(features))
    write(METHODOLOGY_DIR / "spec-kit-workflow.md", render_spec_kit_methodology())
    write(METHODOLOGY_DIR / "finwiki-environment.md", render_environment_thesis())

    for feature in features:
        write(FEATURES_DIR / f"{feature.feature_name}.md", render_feature_summary(feature))

    print(f"Updated Obsidian project index for {len(features)} feature(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
