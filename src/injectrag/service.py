"""The application layer: one pipeline, one lock, two methods.

`HelpdeskService.ask` returns nothing but the answer string, and
`HelpdeskService.submit_case` returns nothing but the new document id. Every
piece of evidence -- ranked hits, which chunks reached the context, the exposure
flags, the marker verdict, the resolved provider -- goes to JsonlLogger instead,
because the browser is meant to look like an ordinary helpdesk. If you want to
know why an answer said what it said, read `logs/queries.jsonl`.

The corpus is poisoned at boot (36 clean + 5 attacker tickets), exactly as
run_demo.py:build_pipelines builds it, and grows further whenever a technician
files a case. Nothing is persistent: restart and the corpus is the 41-document
snapshot again.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import threading
from uuid import uuid4

from .index import Hit
from .logging_store import JsonlLogger
from .pipeline import Pipeline, load_documents, render_context, resolve_spotlighting_strategy
from .seed_marker import MARKER

CLEAN_CORPUS = "data/corpus/clean/documents.jsonl"
ATTACK_CORPUS = "data/corpus/attack/documents.jsonl"

DEFENSES = {"off", "boundary", "datamarking"}

TOP_K = 5

GENERATION_FAILURE_MESSAGE = (
    "Sorry, I could not reach the assistant service just now. Please try again."
)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compose_ticket_body(description: str, resolution: str) -> str:
    """Compose a resolved-ticket body.

    Copied verbatim from tools/seed_clean_corpus.py and tools/seed_attack.py so a
    case filed through the application produces byte-identical text to the seeded
    equivalent. tools/test_integration.py asserts that equivalence.
    """
    return (
        f"Employee description: {description.strip()}\n\n"
        f"Technician resolution: {resolution.strip()}"
    )


class HelpdeskService:
    def __init__(
        self,
        documents: list[dict],
        attacker_ids: set[str],
        logger: JsonlLogger,
        marker: str = MARKER,
        defense: str = "off",
    ):
        defense = (defense or "off").strip().lower()
        if defense not in DEFENSES:
            raise ValueError(f"unknown defense '{defense}'; use one of: {sorted(DEFENSES)}")
        self.defense = defense
        self.marker = marker
        self.logger = logger
        self.documents: list[dict] = list(documents)
        self.pipeline = Pipeline.from_documents(
            self.documents, attacker_doc_ids=set(attacker_ids), marker=marker
        )
        self._seq = 0
        self._lock = threading.Lock()

    # --- reporting (startup banner only; never reaches the browser) ------

    @property
    def document_count(self) -> int:
        return len(self.documents)

    @property
    def chunk_count(self) -> int:
        return len(self.pipeline.index.chunks)

    # --- answering -------------------------------------------------------

    def _context_chunk_ids(self, hits: list[dict], strategy: str | None) -> list[str]:
        """Which retrieved chunks actually fit under the evidence budget.

        Rebuilt from the chunk texts already in the index rather than by running
        retrieval a second time -- render_context only reads each hit's text,
        document_id and chunk_id, so this is pure string work with no second
        embedding pass and no API call.
        """
        texts = {c.chunk_id: c.text for c in self.pipeline.index.chunks}
        rebuilt = [
            Hit(
                rank=h["rank"],
                score=h["score"],
                chunk_id=h["chunk_id"],
                document_id=h["document_id"],
                text=texts.get(h["chunk_id"], ""),
            )
            for h in hits
        ]
        _, included = render_context(rebuilt, strategy)
        return included

    def ask(self, question: str, user: dict) -> str:
        """Answer one question. Returns the answer text and nothing else."""
        question = (question or "").strip()
        if not question:
            raise ValueError("a question needs text")

        query_id = f"q-{uuid4().hex[:8]}"
        condition = "defended" if self.defense != "off" else "attacked"
        strategy = self.defense if self.defense != "off" else None

        with self._lock:
            trial = self.pipeline.answer(
                query_id, question, condition,
                top_k=TOP_K, spotlighting_strategy=strategy, include_prompt=False,
            )
            resolved = resolve_spotlighting_strategy(condition, strategy)
            context_chunk_ids = self._context_chunk_ids(trial.hits, resolved)

            self.logger.log_query({
                "query_id": query_id,
                "user_id": user.get("user_id"),
                "username": user.get("username"),
                "display": user.get("display"),
                "question": question,
                "condition": trial.condition,
                "defense": self.defense,
                "spotlighting_strategy": trial.spotlighting_strategy,
                "retrieved": [
                    {
                        "rank": h["rank"],
                        "document_id": h["document_id"],
                        "chunk_id": h["chunk_id"],
                        "score": h["score"],
                    }
                    for h in trial.hits
                ],
                "context_chunk_ids": context_chunk_ids,
                "highest_context_chunk": trial.highest_context_chunk,
                "attacker_in_topk": trial.attacker_in_topk,
                "attacker_in_context": trial.attacker_in_context,
                "marker": self.marker,
                "marker_present": trial.marker_present,
                "answer": trial.answer,
                "provider": trial.provider,
                "model": trial.model,
                "finish_reason": trial.finish_reason,
                "error": trial.error,
            })

        if trial.error:
            # The provider failure is already in the log with its exact text. The
            # browser gets an apology and nothing else -- never a stack trace or a
            # vendor error string.
            return GENERATION_FAILURE_MESSAGE
        return trial.answer

    # --- ingestion -------------------------------------------------------

    def submit_case(self, case: dict, user: dict) -> str:
        """File a resolved case into the live corpus. Returns the document id."""
        case_date = (case.get("case_date") or "").strip()
        title = (case.get("title") or "").strip()
        description = (case.get("description") or "").strip()
        resolution = (case.get("resolution") or "").strip()
        for name, value in (
            ("case_date", case_date), ("title", title),
            ("description", description), ("resolution", resolution),
        ):
            if not value:
                raise ValueError(f"{name} must not be blank")

        with self._lock:
            self._seq += 1
            document_id = f"C{self._seq:02d}"
            body = compose_ticket_body(description, resolution)
            document = {
                "schema_version": 1,
                "document_id": document_id,
                "source_type": "resolved_ticket",
                "membership": "attacker",
                "topic": "recovery",
                "title": title,
                "body": body,
                "employee_description": description,
                "technician_resolution": resolution,
                "source_ref": f"workflow/cases/{document_id}",
                "case_date": case_date,
                "content_hash": content_hash(body),
            }
            # `attacker=True` is an operator label for exposure bookkeeping, not an
            # inference: in this build the technician is the adversary, so anything
            # they file is attacker-authored by construction. add_document still
            # never inspects the body to decide membership.
            added = self.pipeline.add_document(document, attacker=True)
            self.documents.append(document)

            self.logger.log_ingestion({
                "document_id": document_id,
                "user_id": user.get("user_id"),
                "username": user.get("username"),
                "display": user.get("display"),
                "case_date": case_date,
                "title": title,
                "description": description,
                "resolution": resolution,
                "content_hash": document["content_hash"],
                "chunks_added": added,
                "corpus_documents_after": len(self.documents),
                "corpus_chunks_after": len(self.pipeline.index.chunks),
            })
            return document_id


def provider_label() -> str:
    provider = os.environ.get("INJECTRAG_PROVIDER", "auto").strip().lower()
    if provider == "groq" or (provider == "auto" and os.environ.get("GROQ_API_KEY")):
        return f"groq ({os.environ.get('INJECTRAG_GROQ_MODEL', 'openai/gpt-oss-20b')})"
    if provider == "openai" or (provider == "auto" and os.environ.get("OPENAI_API_KEY")):
        return f"openai ({os.environ.get('INJECTRAG_OPENAI_MODEL', 'gpt-oss-20b')})"
    if provider == "fake":
        return "fake (offline)"
    if provider == "ollama":
        return f"ollama ({os.environ.get('INJECTRAG_OLLAMA_MODEL', 'llama3.1:8b')}, local)"
    if provider == "gemini" or (
        provider == "auto"
        and (os.environ.get("INJECTRAG_GEMINI_KEYS") or os.environ.get("GEMINI_API_KEY"))
    ):
        return f"gemini ({os.environ.get('INJECTRAG_GEMINI_MODEL', 'gemini-3.8-flash')})"
    return "fake (no API key set)"


def resolved_defense() -> str:
    defense = os.environ.get("INJECTRAG_DEFENSE", "off").strip().lower() or "off"
    if defense not in DEFENSES:
        raise ValueError(
            f"INJECTRAG_DEFENSE='{defense}' is not valid; use one of: {sorted(DEFENSES)}"
        )
    return defense


def build_service(log_dir: str | None = None, defense: str | None = None) -> HelpdeskService:
    """Build the poisoned service exactly as run_demo.py:build_pipelines does.

    41 documents: the 36 clean ones plus the 5 frozen attacker tickets, whose ids
    become the attacker set. Unlike the documented snapshot runner, this index is
    then allowed to grow as cases are filed.
    """
    for path in (CLEAN_CORPUS, ATTACK_CORPUS):
        if not pathlib.Path(path).exists():
            raise FileNotFoundError(
                f"{path} not found; run tools/seed_clean_corpus.py and tools/seed_attack.py first"
            )
    clean_docs = load_documents(CLEAN_CORPUS)
    attack_docs = load_documents(ATTACK_CORPUS)
    attacker_ids = {d["document_id"] for d in attack_docs}
    return HelpdeskService(
        clean_docs + attack_docs,
        attacker_ids,
        JsonlLogger(log_dir),
        marker=MARKER,
        defense=defense if defense is not None else resolved_defense(),
    )
