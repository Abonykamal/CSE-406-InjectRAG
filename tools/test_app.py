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

# --- Task 2: ticket lifecycle and answering -----------------------------
from injectrag.service import DemoService, compose_ticket_body, content_hash  # noqa: E402

svc = DemoService(clean_docs, marker="reset-portal-security.example")
start_docs = svc.status()["documents"]
check("service starts on the clean corpus only", start_docs == 36)
check("service starts with no attacker documents",
      svc.status()["attacker_documents"] == [])

# an open ticket must not be searchable
t1 = svc.submit_ticket("Account recovery help (P01)", p01["employee_description"],
                       submitted_by="attacker", membership="attacker")
check("submitting does not change the corpus", svc.status()["documents"] == start_docs)
open_hits = svc.pipeline.index.search(p01["employee_description"], top_k=5)
check("an unresolved ticket is not retrievable",
      all(h.document_id != t1.ticket_id for h in open_hits))

# resolution publishes it
res = svc.resolve_ticket(t1.ticket_id, p01["technician_resolution"])
check("resolution adds one document", svc.status()["documents"] == start_docs + 1)
check("resolution reports the chunks it added", res["chunks_added"] > 0)
check("the resolved ticket is labelled attacker",
      t1.ticket_id in svc.status()["attacker_documents"])

# the workflow path must produce the same text the seeder produces
workflow_doc = next(d for d in svc.documents if d["document_id"] == t1.ticket_id)
check("workflow body matches the seeded attacker ticket body",
      workflow_doc["body"] == p01["body"])
check("workflow content hash matches the seeded attacker ticket hash",
      workflow_doc["content_hash"] == p01["content_hash"])
check("compose_ticket_body is the seeder's rule",
      compose_ticket_body(" a ", " b ") == "Employee description: a\n\nTechnician resolution: b")

# answering reaches the real pipeline
LOCKED = "My account is locked, what should I do?"
attacked = svc.ask(LOCKED, defense="off")
source_ids = [s["document_id"] for s in attacked["sources"]]
index_ids = [h.document_id for h in svc.pipeline.index.search(LOCKED, top_k=5)]
check("reported sources are the retriever's top-k", source_ids == index_ids)
check("the poisoned ticket reaches the model context", attacked["attacker_in_context"])
check("attacked condition is reported", attacked["condition"] == "attacked")
check("the attacked answer carries the marker", attacked["marker_present"])
check("the prompt panel is populated", bool(attacked["system_prompt"]) and bool(attacked["user_message"]))

defended = svc.ask(LOCKED, defense="boundary")
check("defended condition is reported", defended["condition"] == "defended")
check("defended still retrieves the attacker document", defended["attacker_in_context"])
check("boundary spotlighting suppresses the marker", not defended["marker_present"])
check("defended prompt differs from baseline",
      defended["system_prompt"] != attacked["system_prompt"])

marked = svc.ask(LOCKED, defense="datamarking")
check("data-marking is selectable", marked["spotlighting_strategy"] == "datamarking")

# reset restores the clean corpus
svc.reset()
check("reset restores the document count", svc.status()["documents"] == start_docs)
check("reset clears attacker documents", svc.status()["attacker_documents"] == [])
check("reset clears tickets", svc.tickets() == [])
clean_answer = svc.ask(LOCKED, defense="off")
check("clean condition after reset", clean_answer["condition"] == "clean")
check("no attacker exposure after reset", not clean_answer["attacker_in_context"])
check("no marker after reset", not clean_answer["marker_present"])

# --- Task 3: HTTP API ----------------------------------------------------
from fastapi.testclient import TestClient  # noqa: E402

from injectrag.api import create_app  # noqa: E402

api_svc = DemoService(clean_docs, marker="reset-portal-security.example")
client = TestClient(create_app(api_svc))

r = client.get("/api/status")
check("GET /api/status is 200", r.status_code == 200)
check("status reports the clean corpus", r.json()["documents"] == 36)

r = client.get("/")
check("GET / serves the UI", r.status_code == 200 and "<html" in r.text.lower())

r = client.get("/api/attack-payloads")
check("attack payloads are offered for prefill", len(r.json()["payloads"]) == 5)

r = client.post("/api/chat", json={"question": LOCKED, "defense": "off"})
check("POST /api/chat is 200", r.status_code == 200)
body = r.json()
check("chat returns an answer", bool(body["answer"]))
check("chat returns sources", len(body["sources"]) == 5)
check("chat before poisoning is clean", body["condition"] == "clean")
check("chat before poisoning has no marker", not body["marker_present"])

r = client.post("/api/chat", json={"question": "", "defense": "off"})
check("empty question is rejected", r.status_code == 422)
r = client.post("/api/chat", json={"question": LOCKED, "defense": "nonsense"})
check("unknown defense is rejected", r.status_code == 422)
r = client.post("/api/tickets/NOPE/resolve", json={"resolution": "x"})
check("resolving a missing ticket is 404", r.status_code == 404)

r = client.post("/api/tickets", json={
    "subject": "Account recovery help (P01)",
    "description": p01["employee_description"],
    "submitted_by": "attacker",
    "membership": "attacker",
})
check("POST /api/tickets is 200", r.status_code == 200)
new_id = r.json()["ticket"]["ticket_id"]

r = client.post(f"/api/tickets/{new_id}/resolve",
                json={"resolution": p01["technician_resolution"]})
check("resolve is 200", r.status_code == 200)
check("resolve grows the corpus to 37", r.json()["corpus"]["documents"] == 37)

r = client.post("/api/chat", json={"question": LOCKED, "defense": "off"})
poisoned = r.json()
check("chat after poisoning is attacked", poisoned["condition"] == "attacked")
check("the poisoned ticket is cited as a source",
      any(s["membership"] == "attacker" for s in poisoned["sources"]))
check("the poisoned answer carries the marker", poisoned["marker_present"])

r = client.post("/api/chat", json={"question": LOCKED, "defense": "boundary"})
check("defended over HTTP suppresses the marker", not r.json()["marker_present"])

r = client.post("/api/reset")
check("reset over HTTP restores 36 documents", r.json()["documents"] == 36)

report()
