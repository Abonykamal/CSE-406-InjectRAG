"""Launch the Northwind IT Helpdesk application.

    .venv/bin/python run_app.py                          # http://127.0.0.1:8000
    .venv/bin/python run_app.py --host 0.0.0.0 --port 8000
    INJECTRAG_PROVIDER=fake .venv/bin/python run_app.py   # offline, no API calls

The corpus is poisoned at boot: 36 clean documents plus the 5 frozen attacker
tickets. The defense is server configuration, not a UI control -- set
INJECTRAG_DEFENSE to off | boundary | datamarking and restart.

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
from injectrag.service import build_service, provider_label, resolved_defense  # noqa: E402

if __name__ == "__main__":
    import uvicorn

    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    print("Indexing the corpus (first run loads the ONNX model, ~25 s)...", flush=True)
    service = build_service()
    print(f"  {service.document_count} documents, {service.chunk_count} chunks indexed", flush=True)
    print(f"  attacker documents: {', '.join(sorted(service.pipeline.attacker_doc_ids))}", flush=True)
    print(f"  provider: {provider_label()}", flush=True)
    print(f"  defense: {resolved_defense()}", flush=True)
    print(f"  log directory: {service.logger.log_dir}", flush=True)
    print(f"\nOpen http://{args.host}:{args.port}\n", flush=True)

    uvicorn.run(create_app(service), host=args.host, port=args.port, log_level="warning")
