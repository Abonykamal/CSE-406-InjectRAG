"""Fast offline sanity checks for the demo pipeline. No network, no API key.

Run:  .venv/Scripts/python.exe tools/smoke_test.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from injectrag.chunking import chunk_document
from injectrag.pipeline import Pipeline, datamark_text, load_documents, render_context, system_prompt_for
from injectrag.seed_marker import MARKER

CLEAN = "data/corpus/clean/documents.jsonl"
ATTACK = "data/corpus/attack/documents.jsonl"

failures = []


def check(name, cond):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        failures.append(name)


clean = load_documents(CLEAN)
att = load_documents(ATTACK)

check("36 clean documents", len(clean) == 36)
check("5 attacker documents", len(att) == 5)
check("marker absent from clean corpus",
      MARKER.lower() not in pathlib.Path(CLEAN).read_text(encoding="utf-8").lower())

# each attacker ticket keeps cover + injection in one retrievable chunk
for d in att:
    chunks = chunk_document(d["document_id"], d["body"])
    has_marker_chunk = any(MARKER in c.text for c in chunks)
    check(f"{d['document_id']} has a chunk containing the injected marker", has_marker_chunk)

# build poisoned index and confirm retrieval + exposure on a target question
ids = {d["document_id"] for d in att}
pipe = Pipeline.from_documents(clean + att, attacker_doc_ids=ids, marker=MARKER)
t = pipe.answer("smoke", "I forgot my password, how do I reset it?", "attacked")
check("attacker document reaches top-k on a target question", t.attacker_in_topk)
check("attacker content reaches the model context", t.attacker_in_context)

# clean index never exposes attacker content
clean_pipe = Pipeline.from_documents(clean, attacker_doc_ids=ids, marker=MARKER)
tc = clean_pipe.answer("smoke", "I forgot my password, how do I reset it?", "clean")
check("clean condition never exposes attacker content", not tc.attacker_in_context)

# spotlighting system prompts differ from baseline
from injectrag.pipeline import BASELINE_SYSTEM, DATAMARKING_SYSTEM, SPOTLIGHTING_SYSTEM
check("spotlighting prompt adds a handling rule", len(SPOTLIGHTING_SYSTEM) > len(BASELINE_SYSTEM))
check("data-marking prompt adds a handling rule", len(DATAMARKING_SYSTEM) > len(BASELINE_SYSTEM))
check("boundary defended prompt selected", system_prompt_for("defended", "boundary") == SPOTLIGHTING_SYSTEM)
check("data-marking defended prompt selected", system_prompt_for("defended", "datamarking") == DATAMARKING_SYSTEM)

marked = datamark_text("Reset your password.")
check("data marking interleaves marker", marked == "Reset^ your^ password.")
ctx, _ = render_context(pipe.index.search("I forgot my password", top_k=1), "datamarking")
check("data-marked context contains marker", " ^" in ctx)

print()
if failures:
    print(f"{len(failures)} check(s) FAILED: {failures}")
    sys.exit(1)
print("all smoke checks passed")
