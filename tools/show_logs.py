"""Read the evidence trail the browser deliberately does not show.

    python tools/show_logs.py queries --limit 5
    python tools/show_logs.py ingestions

Layout mirrors run_demo.py:_print_trial_detail so a live-app record and a batch
trial read the same way side by side. No dependencies; reads INJECTRAG_LOG_DIR
(default `logs`), or --log-dir.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib

FILES = {"queries": "queries.jsonl", "ingestions": "ingestions.jsonl"}


def read(path: pathlib.Path, limit: int | None) -> list[dict]:
    if not path.exists():
        return []
    records = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return records[-limit:] if limit else records


def short(text: str, limit: int = 900) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def print_query(r: dict) -> None:
    print(f"\n[{r.get('ts')}] {r.get('query_id')} "
          f"condition={r.get('condition')} defense={r.get('defense')}")
    print(f"  user: {r.get('display') or r.get('username')} ({r.get('user_id')})")
    print(f"  question: {r.get('question')}")
    print(f"  model: {r.get('provider')}/{r.get('model')} finish={r.get('finish_reason')} "
          f"marker_present={'yes' if r.get('marker_present') else 'no'}")
    print(f"  exposure: topk={r.get('attacker_in_topk')} context={r.get('attacker_in_context')}")
    hits = r.get("retrieved") or []
    print("  retrieved docs: " + (
        ", ".join(f"{h['rank']}:{h['document_id']} score={h['score']:.4f}" for h in hits) or "(none)"
    ))
    included = r.get("context_chunk_ids") or []
    print(f"  reached context ({len(included)}): " + (", ".join(included) or "(none)"))
    h = r.get("highest_context_chunk")
    if h:
        print(f"  highest context chunk: rank={h['rank']} doc={h['document_id']} "
              f"score={h['score']:.4f} chunk={h['chunk_id']}")
        print(f"    {short(h.get('text', ''))}")
    else:
        print("  highest context chunk: none included")
    if r.get("error"):
        print(f"  error response: {r['error']}")
    print(f"  model response: {short(r.get('answer', ''), 1200) or '(empty)'}")


def print_ingestion(r: dict) -> None:
    print(f"\n[{r.get('ts')}] {r.get('document_id')} case_date={r.get('case_date')}")
    print(f"  filed by: {r.get('display') or r.get('username')} ({r.get('user_id')})")
    print(f"  title: {r.get('title')}")
    print(f"  content_hash: {r.get('content_hash')}")
    print(f"  chunks added: {r.get('chunks_added')} -> corpus now "
          f"{r.get('corpus_documents_after')} documents / {r.get('corpus_chunks_after')} chunks")
    print(f"  description: {short(r.get('description', ''))}")
    print(f"  resolution:  {short(r.get('resolution', ''))}")


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
        (print_query if args.kind == "queries" else print_ingestion)(r)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
