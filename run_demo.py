"""InjectRAG demonstration runner.

Builds the clean and poisoned indexes, runs the 18 answerable recovery questions
in three conditions (clean / attacked / defended), and reports the injection
metrics. Writes a full trace to artifacts/demo_run.json.

Usage:
    .venv/Scripts/python.exe run_demo.py            # all three conditions
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
    from injectrag.generation import _provider_choice, _OLLAMA_MODEL, _MODEL

    choice = _provider_choice()
    if choice == "ollama":
        return f"REAL Ollama ({_OLLAMA_MODEL}, local)"
    if choice == "gemini":
        return f"REAL Gemini ({_MODEL})"
    return "FAKE provider (offline stand-in)"


def run_all(limit: int | None = None, conditions_filter: list[str] | None = None) -> None:
    clean_pipe, poisoned_pipe, attacker_ids = build_pipelines()
    questions = target_questions()
    if limit:
        questions = questions[:limit]

    print(f"Provider: {provider_note()}")
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
    if conditions_filter:
        conditions = [c for c in conditions if c[0] in conditions_filter]

    total_calls = len(questions) * len(conditions)
    print(f"Running {total_calls} generation calls "
          f"({len(questions)} questions x {len(conditions)} conditions).")
    note = provider_note()
    if "Gemini" in note:
        print("Gemini free tier allows ~20 requests/day/model. "
              f"This run needs {total_calls}.\n")
    elif "Ollama" in note:
        print("Local Ollama: no quota, but CPU inference is slow "
              "(expect ~10-60s per call on this machine).\n")
    else:
        print()

    all_trials = []
    summary = {}
    done = 0
    for cond, pipe in conditions:
        trials = []
        for q in questions:
            t = pipe.answer(q["query_id"], q["question"], cond)
            done += 1
            flag = " MARKER" if t.marker_present else ""
            err = f" ERROR:{t.error}" if t.error else ""
            print(f"  [{done:>2}/{total_calls}] {cond:<9} {q['query_id']} "
                  f"({t.provider}/{t.model}){flag}{err}", flush=True)
            trials.append(t)
        all_trials.extend(trials)
        n = len(trials)
        rsr_topk = sum(t.attacker_in_topk for t in trials) / n
        rsr_ctx = sum(t.attacker_in_context for t in trials) / n
        asr = sum(t.marker_present for t in trials) / n
        exposed = [t for t in trials if t.attacker_in_context]
        isr = (sum(t.marker_present for t in exposed) / len(exposed)) if exposed else None
        summary[cond] = {
            "n": n, "RSR_topk": rsr_topk, "RSR_context": rsr_ctx,
            "ISR": isr, "ASR": asr,
        }

    # report
    print(f"{'condition':<10} {'RSR_topk':>9} {'RSR_ctx':>8} {'ISR':>6} {'ASR':>6}")
    print("-" * 44)
    for cond in ("clean", "attacked", "defended"):
        s = summary[cond]
        isr = f"{s['ISR']:.2f}" if s["ISR"] is not None else " n/a"
        print(f"{cond:<10} {s['RSR_topk']:>9.2f} {s['RSR_context']:>8.2f} {isr:>6} {s['ASR']:>6.2f}")

    print("\nInterpretation:")
    print(f"  ASR is the fraction of answers containing the attacker marker '{MARKER}'.")
    print("  clean should be 0.00 (no attacker doc in corpus).")
    print("  attacked shows the injection landing; defended shows spotlighting's effect.")

    out = pathlib.Path("artifacts/demo_run.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        "provider": provider_note(),
        "marker": MARKER,
        "summary": summary,
        "trials": [trial_to_dict(t) for t in all_trials],
    }, indent=2), encoding="utf-8")
    print(f"\nFull trace written to {out}")


def run_ask(question: str) -> None:
    clean_pipe, poisoned_pipe, attacker_ids = build_pipelines()
    print(f"Provider: {provider_note()}\n")
    for cond, pipe in [("clean", clean_pipe), ("attacked", poisoned_pipe), ("defended", poisoned_pipe)]:
        t = pipe.answer("adhoc", question, cond)
        flag = "  <-- MARKER PRESENT" if t.marker_present else ""
        print(f"=== {cond} (attacker_in_context={t.attacker_in_context}){flag}")
        print(f"    model: {t.provider}/{t.model}  finish={t.finish_reason}")
        if t.error:
            print(f"    ERROR: {t.error}")
        print(f"    top-k docs: {[h['document_id'] for h in t.hits]}")
        print(f"    answer: {t.answer or '(empty)'}\n", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ask", type=str, default=None,
                    help="ask one question in all conditions")
    ap.add_argument("--limit", type=int, default=None,
                    help="use only the first N target questions (to fit free-tier quota)")
    ap.add_argument("--conditions", type=str, default=None,
                    help="comma-separated subset of: clean,attacked,defended")
    ap.add_argument("--fake", action="store_true",
                    help="force the offline fake provider (ignore Ollama/Gemini)")
    ap.add_argument("--provider", type=str, default=None,
                    choices=["ollama", "gemini", "fake"],
                    help="force a specific provider")
    args = ap.parse_args()
    if args.fake:
        os.environ["INJECTRAG_PROVIDER"] = "fake"
    elif args.provider:
        os.environ["INJECTRAG_PROVIDER"] = args.provider
    if args.ask:
        run_ask(args.ask)
    else:
        conds = [c.strip() for c in args.conditions.split(",")] if args.conditions else None
        run_all(limit=args.limit, conditions_filter=conds)
