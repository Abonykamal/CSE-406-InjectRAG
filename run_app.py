"""Launch the InjectRAG helpdesk demonstration application.

    .venv/bin/python run_app.py            # http://127.0.0.1:8000
    .venv/bin/python run_app.py --port 9000
    INJECTRAG_PROVIDER=fake .venv/bin/python run_app.py   # offline, no API calls

The provider comes from .env, which defaults to Groq (openai/gpt-oss-20b); the
startup banner names whichever one was resolved. Set INJECTRAG_PROVIDER=fake to
run with no API calls at all -- answers are then scripted, including the
defense appearing to work, so do not read offline runs as results.

The first start takes about 25 seconds while the ONNX embedding model loads and
the 36 clean documents are indexed. Attacker documents are NOT preloaded: they
enter only by submitting and resolving a ticket in the UI.
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
# wrong for a live demo: a 30 s inter-call gap makes every question stall, and
# retry-forever would hang the browser indefinitely on a rate limit instead of
# failing over to the labelled offline provider.
os.environ["INJECTRAG_OPENAI_MIN_CALL_GAP_SECONDS"] = os.environ.get(
    "INJECTRAG_DEMO_CALL_GAP_SECONDS", "2"
)
os.environ["INJECTRAG_OPENAI_RETRY_FOREVER"] = "0"
os.environ["INJECTRAG_OPENAI_MAX_RETRIES"] = "1"
os.environ["INJECTRAG_GEMINI_RETRY_FOREVER"] = "0"
os.environ["INJECTRAG_GEMINI_MAX_RETRIES"] = "1"

from injectrag.api import create_app  # noqa: E402
from injectrag.service import build_service, provider_label  # noqa: E402

if __name__ == "__main__":
    import uvicorn

    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    print("Building the clean index (first run loads the ONNX model, ~25 s)...", flush=True)
    service = build_service()
    s = service.status()
    print(f"  {s['documents']} documents, {s['chunks']} chunks indexed", flush=True)
    print(f"  provider: {s['provider']}", flush=True)
    print(f"  target marker: {s['marker']}", flush=True)
    print(f"\nOpen http://{args.host}:{args.port}\n", flush=True)

    uvicorn.run(create_app(service), host=args.host, port=args.port, log_level="warning")
