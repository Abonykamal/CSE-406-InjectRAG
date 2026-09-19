"""Append-only JSONL evidence trail.

The browser deliberately shows nothing about retrieval, exposure or the marker --
a visitor sees an ordinary helpdesk. Everything that makes this a measurable
experiment is written here instead, so these two files are the only place the
attack can be read from.

Two files under LOG_DIR (INJECTRAG_LOG_DIR, default `logs`):

  queries.jsonl     one line per employee question
  ingestions.jsonl  one line per technician case submission

Append-only, one line per record, flushed on every write, guarded by a single
lock so concurrent requests cannot interleave partial lines. Under Docker the
directory is a bind mount, so the trail survives the container -- the one habit
worth keeping from task R12.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import pathlib
import threading

DEFAULT_LOG_DIR = "logs"
QUERY_LOG = "queries.jsonl"
INGESTION_LOG = "ingestions.jsonl"


def utc_now() -> str:
    """UTC ISO-8601 with a trailing Z, second resolution."""
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class JsonlLogger:
    def __init__(self, log_dir: str | None = None):
        self.log_dir = pathlib.Path(
            log_dir or os.environ.get("INJECTRAG_LOG_DIR") or DEFAULT_LOG_DIR
        )
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    # --- paths -----------------------------------------------------------

    @property
    def query_path(self) -> pathlib.Path:
        return self.log_dir / QUERY_LOG

    @property
    def ingestion_path(self) -> pathlib.Path:
        return self.log_dir / INGESTION_LOG

    # --- writing ---------------------------------------------------------

    def _append(self, path: pathlib.Path, record: dict) -> None:
        line = json.dumps(record, ensure_ascii=False)
        with self._lock:
            with path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
                fh.flush()

    def log_query(self, record: dict) -> None:
        self._append(self.query_path, {"ts": utc_now(), "event": "query", **record})

    def log_ingestion(self, record: dict) -> None:
        self._append(self.ingestion_path, {"ts": utc_now(), "event": "ingestion", **record})

    # --- reading (for tools/show_logs.py and the tests) ------------------

    def read(self, kind: str, limit: int | None = None) -> list[dict]:
        path = {"queries": self.query_path, "ingestions": self.ingestion_path}[kind]
        if not path.exists():
            return []
        records = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return records[-limit:] if limit else records
