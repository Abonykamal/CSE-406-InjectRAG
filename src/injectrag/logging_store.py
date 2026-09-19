"""Append-only JSONL evidence trail.

The browser deliberately shows nothing about retrieval, exposure or the marker --
a visitor sees an ordinary helpdesk. Everything that makes this a measurable
experiment is written here instead, so these two files are the only place the
attack can be read from.

Four files under LOG_DIR (INJECTRAG_LOG_DIR, default `logs`):

  queries.jsonl     one line per employee question       (machine-readable)
  ingestions.jsonl  one line per technician case         (machine-readable)
  queries.log       the same records, rendered for people
  ingestions.log    the same records, rendered for people

The .jsonl files keep a strict one-record-per-line contract -- `read()` below,
tools/show_logs.py and the integration tests all split on newlines, and any
other JSONL tool should be able to read them. Pretty-printing them would break
that, so readability lives in the parallel .log files instead: fixed-width
labels, multi-line fields indented under their label with real line breaks, and
a blank line between records. Both writes happen under the same lock, so the
two views can never disagree about what was logged.

Append-only, flushed on every write, guarded by a single lock so concurrent
requests cannot interleave partial lines. Under Docker the directory is a bind
mount, so the trail survives the container -- the one habit worth keeping from
task R12.
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
QUERY_TEXT_LOG = "queries.log"
INGESTION_TEXT_LOG = "ingestions.log"

_LABEL_WIDTH = 10
_INDENT = "    "


def _yn(value: object) -> str:
    return "yes" if value else "no"


def _block(label: str, text: str) -> list[str]:
    """A multi-line field: the label on its own line, the text indented under it.

    This is the whole point of the .log rendering -- an answer or a retrieved
    chunk is read as prose, not as one long line of \n escapes.
    """
    body = (text or "").rstrip()
    if not body:
        return [f"  {label.ljust(_LABEL_WIDTH)} (empty)"]
    # A short one-liner reads better beside its label than under it.
    if "\n" not in body and len(body) <= 88:
        return [f"  {label.ljust(_LABEL_WIDTH)} {body}"]
    lines = [f"  {label}"]
    lines.extend(_INDENT + line for line in body.splitlines())
    return lines


def _field(label: str, value: object) -> str:
    return f"  {label.ljust(_LABEL_WIDTH)} {value}"


def render_query(r: dict) -> str:
    """One query record as plain text. Shared with tools/show_logs.py so the
    file on disk and the CLI never drift into two different layouts."""
    out = [f"[{r.get('ts')}] {r.get('query_id')}"]
    out.append(_field("user", f"{r.get('display') or r.get('username')} ({r.get('user_id')})"))
    if r.get("conversation_id"):
        out.append(_field("chat", r["conversation_id"]))
    # `corpus` is absent from records written before the corpus became
    # selectable; those runs were always poisoned, but say nothing rather than
    # assert it retroactively.
    line = f"{r.get('condition')}    defense {r.get('defense')}"
    if r.get("corpus"):
        line += f"    corpus {r['corpus']}"
    out.append(_field("condition", line))
    strategy = r.get("spotlighting_strategy")
    if strategy:
        out.append(_field("strategy", strategy))
    if r.get("demo_override"):
        out.append(_field("source", "condition chosen in the browser (demo controls on)"))
    out.append(_field(
        "model",
        f"{r.get('provider')}/{r.get('model')}    finish {r.get('finish_reason')}",
    ))
    out.extend(_block("question", r.get("question", "")))

    hits = r.get("retrieved") or []
    included = set(r.get("context_chunk_ids") or [])
    if hits:
        out.append(f"  {'retrieved'.ljust(_LABEL_WIDTH)} "
                   f"{len(included)} of {len(hits)} chunks reached the context")
        for h in hits:
            mark = "*" if h.get("chunk_id") in included else " "
            out.append(f"{_INDENT}{mark} {h.get('rank')}. {h.get('document_id'):<5} "
                       f"{h.get('score')}  {h.get('chunk_id')}")

    out.append(_field(
        "exposure",
        f"attacker in top-k: {_yn(r.get('attacker_in_topk'))}    "
        f"in context: {_yn(r.get('attacker_in_context'))}    "
        f"marker present: {_yn(r.get('marker_present'))}",
    ))
    top = r.get("highest_context_chunk")
    if top:
        out.extend(_block(f"top chunk ({top.get('document_id')})", top.get("text", "")))
    out.extend(_block("answer", r.get("answer", "")))
    if r.get("error"):
        out.extend(_block("error", str(r["error"])))
    return "\n".join(out) + "\n"


def render_ingestion(r: dict) -> str:
    """One ingestion record as plain text."""
    out = [f"[{r.get('ts')}] {r.get('document_id')}"]
    out.append(_field("user", f"{r.get('display') or r.get('username')} ({r.get('user_id')})"))
    out.append(_field("case date", r.get("case_date")))
    out.append(_field("title", r.get("title")))
    out.extend(_block("described", r.get("description", "")))
    out.extend(_block("resolved", r.get("resolution", "")))
    out.append(_field("hash", r.get("content_hash")))
    out.append(_field(
        "corpus",
        f"+{r.get('chunks_added')} chunks -> {r.get('corpus_documents_after')} documents, "
        f"{r.get('corpus_chunks_after')} chunks",
    ))
    return "\n".join(out) + "\n"


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

    @property
    def query_text_path(self) -> pathlib.Path:
        return self.log_dir / QUERY_TEXT_LOG

    @property
    def ingestion_text_path(self) -> pathlib.Path:
        return self.log_dir / INGESTION_TEXT_LOG

    # --- writing ---------------------------------------------------------

    def _append(self, path: pathlib.Path, record: dict, text_path: pathlib.Path,
                render) -> None:
        """Write the record twice: strict JSONL, then the readable rendering.

        One lock covers both files, so a reader never sees a record in one view
        and not the other. A failure to render must not lose the evidence, so the
        JSONL write happens first and the text write is best-effort.
        """
        line = json.dumps(record, ensure_ascii=False)
        with self._lock:
            with path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
                fh.flush()
            try:
                rendered = render(record)
            except Exception as e:  # noqa: BLE001 - never lose a record to a format bug
                rendered = f"[{record.get('ts')}] (could not render: {type(e).__name__}: {e})\n"
            with text_path.open("a", encoding="utf-8") as fh:
                fh.write(rendered + "\n")
                fh.flush()

    def log_query(self, record: dict) -> None:
        self._append(
            self.query_path, {"ts": utc_now(), "event": "query", **record},
            self.query_text_path, render_query,
        )

    def log_ingestion(self, record: dict) -> None:
        self._append(
            self.ingestion_path, {"ts": utc_now(), "event": "ingestion", **record},
            self.ingestion_text_path, render_ingestion,
        )

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
