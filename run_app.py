"""Launch the Northwind IT Helpdesk application.

    .venv/bin/python run_app.py                          # http://127.0.0.1:8000
    .venv/bin/python run_app.py --host 0.0.0.0 --port 8000
    INJECTRAG_PROVIDER=fake .venv/bin/python run_app.py   # offline, no API calls

Two corpora are indexed at boot in one embedding pass: the clean 36 documents,
and the poisoned 41 (clean plus the 5 frozen attacker tickets). INJECTRAG_CORPUS
and INJECTRAG_DEFENSE set what a conversation starts on; with
INJECTRAG_DEMO_CONTROLS=1 (the default) the browser can change both per
conversation, so the same question can be re-asked with the defense on without
a restart. Set INJECTRAG_DEMO_CONTROLS=0 to hide the controls and pin every
request to this configuration.

Nothing about retrieval, exposure or the marker appears in the browser. Read
logs/queries.jsonl, or `python tools/show_logs.py queries`, for the evidence.

The first start takes about 25 seconds while the ONNX embedding model loads and
the 41 documents are indexed. Under Docker the model is baked into the image, so
it is much faster there.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))


def _load_dotenv() -> None:
    env = pathlib.Path(__file__).parent / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()

# Interactive overrides, applied BEFORE importing injectrag.generation, which
# freezes these into module constants at import time. The batch defaults are
# wrong for a live app: a 30 s inter-call gap makes every message stall, and
# retry-forever would hang the browser indefinitely on a rate limit.
# Under Docker these same three values come from docker-compose.yml.
os.environ.setdefault("INJECTRAG_OPENAI_MIN_CALL_GAP_SECONDS", "2")
os.environ.setdefault("INJECTRAG_OPENAI_RETRY_FOREVER", "0")
os.environ.setdefault("INJECTRAG_OPENAI_MAX_RETRIES", "1")
os.environ.setdefault("INJECTRAG_GEMINI_RETRY_FOREVER", "0")
os.environ.setdefault("INJECTRAG_GEMINI_MAX_RETRIES", "1")

from injectrag.api import create_app  # noqa: E402
from injectrag.service import (  # noqa: E402
    build_service,
    demo_controls_enabled,
    provider_label,
    resolved_corpus,
    resolved_defense,
)

if __name__ == "__main__":
    import uvicorn

    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    print("Indexing the corpus (first run loads the ONNX model, ~25 s)...", flush=True)
    service = build_service()
    print(f"  poisoned corpus: {service.document_count} documents, "
          f"{service.chunk_count} chunks", flush=True)
    print(f"  clean corpus:    {service.clean_document_count} documents, "
          f"{len(service.pipelines['clean'].index.chunks)} chunks", flush=True)
    print(f"  attacker documents: {', '.join(sorted(service.pipeline.attacker_doc_ids))}", flush=True)
    print(f"  provider: {provider_label()}", flush=True)
    print(f"  starts on: corpus={resolved_corpus()} defense={resolved_defense()}", flush=True)
    print(f"  demo controls: {'on (the browser can change both)' if demo_controls_enabled() else 'off (pinned to .env)'}",
          flush=True)
    print(f"  log directory: {service.logger.log_dir}", flush=True)
    print(f"\nOpen http://{args.host}:{args.port}\n", flush=True)

    uvicorn.run(create_app(service), host=args.host, port=args.port, log_level="warning")
