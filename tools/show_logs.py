"""Read the evidence trail the browser deliberately does not show.

    python tools/show_logs.py queries --limit 5
    python tools/show_logs.py ingestions

The layout is the shared renderer in injectrag.logging_store, the same one that
writes logs/queries.log -- so what this prints and what is on disk cannot drift
into two different formats. Reads INJECTRAG_LOG_DIR (default `logs`), or
--log-dir.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from injectrag.logging_store import render_ingestion, render_query  # noqa: E402

FILES = {"queries": "queries.jsonl", "ingestions": "ingestions.jsonl"}


def read(path: pathlib.Path, limit: int | None) -> list[dict]:
    if not path.exists():
        return []
    records = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return records[-limit:] if limit else records


def print_record(kind: str, record: dict) -> None:
    print()
    print((render_query if kind == "queries" else render_ingestion)(record), end="")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=sorted(FILES))
    ap.add_argument("--limit", type=int, default=None, help="show only the last N records")
    ap.add_argument("--log-dir", default=None)
    args = ap.parse_args()

    log_dir = pathlib.Path(args.log_dir or os.environ.get("INJECTRAG_LOG_DIR") or "logs")
    path = log_dir / FILES[args.kind]
    records = read(path, args.limit)
    if not records:
        print(f"no {args.kind} records in {path}")
        return 0

    print(f"{len(records)} {args.kind} record(s) from {path}")
    for r in records:
        print_record(args.kind, r)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
