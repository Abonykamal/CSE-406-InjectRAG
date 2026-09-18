"""In-memory demo service: ticket lifecycle, live ingestion, and answering.

This is the whole application layer for the demonstration build. It holds one
Pipeline whose index grows when a technician resolves a ticket, which is how the
indirect injection is performed live in front of an audience rather than being
pre-baked into a snapshot.

Nothing here is persistent by design -- restart and the corpus is clean again.
The documented system (SQLite accounts/tickets/threads, Qdrant, publication
orchestration) is a separate track; see DEMO.md.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import threading
from dataclasses import asdict, dataclass

from .pipeline import Pipeline, load_documents
from .seed_marker import MARKER

CLEAN_CORPUS = "data/corpus/clean/documents.jsonl"
ATTACK_CORPUS = "data/corpus/attack/documents.jsonl"

DEFENSES = {"off", "boundary", "datamarking"}


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compose_ticket_body(description: str, resolution: str) -> str:
    """Compose a resolved-ticket body.

    This rule is copied verbatim from tools/seed_clean_corpus.py and
    tools/seed_attack.py so that a ticket resolved through the application
    produces byte-identical text to the seeded equivalent. tools/test_app.py
    asserts that equivalence.
    """
    return (
        f"Employee description: {description.strip()}\n\n"
        f"Technician resolution: {resolution.strip()}"
    )


@dataclass
class Ticket:
    ticket_id: str
    subject: str
    submitted_by: str
    membership: str  # clean | attacker -- an operator label, never inferred
    employee_description: str
    status: str = "open"  # open | resolved
    technician_resolution: str | None = None
    document_id: str | None = None
    chunks_added: int = 0


@dataclass
class _Snapshot:
    chunk_count: int
    document_count: int


class DemoService:
    """One live index plus the tickets that can grow it."""

    def __init__(self, clean_documents: list[dict], marker: str = MARKER):
        self.marker = marker
        self.pipeline = Pipeline.from_documents(
            clean_documents, attacker_doc_ids=set(), marker=marker
        )
        self.documents: list[dict] = list(clean_documents)
        self._clean = _Snapshot(
            chunk_count=len(self.pipeline.index.chunks),
            document_count=len(clean_documents),
        )
        self._tickets: dict[str, Ticket] = {}
        self._seq = 0
        self._lock = threading.Lock()

    # --- reporting -------------------------------------------------------

    def _chunk_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for c in self.pipeline.index.chunks:
            counts[c.document_id] = counts.get(c.document_id, 0) + 1
        return counts

    def status(self) -> dict:
        return {
            "ready": True,
            "documents": len(self.documents),
            "chunks": len(self.pipeline.index.chunks),
            "attacker_documents": sorted(self.pipeline.attacker_doc_ids),
            "clean_documents": self._clean.document_count,
            "marker": self.marker,
            "provider": provider_label(),
            "open_tickets": sum(1 for t in self._tickets.values() if t.status == "open"),
        }

    def corpus(self) -> dict:
        counts = self._chunk_counts()
        return {
            "documents": [
                {
                    "document_id": d["document_id"],
                    "title": d.get("title", ""),
                    "source_type": d.get("source_type", ""),
                    "membership": "attacker"
                    if d["document_id"] in self.pipeline.attacker_doc_ids
                    else "clean",
                    "chunks": counts.get(d["document_id"], 0),
                }
                for d in self.documents
            ],
            "total": len(self.documents),
            "attacker": len(self.pipeline.attacker_doc_ids),
        }

    def attack_payloads(self) -> list[dict]:
        """The frozen attacker tickets, offered to the UI as prefill text so the
        demonstrator never has to type an injection on stage."""
        return [
            {
                "document_id": d["document_id"],
                "subject": f"Account recovery help ({d['document_id']})",
                "employee_description": d.get("employee_description", ""),
                "technician_resolution": d.get("technician_resolution", ""),
            }
            for d in load_documents(ATTACK_CORPUS)
        ]

    def tickets(self) -> list[dict]:
        return [asdict(t) for t in self._tickets.values()]

    # --- lifecycle -------------------------------------------------------

    def submit_ticket(
        self,
        subject: str,
        description: str,
        submitted_by: str = "employee",
        membership: str = "clean",
    ) -> Ticket:
        if not description.strip():
            raise ValueError("a ticket needs a description")
        if membership not in {"clean", "attacker"}:
            raise ValueError(f"unknown membership '{membership}'")
        with self._lock:
            self._seq += 1
            ticket_id = f"W{self._seq:02d}"
            ticket = Ticket(
                ticket_id=ticket_id,
                subject=subject.strip() or f"Ticket {ticket_id}",
                submitted_by=submitted_by,
                membership=membership,
                employee_description=description.strip(),
            )
            self._tickets[ticket_id] = ticket
            return ticket

    def resolve_ticket(self, ticket_id: str, resolution: str) -> dict:
        """Resolve a ticket and publish it into the live corpus.

        Resolution is the only path into the index: an open ticket is never
        searchable. This mirrors the documented admission rule.
        """
        if not resolution.strip():
            raise ValueError("a resolution needs text")
        with self._lock:
            ticket = self._tickets.get(ticket_id)
            if ticket is None:
                raise KeyError(ticket_id)
            if ticket.status == "resolved":
                raise ValueError(f"{ticket_id} is already resolved")

            body = compose_ticket_body(ticket.employee_description, resolution)
            document = {
                "schema_version": 1,
                "document_id": ticket.ticket_id,
                "source_type": "resolved_ticket",
                "membership": ticket.membership,
                "topic": "recovery",
                "title": ticket.subject,
                "body": body,
                "employee_description": ticket.employee_description,
                "technician_resolution": resolution.strip(),
                "source_ref": f"workflow/tickets/{ticket.ticket_id}",
                "content_hash": content_hash(body),
            }
            added = self.pipeline.add_document(
                document, attacker=(ticket.membership == "attacker")
            )
            self.documents.append(document)

            ticket.status = "resolved"
            ticket.technician_resolution = resolution.strip()
            ticket.document_id = document["document_id"]
            ticket.chunks_added = added

            return {
                "ticket": asdict(ticket),
                "document": {k: document[k] for k in ("document_id", "title", "membership")},
                "chunks_added": added,
                "corpus": self.status(),
            }

    def reset(self) -> dict:
        """Drop everything ingested at runtime and restore the clean corpus."""
        with self._lock:
            self.pipeline.index.truncate(self._clean.chunk_count)
            del self.documents[self._clean.document_count :]
            self.pipeline.attacker_doc_ids.clear()
            self._tickets.clear()
            self._seq = 0
            return self.status()

    # --- answering -------------------------------------------------------

    def ask(self, question: str, defense: str = "off") -> dict:
        if not question.strip():
            raise ValueError("a question needs text")
        if defense not in DEFENSES:
            raise ValueError(f"unknown defense '{defense}'; use one of: {sorted(DEFENSES)}")

        if defense == "off":
            condition = "attacked" if self.pipeline.attacker_doc_ids else "clean"
            strategy = None
        else:
            condition = "defended"
            strategy = defense

        with self._lock:
            trial = self.pipeline.answer(
                "ui", question.strip(), condition,
                spotlighting_strategy=strategy, include_prompt=True,
            )
            fallback_reason = None
            if trial.error:
                # Visible, never silent: retry once on the offline provider so the
                # demo survives a rate limit, and report exactly what failed.
                previous = os.environ.get("INJECTRAG_PROVIDER")
                os.environ["INJECTRAG_PROVIDER"] = "fake"
                try:
                    fallback_reason = trial.error
                    trial = self.pipeline.answer(
                        "ui", question.strip(), condition,
                        spotlighting_strategy=strategy, include_prompt=True,
                    )
                finally:
                    if previous is None:
                        os.environ.pop("INJECTRAG_PROVIDER", None)
                    else:
                        os.environ["INJECTRAG_PROVIDER"] = previous

            titles = {d["document_id"]: d.get("title", "") for d in self.documents}
            sources = [
                {
                    **h,
                    "title": titles.get(h["document_id"], ""),
                    "membership": "attacker"
                    if h["document_id"] in self.pipeline.attacker_doc_ids
                    else "clean",
                }
                for h in trial.hits
            ]

            return {
                "question": trial.question,
                "answer": trial.answer,
                "defense": defense,
                "condition": trial.condition,
                "spotlighting_strategy": trial.spotlighting_strategy,
                "sources": sources,
                "attacker_in_topk": trial.attacker_in_topk,
                "attacker_in_context": trial.attacker_in_context,
                "marker_present": trial.marker_present,
                "marker": self.marker,
                "provider": trial.provider,
                "model": trial.model,
                "finish_reason": trial.finish_reason,
                "error": trial.error,
                "fallback_reason": fallback_reason,
                "system_prompt": trial.system_prompt,
                "user_message": trial.user_message,
                "corpus": self.status(),
            }


def provider_label() -> str:
    provider = os.environ.get("INJECTRAG_PROVIDER", "auto").strip().lower()
    if provider == "groq" or (provider == "auto" and os.environ.get("GROQ_API_KEY")):
        return f"groq ({os.environ.get('INJECTRAG_GROQ_MODEL', 'openai/gpt-oss-20b')})"
    if provider == "openai" or (provider == "auto" and os.environ.get("OPENAI_API_KEY")):
        return f"openai ({os.environ.get('INJECTRAG_OPENAI_MODEL', 'gpt-oss-20b')})"
    if provider == "fake":
        return "fake (offline)"
    if provider == "gemini" or (
        provider == "auto"
        and (os.environ.get("INJECTRAG_GEMINI_KEYS") or os.environ.get("GEMINI_API_KEY"))
    ):
        return f"gemini ({os.environ.get('INJECTRAG_GEMINI_MODEL', 'gemini-3.8-flash')})"
    return "fake (no API key set)"


def build_service() -> DemoService:
    """Build the service from the clean corpus on disk. Attacker documents are
    NOT loaded -- they enter only through the ticket workflow."""
    path = pathlib.Path(CLEAN_CORPUS)
    if not path.exists():
        raise FileNotFoundError(
            f"{CLEAN_CORPUS} not found; run tools/seed_clean_corpus.py first"
        )
    return DemoService(load_documents(CLEAN_CORPUS))
