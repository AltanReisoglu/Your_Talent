"""Validate Spec Kit feature artifacts for FinWiki.

This helper is intentionally lightweight. Spec Kit owns the main workflow; this
script adds FinWiki's evidence-bundle gate before commit or push.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPECS_DIR = REPO_ROOT / "specs"
REQUIRED = ("spec.md", "plan.md", "tasks.md")
EVIDENCE = "evidence.md"
UNCLEAR_MARKERS = ("[NEEDS CLARIFICATION",)
PLACEHOLDER_MARKERS = ("[command]", "[passed/failed/not-run]", "[notes]")


def _feature_dirs(name: str | None) -> list[Path]:
    if name:
        candidate = SPECS_DIR / name
        return [candidate]
    if not SPECS_DIR.exists():
        return []
    return sorted(path for path in SPECS_DIR.iterdir() if path.is_dir())


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="replace")


def validate_feature(feature: Path, require_evidence: bool) -> list[str]:
    errors: list[str] = []
    if not feature.exists():
        return [f"Missing feature directory: {feature.relative_to(REPO_ROOT)}"]

    for filename in REQUIRED:
        path = feature / filename
        if not path.exists():
            errors.append(f"{feature.name}: missing {filename}")
            continue
        text = _read(path)
        for marker in UNCLEAR_MARKERS:
            if marker in text:
                errors.append(f"{feature.name}: unresolved clarification marker in {filename}")

    evidence = feature / EVIDENCE
    if require_evidence and not evidence.exists():
        errors.append(f"{feature.name}: missing evidence.md")
    elif evidence.exists():
        text = _read(evidence)
        for marker in PLACEHOLDER_MARKERS:
            if marker in text:
                errors.append(f"{feature.name}: unresolved evidence placeholder {marker}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feature", help="Feature directory name under specs/")
    parser.add_argument(
        "--require-evidence",
        action="store_true",
        help="Require evidence.md for each checked feature",
    )
    args = parser.parse_args()

    features = _feature_dirs(args.feature)
    if not features:
        print("No Spec Kit feature directories found under specs/.")
        return 0

    errors: list[str] = []
    for feature in features:
        errors.extend(validate_feature(feature, args.require_evidence))

    if errors:
        print("Spec evidence check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Spec evidence check passed for {len(features)} feature(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
