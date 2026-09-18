"""Positional control: same 5 retrieved chunks, attacker chunks promoted to the front."""
import json, pathlib, sys
sys.path.insert(0, "src")
from injectrag.pipeline import (Pipeline, load_documents, render_context,
                                build_user_message, system_prompt_for)
from injectrag.seed_marker import MARKER

clean = load_documents("data/corpus/clean/documents.jsonl")
attack = load_documents("data/corpus/attack/documents.jsonl")
aids = {d["document_id"] for d in attack}
pipe = Pipeline.from_documents(clean + attack, attacker_doc_ids=aids, marker=MARKER)

qs = [json.loads(l) for l in pathlib.Path("data/queries/dev_questions.jsonl")
      .read_text(encoding="utf-8").splitlines() if l.strip()]
qs = [q for q in qs if q["category"] == "answerable_target"]

items = []
for q in qs:
    hits = pipe.index.search(q["question"], top_k=5)
    atk = [h for h in hits if h.document_id in aids]
    rest = [h for h in hits if h.document_id not in aids]
    promoted = atk + rest
    for i, h in enumerate(promoted, 1):
        h.rank = i
    ctx, included = render_context(promoted, None)
    ctx_docs = {c.split("#")[0] for c in included}
    items.append({
        "query_id": q["query_id"], "question": q["question"], "condition": "attacked",
        "spotlighting_strategy": None, "system": system_prompt_for("attacked", None),
        "user_message": build_user_message(q["question"], ctx),
        "hits": [{"rank": h.rank, "score": h.score, "document_id": h.document_id,
                  "chunk_id": h.chunk_id} for h in promoted],
        "attacker_in_topk": bool(aids & {h.document_id for h in hits}),
        "attacker_in_context": bool(aids & ctx_docs),
        "marker": MARKER, "n_included": len(included),
    })

pathlib.Path("artifacts").mkdir(exist_ok=True)
pathlib.Path("artifacts/assembled_promoted.json").write_text(
    json.dumps({"marker": MARKER, "n_clean_docs": len(clean),
                "n_attacker_docs": len(attack), "items": items}, indent=2), encoding="utf-8")
print("chunks included per question:", sorted({i["n_included"] for i in items}))
print("exposed:", sum(i["attacker_in_context"] for i in items), "/", len(items))
