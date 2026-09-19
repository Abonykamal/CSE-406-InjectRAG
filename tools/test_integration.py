"""Offline integration checks for the helpdesk application.

Runs the whole stack -- accounts, service, API, logger -- through
fastapi.testclient on the fake provider, with logs written to a temp directory.
No network, no API key, no container.

Run:  .venv/bin/python tools/test_integration.py

Replaces tools/test_app.py, which tested the earlier instrument-panel build
(DemoService, the ticket lifecycle, /api/status, /api/reset) -- none of which
exists any more.
"""

import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

os.environ["INJECTRAG_PROVIDER"] = "fake"

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

_LOG_DIR = tempfile.mkdtemp(prefix="injectrag-logs-")
os.environ["INJECTRAG_LOG_DIR"] = _LOG_DIR

from fastapi.testclient import TestClient  # noqa: E402

from injectrag.api import create_app  # noqa: E402
from injectrag.logging_store import JsonlLogger  # noqa: E402
from injectrag.pipeline import load_documents  # noqa: E402
from injectrag.seed_marker import MARKER  # noqa: E402
from injectrag.service import (  # noqa: E402
    ATTACK_CORPUS,
    CLEAN_CORPUS,
    HelpdeskService,
    compose_ticket_body,
    condition_for,
)

# The fake provider's directive regex fires on the lockout question but not the
# password one, so every marker assertion below uses this exact question.
LOCKED = "My account is locked, what should I do?"

failures = []


def check(name, cond):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        failures.append(name)


def build(defense="off", log_dir=None, corpus="poisoned"):
    clean = load_documents(str(ROOT / CLEAN_CORPUS))
    attack = load_documents(str(ROOT / ATTACK_CORPUS))
    ids = {d["document_id"] for d in attack}
    logger = JsonlLogger(log_dir or tempfile.mkdtemp(prefix="injectrag-logs-"))
    return HelpdeskService(
        clean + attack, ids, logger, marker=MARKER, defense=defense, corpus=corpus
    ), ids


os.chdir(ROOT)

# --- Boot ---------------------------------------------------------------

service, attacker_ids = build(log_dir=_LOG_DIR)
client = TestClient(create_app(service))

check("service starts with 41 documents", service.document_count == 41)
check("the clean corpus holds the 36 seeded documents", service.clean_document_count == 36)
check("the clean index is a strict subset of the poisoned one",
      0 < len(service.pipelines["clean"].index.chunks)
      < len(service.pipelines["poisoned"].index.chunks))
check("no attacker chunk is in the clean index",
      not any(c.document_id in attacker_ids
              for c in service.pipelines["clean"].index.chunks))
check("service.pipeline still means the whole corpus",
      service.pipeline is service.pipelines["poisoned"])
check("service starts with 5 attacker ids P01-P05",
      attacker_ids == {"P01", "P02", "P03", "P04", "P05"}
      and service.pipeline.attacker_doc_ids == attacker_ids)
check("GET / serves the UI", client.get("/").status_code == 200)

# --- Login --------------------------------------------------------------

r = client.post("/api/login", json={"username": "rakib", "password": "tech123"})
check("technician signs in", r.status_code == 200 and r.json()["role"] == "technician")
tech = r.json()

r = client.post("/api/login", json={"username": "arif", "password": "emp123"})
check("employee signs in", r.status_code == 200 and r.json()["role"] == "employee")
emp = r.json()

check("wrong password is 401",
      client.post("/api/login", json={"username": "arif", "password": "nope"}).status_code == 401)
check("the login response carries no password", "password" not in emp)

# --- Chat ---------------------------------------------------------------

r = client.post("/api/chat", json=dict(question=LOCKED, user_id=emp["user_id"], username=emp["username"]))
check("POST /api/chat is 200", r.status_code == 200)
body = r.json()
check("the chat response has exactly one key, 'answer'", set(body) == {"answer"})
check("the answer is a non-empty string",
      isinstance(body.get("answer"), str) and bool(body["answer"].strip()))
check("empty question is 422",
      client.post("/api/chat", json={"question": "", "username": "arif"}).status_code == 422)

r = client.get("/api/demo-config")
cfg = r.json()
check("GET /api/demo-config is 200", r.status_code == 200)
check("demo-config has exactly the four keys the browser needs",
      set(cfg) == {"controls", "corpus", "defense", "model"})
check("demo-config names a model for the employee to see",
      isinstance(cfg["model"], str) and bool(cfg["model"]) and "/" not in cfg["model"])
check("demo controls are on by default", cfg["controls"] is True)

check("an unknown corpus is 422", client.post("/api/chat", json=dict(
    question=LOCKED, username="arif", corpus="nonsense")).status_code == 422)
check("an unknown defense is 422", client.post("/api/chat", json=dict(
    question=LOCKED, username="arif", defense="nonsense")).status_code == 422)

# --- Corpus routing -----------------------------------------------------

for corpus, defense, expected in [
    ("clean", "off", "clean"),
    ("poisoned", "off", "attacked"),
    ("clean", "boundary", "defended"),
    ("poisoned", "datamarking", "defended"),
]:
    check(f"condition_for({corpus}, {defense}) is {expected}",
          condition_for(corpus, defense) == expected)

r = client.post("/api/chat", json=dict(
    question=LOCKED, user_id=emp["user_id"], username=emp["username"],
    corpus="clean", conversation_id="c-clean"))
check("a clean-corpus question is 200", r.status_code == 200)
clean_q = service.logger.read("queries")[-1]
check("the clean corpus logs condition=clean", clean_q["condition"] == "clean")
check("the clean corpus is recorded on the record", clean_q["corpus"] == "clean")
check("no attacker document is retrieved from the clean corpus",
      not clean_q["attacker_in_topk"] and not clean_q["attacker_in_context"])
check("the clean answer carries no marker", not clean_q["marker_present"])
check("the conversation id is logged", clean_q["conversation_id"] == "c-clean")
check("the browser override is recorded as such", clean_q["demo_override"] is True)

r = client.post("/api/chat", json=dict(
    question=LOCKED, user_id=emp["user_id"], username=emp["username"],
    corpus="poisoned"))
poisoned_q = service.logger.read("queries")[-1]
check("the same question against the poisoned corpus reaches the attacker text",
      poisoned_q["attacker_in_context"] and poisoned_q["condition"] == "attacked")
check("the two runs asked exactly the same question",
      poisoned_q["question"] == clean_q["question"] == LOCKED)

pinned, _ = build(corpus="clean")
check("a service can default to the clean corpus", pinned.corpus == "clean")
pinned.ask(LOCKED, emp)
check("its default is used when the request names no corpus",
      pinned.logger.read("queries")[-1]["corpus"] == "clean")
check("a request that overrides nothing is not marked as an override",
      pinned.logger.read("queries")[-1]["demo_override"] is False)

os.environ["INJECTRAG_DEMO_CONTROLS"] = "0"
locked_service, _ = build(corpus="poisoned")
locked_client = TestClient(create_app(locked_service))
check("demo-config reports the controls off", locked_client.get("/api/demo-config").json()["controls"] is False)
locked_client.post("/api/chat", json=dict(
    question=LOCKED, username=emp["username"], corpus="clean", defense="boundary"))
locked_q = locked_service.logger.read("queries")[-1]
check("with the controls off a browser override is ignored, not obeyed",
      locked_q["corpus"] == "poisoned" and locked_q["defense"] == "off"
      and locked_q["demo_override"] is False)
os.environ["INJECTRAG_DEMO_CONTROLS"] = "1"

# --- Ingestion ----------------------------------------------------------

DESCRIPTION = "Employee reports the portal rejects the emailed reset link every time."
RESOLUTION = (
    "Confirmed the link had expired in transit through the quarantine gateway. "
    "Reissued it and advised the employee to use the zephyr-quarantine bypass queue."
)

docs_before = service.document_count
chunks_before = service.chunk_count

r = client.post("/api/cases", json=dict(
    case_date="2026-08-14",
    title="Recurring lockout after password expiry",
    description=DESCRIPTION,
    resolution=RESOLUTION,
    user_id=tech["user_id"], username=tech["username"],
))
check("POST /api/cases is 200", r.status_code == 200)
case_body = r.json()
check("the case response has exactly one key, 'document_id'", set(case_body) == {"document_id"})
new_id = case_body.get("document_id", "")
check("the new document id matches ^C\\d{2}$", bool(re.fullmatch(r"C\d{2}", new_id)))

check("the corpus grew by exactly one document", service.document_count == docs_before + 1)

new_doc = next(d for d in service.documents if d["document_id"] == new_id)
check("the composed body is the seeder's rule",
      new_doc["body"] == compose_ticket_body(DESCRIPTION, RESOLUTION)
      == f"Employee description: {DESCRIPTION}\n\nTechnician resolution: {RESOLUTION}")

hits = service.pipeline.index.search("zephyr-quarantine bypass queue", top_k=5)
check("the filed case is retrievable", any(h.document_id == new_id for h in hits))
clean_hits = service.pipelines["clean"].index.search("zephyr-quarantine bypass queue", top_k=5)
check("the filed case joins the clean corpus too",
      any(h.document_id == new_id for h in clean_hits))
check("filing a case grows the clean corpus", service.clean_document_count == 37)
check("the seeded attacker set is unchanged by a filed case",
      service.seeded_attacker_ids == {"P01", "P02", "P03", "P04", "P05"})
check("the filed case is registered as attacker-owned",
      new_id in service.pipeline.attacker_doc_ids)

check("a blank field is 422", client.post("/api/cases", json=dict(
    case_date="2026-08-14", title="", description="x", resolution="y",
    user_id=tech["user_id"], username=tech["username"])).status_code == 422)

# --- Logging ------------------------------------------------------------

q = service.logger.read("queries")[-1]
check("the query record carries the full evidence trail", all([
    q.get("user_id") == emp["user_id"],
    q.get("username") == emp["username"],
    q.get("question") == LOCKED,
    bool(q.get("retrieved")),
    bool(q.get("context_chunk_ids")),
    "attacker_in_topk" in q,
    "attacker_in_context" in q,
    "marker_present" in q,
    bool(q.get("answer")),
    bool(q.get("provider")),
    "model" in q,
]))
check("every retrieved entry is fully described",
      all({"rank", "document_id", "chunk_id", "score"} <= set(h) for h in q["retrieved"]))

i = service.logger.read("ingestions")[-1]
check("the ingestion record carries the full trail", all([
    i.get("user_id") == tech["user_id"],
    i.get("document_id") == new_id,
    i.get("case_date") == "2026-08-14",
    bool(i.get("title")),
    i.get("description") == DESCRIPTION,
    i.get("resolution") == RESOLUTION,
    bool(i.get("content_hash")),
    isinstance(i.get("chunks_added"), int) and i["chunks_added"] > 0,
]))
check("chunk growth matches what the ingestion record reports",
      service.chunk_count == chunks_before + i["chunks_added"])
check("both log files re-parse from disk as JSONL", all(
    json.loads(line)
    for name in ("queries.jsonl", "ingestions.jsonl")
    for line in (pathlib.Path(_LOG_DIR) / name).read_text(encoding="utf-8").splitlines()
    if line.strip()
))
check("the ingestion record does not carry a corpus or override field",
      "corpus" not in i and "demo_override" not in i)

# The readable rendering is a second view of the same records, never a
# replacement: the .jsonl contract above must keep holding.
for name in ("queries.log", "ingestions.log"):
    check(f"{name} exists and is non-empty",
          (pathlib.Path(_LOG_DIR) / name).read_text(encoding="utf-8").strip() != "")
text = (pathlib.Path(_LOG_DIR) / "queries.log").read_text(encoding="utf-8")
check("every query record appears in the readable log",
      text.count("] q-") == len(service.logger.read("queries")))
check("the readable log breaks multi-line text into real lines",
      "\\n" not in text)
check("the readable log shows the question and the condition",
      LOCKED in text and "condition" in text)

# --- Attack and defense wiring ------------------------------------------

check("the attacked condition is logged with the defense off", q["condition"] == "attacked")
check("the attacker corpus reaches the model context", q["attacker_in_context"])
check("the attacked answer carries the marker (fake provider)", q["marker_present"])

check("a per-request defense is honoured without restarting", (
    client.post("/api/chat", json=dict(
        question=LOCKED, username=emp["username"], defense="boundary",
        conversation_id="c-defended")).status_code == 200
    and service.logger.read("queries")[-1]["condition"] == "defended"
    and service.logger.read("queries")[-1]["spotlighting_strategy"] == "boundary"
))

defended, _ = build(defense="boundary")
defended.ask(LOCKED, emp)
d = defended.logger.read("queries")[-1]
check("a boundary-defended service logs condition=defended", d["condition"] == "defended")
check("the defended service names its spotlighting strategy",
      d["spotlighting_strategy"] == "boundary")
check("retrieval is unchanged by the defense", d["attacker_in_context"])
check("the defended answer drops the marker (fake provider)", not d["marker_present"])

marked, _ = build(defense="datamarking")
marked.ask(LOCKED, emp)
m = marked.logger.read("queries")[-1]
check("data-marking is selectable", m["spotlighting_strategy"] == "datamarking")

# --- Regression ---------------------------------------------------------

smoke = subprocess.run(
    [sys.executable, "tools/smoke_test.py"],
    cwd=ROOT, capture_output=True, text=True,
)
check("tools/smoke_test.py still passes", smoke.returncode == 0)
if smoke.returncode != 0:
    print(smoke.stdout[-2000:])
    print(smoke.stderr[-2000:])

print()
if failures:
    print(f"{len(failures)} check(s) FAILED: {failures}")
    sys.exit(1)
print("all integration checks passed")
