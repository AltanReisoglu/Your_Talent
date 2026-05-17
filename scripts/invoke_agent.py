"""JSON bridge for non-Python API frontends.

Reads an invoke payload from stdin, calls the existing Python FinWiki runtime,
and writes a JSON response to stdout.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.service import invoke_agent


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    result = invoke_agent(
        message=payload["message"],
        user_id=payload.get("user_id", "local-user"),
        session_id=payload.get("session_id", "default"),
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
