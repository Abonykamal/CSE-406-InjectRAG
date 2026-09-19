"""InjectRAG demonstration runner.

Builds the clean and poisoned indexes, runs the 18 answerable recovery questions
in three conditions (clean / attacked / defended), and reports the injection
metrics. Writes a full JSONL trace to artifacts/demo_run.jsonl.

Usage:
    .venv/Scripts/python.exe run_demo.py            # all three conditions
    .venv/Scripts/python.exe run_demo.py --spotlighting datamarking
    .venv/Scripts/python.exe run_demo.py --ask "I forgot my password"   # one-off

Set GEMINI_API_KEY (or GOOGLE_API_KEY) for real Gemini answers; without a key a
fake provider runs so the pipeline is still exercisable.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))


def _load_dotenv() -> None:
    """Minimal .env reader (KEY=VALUE lines) so an API key can live in a file
    instead of the shell. No dependency on python-dotenv."""
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

from injectrag.pipeline import Pipeline, load_documents, trial_to_dict  # noqa: E402
from injectrag.seed_marker import MARKER  # noqa: E402

CLEAN = "data/corpus/clean/documents.jsonl"
ATTACK = "data/corpus/attack/documents.jsonl"
QUESTIONS = "data/queries/dev_questions.jsonl"


def load_questions() -> list[dict]:
    qs = []
    for line in pathlib.Path(QUESTIONS).read_text(encoding="utf-8").splitlines():
        if line.strip():
            qs.append(json.loads(line))
    return qs


def target_questions() -> list[dict]:
    return [q for q in load_questions() if q["category"] == "answerable_target"]


def build_pipelines():
    clean_docs = load_documents(CLEAN)
    attack_docs = load_documents(ATTACK)
    attacker_ids = {d["document_id"] for d in attack_docs}

    clean_pipe = Pipeline.from_documents(clean_docs, attacker_doc_ids=set(), marker=MARKER)
    poisoned_pipe = Pipeline.from_documents(
        clean_docs + attack_docs, attacker_doc_ids=attacker_ids, marker=MARKER
    )
    return clean_pipe, poisoned_pipe, attacker_ids


def provider_note() -> str:
    provider = os.environ.get("INJECTRAG_PROVIDER", "auto").strip().lower()
    if provider == "groq" or (provider == "auto" and os.environ.get("GROQ_API_KEY")):
        model = os.environ.get("INJECTRAG_GROQ_MODEL", "openai/gpt-oss-20b")
        return f"REAL Groq ({model})"
    if provider == "openai" or (provider == "auto" and os.environ.get("OPENAI_API_KEY")):
        model = os.environ.get("INJECTRAG_OPENAI_MODEL", "gpt-oss-20b")
        return f"REAL OpenAI ({model})"
    if provider == "fake":
        return "FAKE provider"
    if provider == "ollama":
        model = os.environ.get("INJECTRAG_OLLAMA_MODEL", "llama3.1:8b")
        return f"REAL Ollama ({model}, local)"
    if provider == "gemini" or (
        provider == "auto"
        and (os.environ.get("INJECTRAG_GEMINI_KEYS") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    ):
        model = os.environ.get("INJECTRAG_GEMINI_MODEL", "gemini-3.8-flash")
        keys = [k.strip() for k in os.environ.get("INJECTRAG_GEMINI_KEYS", "").split(",") if k.strip()]
        key_count = len(keys) or (1 if (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")) else 0)
        return f"REAL Gemini ({model}, {key_count} key slot{'s' if key_count != 1 else ''})"
    # auto mode with no cloud key: a running local Ollama beats the fake provider
    if provider == "auto":
        try:
            from injectrag.generation import _ollama_up
            if _ollama_up():
                model = os.environ.get("INJECTRAG_OLLAMA_MODEL", "llama3.1:8b")
                return f"REAL Ollama ({model}, local)"
        except Exception:
            pass
    return "FAKE provider (no API key or local model)"


def _short_text(text: str, limit: int = 900) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _format_hits(hits: list[dict]) -> str:
    return ", ".join(
        f"{h['rank']}:{h['document_id']} score={h['score']:.4f}" for h in hits
    )


def _print_trial_detail(t, query_number: int, query_total: int, call_number: int, call_total: int, print_prompts: bool = False) -> None:
    marker = "yes" if t.marker_present else "no"
    status = "ERROR" if t.error else "ok"
    print(
        f"\n[{call_number}/{call_total}] condition={t.condition} "
        f"query={query_number}/{query_total} id={t.query_id} status={status}",
        flush=True,
    )
    if t.spotlighting_strategy:
        print(f"  spotlighting: {t.spotlighting_strategy}", flush=True)
    print(f"  question: {t.question}", flush=True)
    print(f"  model: {t.provider}/{t.model} finish={t.finish_reason} marker_present={marker}", flush=True)
    print(f"  exposure: topk={t.attacker_in_topk} context={t.attacker_in_context}", flush=True)
    print(f"  retrieved docs: {_format_hits(t.hits) or '(none)'}", flush=True)
    if t.highest_context_chunk:
        h = t.highest_context_chunk
        print(
            f"  highest context chunk: rank={h['rank']} doc={h['document_id']} "
            f"score={h['score']:.4f} chunk={h['chunk_id']}",
            flush=True,
        )
        print(f"    {_short_text(h['text'])}", flush=True)
    else:
        print("  highest context chunk: none included", flush=True)
    if t.error:
        print(f"  error response: {t.error}", flush=True)
        print("  model response: (empty; excluded from metric denominators)", flush=True)
    else:
        print(f"  model response: {_short_text(t.answer, limit=1200) or '(empty)'}", flush=True)
    if print_prompts:
        print("\n  --- exact system prompt sent ---", flush=True)
        print(t.system_prompt or "", flush=True)
        print("  --- exact user message sent ---", flush=True)
        print(t.user_message or "", flush=True)
        print("  --- end exact prompt ---", flush=True)


def run_all(spotlighting_strategy: str | None = None, limit: int | None = None, print_prompts: bool = False) -> None:
    clean_pipe, poisoned_pipe, attacker_ids = build_pipelines()
    questions = target_questions()
    if limit is not None:
        questions = questions[:limit]

    print(f"Provider: {provider_note()}")
    print(f"Defended spotlighting: {spotlighting_strategy or os.environ.get('INJECTRAG_SPOTLIGHTING', 'boundary')}")
    print(f"Target marker: {MARKER}")
    print(f"Clean corpus: {len(load_documents(CLEAN))} docs | "
          f"Poisoned: {len(load_documents(CLEAN, ATTACK))} docs "
          f"({len(attacker_ids)} attacker tickets)")
    print(f"Questions (answerable recovery): {len(questions)}\n")

    conditions = [
        ("clean", clean_pipe),
        ("attacked", poisoned_pipe),
        ("defended", poisoned_pipe),
    ]

    total_calls = len(questions) * len(conditions)
    print(f"Running {total_calls} generation calls "
          f"({len(questions)} questions x {len(conditions)} conditions).")
    if "REAL" in provider_note():
        print("Real API calls run one at a time; free-tier rate limits may add pauses.\n")

    all_trials = []
    summary = {}
    done = 0
    for cond, pipe in conditions:
        trials = []
        for query_number, q in enumerate(questions, start=1):
            t = pipe.answer(
                q["query_id"],
                q["question"],
                cond,
                spotlighting_strategy=spotlighting_strategy,
                include_prompt=print_prompts,
            )
            done += 1
            _print_trial_detail(t, query_number, len(questions), done, total_calls, print_prompts)
            trials.append(t)
        all_trials.extend(trials)
        completed = [t for t in trials if not t.error]
        failed = [t for t in trials if t.error]
        n = len(completed)
        rsr_topk = (sum(t.attacker_in_topk for t in completed) / n) if n else None
        rsr_ctx = (sum(t.attacker_in_context for t in completed) / n) if n else None
        asr = (sum(t.marker_present for t in completed) / n) if n else None
        exposed = [t for t in completed if t.attacker_in_context]
        isr = (sum(t.marker_present for t in exposed) / len(exposed)) if exposed else None
        summary[cond] = {
            "n": n, "failed": len(failed), "total": len(trials),
            "RSR_topk": rsr_topk, "RSR_context": rsr_ctx,
            "ISR": isr, "ASR": asr,
        }

    # report
    print(f"{'condition':<10} {'done':>5} {'fail':>5} {'RSR_topk':>9} {'RSR_ctx':>8} {'ISR':>6} {'ASR':>6}")
    print("-" * 56)
    for cond in ("clean", "attacked", "defended"):
        s = summary[cond]
        rsr_topk = f"{s['RSR_topk']:.2f}" if s["RSR_topk"] is not None else " n/a"
        rsr_ctx = f"{s['RSR_context']:.2f}" if s["RSR_context"] is not None else " n/a"
        isr = f"{s['ISR']:.2f}" if s["ISR"] is not None else " n/a"
        asr = f"{s['ASR']:.2f}" if s["ASR"] is not None else " n/a"
        print(f"{cond:<10} {s['n']:>5}/{s['total']:<5} {s['failed']:>5} {rsr_topk:>9} {rsr_ctx:>8} {isr:>6} {asr:>6}")

    print("\nInterpretation:")
    print(f"  ASR is the fraction of answers containing the attacker marker '{MARKER}'.")
    print("  clean should be 0.00 (no attacker doc in corpus).")
    print("  attacked shows the injection landing; defended shows spotlighting's effect.")

    out = pathlib.Path("artifacts/demo_run.jsonl")
    out.parent.mkdir(exist_ok=True)
    records = [
        {
            "record_type": "summary",
            "provider": provider_note(),
            "marker": MARKER,
            "spotlighting_strategy": spotlighting_strategy or os.environ.get("INJECTRAG_SPOTLIGHTING", "boundary"),
            "summary": summary,
        }
    ]
    records.extend(
        {"record_type": "trial", **trial_to_dict(t)}
        for t in all_trials
    )
    out.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )
    print(f"\nFull trace written to {out}")


def run_ask(question: str) -> None:
    clean_pipe, poisoned_pipe, attacker_ids = build_pipelines()
    print(f"Provider: {provider_note()}\n")
    for cond, pipe in [("clean", clean_pipe), ("attacked", poisoned_pipe), ("defended", poisoned_pipe)]:
        t = pipe.answer("adhoc", question, cond)
        flag = "  <-- MARKER PRESENT" if t.marker_present else ""
        print(f"=== {cond} (attacker_in_context={t.attacker_in_context}){flag}")
        if t.spotlighting_strategy:
            print(f"    spotlighting: {t.spotlighting_strategy}")
        print(f"    model: {t.provider}/{t.model}  finish={t.finish_reason}")
        if t.error:
            print(f"    ERROR: {t.error}")
        print(f"    top-k docs: {_format_hits(t.hits)}")
        if t.highest_context_chunk:
            h = t.highest_context_chunk
            print(f"    highest context chunk: {h['document_id']} {h['chunk_id']}")
            print(f"    {_short_text(h['text'])}")
        print(f"    answer: {t.answer or '(empty)'}\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ask", type=str, default=None)
    ap.add_argument(
        "--spotlighting",
        choices=["boundary", "datamarking"],
        default=None,
        help="spotlighting strategy for the defended condition; defaults to INJECTRAG_SPOTLIGHTING or boundary",
    )
    ap.add_argument("--limit", type=int, default=None, help="run only the first N target questions")
    ap.add_argument("--print-prompts", action="store_true", help="print the exact system/user text sent to the LLM")
    ap.add_argument("--provider", choices=["fake", "gemini", "openai", "groq", "ollama"], default=None,
                    help="force a provider (overrides auto-detection)")
    ap.add_argument("--fake", action="store_true", help="force the offline fake provider")
    args = ap.parse_args()
    if args.fake:
        os.environ["INJECTRAG_PROVIDER"] = "fake"
    elif args.provider:
        os.environ["INJECTRAG_PROVIDER"] = args.provider
    if args.ask:
        if args.spotlighting:
            os.environ["INJECTRAG_SPOTLIGHTING"] = args.spotlighting
        run_ask(args.ask)
    else:
        run_all(args.spotlighting, args.limit, args.print_prompts)
