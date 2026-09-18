"""Wiring checks for the helpdesk application demo.

Verifies that the app's ingestion path really reaches the index and that the
chat endpoint really reaches the pipeline. Runs offline on the fake provider.

Run:  INJECTRAG_PROVIDER=fake .venv/bin/python tools/test_app.py
"""

import os
import pathlib
import sys

os.environ["INJECTRAG_PROVIDER"] = "fake"
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from injectrag.pipeline import Pipeline, load_documents

CLEAN = "data/corpus/clean/documents.jsonl"
ATTACK = "data/corpus/attack/documents.jsonl"

failures = []


def check(name, cond):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        failures.append(name)


def report():
    print()
    if failures:
        print(f"{len(failures)} check(s) FAILED: {failures}")
        sys.exit(1)
    print("all application checks passed")


clean_docs = load_documents(CLEAN)
attack_docs = load_documents(ATTACK)

# --- Task 1: runtime index growth ---------------------------------------
pipe = Pipeline.from_documents(clean_docs, attacker_doc_ids=set(), marker="")
baseline_chunks = len(pipe.index.chunks)
check("clean index builds 36 documents", len(clean_docs) == 36)

p01 = next(d for d in attack_docs if d["document_id"] == "P01")
added = pipe.add_document(p01, attacker=True)
check("add_document reports chunks added", added > 0)
check("index grew by exactly that many chunks",
      len(pipe.index.chunks) == baseline_chunks + added)
check("added document is registered as attacker-owned",
      "P01" in pipe.attacker_doc_ids)

hits = pipe.index.search("My account is locked, what should I do?", top_k=5)
check("runtime-added document is retrievable",
      any(h.document_id == "P01" for h in hits))

pipe.index.truncate(baseline_chunks)
check("truncate restores the clean chunk count",
      len(pipe.index.chunks) == baseline_chunks)
hits_after = pipe.index.search("My account is locked, what should I do?", top_k=5)
check("no attacker document survives truncation",
      not any(h.document_id == "P01" for h in hits_after))

report()
