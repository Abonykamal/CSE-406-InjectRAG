"""The application layer: two corpora, one lock, two methods.

`HelpdeskService.ask` returns nothing but the answer string, and
`HelpdeskService.submit_case` returns nothing but the new document id. Every
piece of evidence -- ranked hits, which chunks reached the context, the exposure
flags, the marker verdict, the resolved provider -- goes to JsonlLogger instead,
because the browser is meant to look like an ordinary helpdesk. If you want to
know why an answer said what it said, read `logs/queries.jsonl`.

Two corpora are held at once. The poisoned one is built at boot exactly as
run_demo.py:build_pipelines builds it (36 clean + 5 attacker tickets); the clean
one is a prefix slice of the same index, so the second view costs no extra
embedding pass. A question is answered against whichever the request asks for,
defaulting to INJECTRAG_CORPUS. A case filed by a technician joins the *clean*
corpus and is therefore retrievable in both views.

Nothing is persistent: restart and the corpora are the 36- and 41-document
snapshots again.
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
CORPORA = {"clean", "poisoned"}

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


def validated_defense(defense: str | None) -> str:
    value = (defense or "off").strip().lower()
    if value not in DEFENSES:
        raise ValueError(f"unknown defense '{defense}'; use one of: {sorted(DEFENSES)}")
    return value


def validated_corpus(corpus: str | None) -> str:
    value = (corpus or "poisoned").strip().lower()
    if value not in CORPORA:
        raise ValueError(f"unknown corpus '{corpus}'; use one of: {sorted(CORPORA)}")
    return value


def condition_for(corpus: str, defense: str) -> str:
    """The experiment condition this request runs under.

    Declared, never inferred: nothing inspects the answer or the retrieved
    documents. It is also load-bearing rather than a label --
    `resolve_spotlighting_strategy` returns None unless the condition is
    "defended", so this string is what selects the system prompt.
    """
    if defense != "off":
        return "defended"
    return "attacked" if corpus == "poisoned" else "clean"


class HelpdeskService:
    def __init__(
        self,
        documents: list[dict],
        attacker_ids: set[str],
        logger: JsonlLogger,
        marker: str = MARKER,
        defense: str = "off",
        corpus: str = "poisoned",
    ):
        self.defense = validated_defense(defense)
        self.corpus = validated_corpus(corpus)
        self.marker = marker
        self.logger = logger
        self.documents: list[dict] = list(documents)

        # One embedding pass. `documents` arrives clean-first, so the clean
        # chunks are a prefix of the full index and the clean view is a row
        # slice of it -- switching corpus at runtime costs nothing.
        # The five frozen attacker tickets. Cases filed later are also labelled
        # attacker for exposure bookkeeping, but they belong to the clean corpus,
        # so the two sets must not be conflated.
        attacker_ids = set(attacker_ids)
        self.seeded_attacker_ids = set(attacker_ids)
        poisoned = Pipeline.from_documents(
            self.documents, attacker_doc_ids=attacker_ids, marker=marker
        )
        clean_docs = [d for d in self.documents if d["document_id"] not in attacker_ids]
        if [d["document_id"] for d in self.documents[: len(clean_docs)]] != [
            d["document_id"] for d in clean_docs
        ]:
            raise ValueError(
                "clean documents must be indexed before attacker documents; "
                "the clean corpus is built as a prefix slice of the poisoned index"
            )
        clean_chunk_count = sum(
            1 for c in poisoned.index.chunks
            if c.document_id not in attacker_ids
        )
        clean = Pipeline(
            poisoned.index.prefix_view(clean_chunk_count),
            # The same set object, so a case filed later is registered in both.
            poisoned.attacker_doc_ids,
            marker,
        )
        self.pipelines = {"clean": clean, "poisoned": poisoned}

        self._seq = 0
        self._lock = threading.Lock()

    @property
    def pipeline(self) -> Pipeline:
        """The poisoned pipeline -- the full 41-document index.

        Kept as the unqualified name because it is the whole corpus: the clean
        view is a subset of it, and the startup banner and the tests both mean
        "everything indexed" when they say `service.pipeline`.
        """
        return self.pipelines["poisoned"]

    # --- reporting (startup banner only; never reaches the browser) ------

    @property
    def document_count(self) -> int:
        return len(self.documents)

    @property
    def clean_document_count(self) -> int:
        """Documents in the clean corpus: everything except the seeded attacker
        tickets. Cases filed at runtime count here, because they join the clean
        corpus even though they are attacker-labelled for exposure bookkeeping."""
        return sum(
            1 for d in self.documents
            if d["document_id"] not in self.seeded_attacker_ids
        )

    @property
    def chunk_count(self) -> int:
        return len(self.pipeline.index.chunks)

    # --- answering -------------------------------------------------------

    def _context_chunk_ids(
        self, pipeline: Pipeline, hits: list[dict], strategy: str | None
    ) -> list[str]:
        """Which retrieved chunks actually fit under the evidence budget.

        Rebuilt from the chunk texts already in the index rather than by running
        retrieval a second time -- render_context only reads each hit's text,
        document_id and chunk_id, so this is pure string work with no second
        embedding pass and no API call.
        """
        texts = {c.chunk_id: c.text for c in pipeline.index.chunks}
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

    def ask(
        self,
        question: str,
        user: dict,
        defense: str | None = None,
        corpus: str | None = None,
        conversation_id: str | None = None,
    ) -> str:
        """Answer one question. Returns the answer text and nothing else.

        `defense` and `corpus` override the server defaults for this one
        question. The API layer only passes them when the demo controls are
        enabled, so in product mode this is configuration, not a request field.
        """
        question = (question or "").strip()
        if not question:
            raise ValueError("a question needs text")

        override = defense is not None or corpus is not None
        defense = self.defense if defense is None else validated_defense(defense)
        corpus = self.corpus if corpus is None else validated_corpus(corpus)

        query_id = f"q-{uuid4().hex[:8]}"
        condition = condition_for(corpus, defense)
        strategy = defense if defense != "off" else None
        pipeline = self.pipelines[corpus]

        with self._lock:
            trial = pipeline.answer(
                query_id, question, condition,
                top_k=TOP_K, spotlighting_strategy=strategy, include_prompt=False,
            )
            resolved = resolve_spotlighting_strategy(condition, strategy)
            context_chunk_ids = self._context_chunk_ids(pipeline, trial.hits, resolved)

            self.logger.log_query({
                "query_id": query_id,
                "conversation_id": conversation_id or None,
                "user_id": user.get("user_id"),
                "username": user.get("username"),
                "display": user.get("display"),
                "question": question,
                "condition": trial.condition,
                "corpus": corpus,
                "defense": defense,
                "demo_override": override,
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
            # A filed case joins the CLEAN corpus, and the poisoned corpus is the
            # clean one plus the five frozen tickets -- so it is indexed into both
            # and is retrievable whichever view the employee is talking to.
            #
            # `attacker=True` is an operator label for exposure bookkeeping, not an
            # inference: in this build the technician is the adversary, so anything
            # they file is attacker-authored by construction. add_document still
            # never inspects the body to decide membership. Both pipelines share
            # one attacker-id set, so labelling happens once.
            added = self.pipelines["clean"].add_document(document, attacker=True)
            self.pipelines["poisoned"].add_document(document, attacker=True)
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
                "clean_documents_after": self.clean_document_count,
            })
            return document_id


def resolved_provider_model() -> tuple[str, str]:
    """The provider and model this process will generate with.

    Mirrors generation._selected_provider, including its auto-detection order,
    so the startup banner and the name shown to the employee describe the same
    call the pipeline will actually make. An empty model means the provider has
    no model id to speak of.
    """
    provider = os.environ.get("INJECTRAG_PROVIDER", "auto").strip().lower()
    has_gemini = bool(os.environ.get("INJECTRAG_GEMINI_KEYS") or os.environ.get("GEMINI_API_KEY"))
    if provider == "auto":
        if os.environ.get("GROQ_API_KEY"):
            provider = "groq"
        elif os.environ.get("OPENAI_API_KEY"):
            provider = "openai"
        elif has_gemini:
            provider = "gemini"
        else:
            provider = "fake"

    if provider == "groq":
        return provider, os.environ.get("INJECTRAG_GROQ_MODEL", "openai/gpt-oss-20b")
    if provider == "openai":
        return provider, os.environ.get("INJECTRAG_OPENAI_MODEL", "gpt-oss-20b")
    if provider == "ollama":
        return provider, os.environ.get("INJECTRAG_OLLAMA_MODEL", "llama3.1:8b")
    if provider == "gemini":
        return provider, os.environ.get("INJECTRAG_GEMINI_MODEL", "gemini-3.8-flash")
    return "fake", ""


def provider_label() -> str:
    provider, model = resolved_provider_model()
    if provider == "fake":
        return "fake (offline)" if os.environ.get(
            "INJECTRAG_PROVIDER", "auto"
        ).strip().lower() == "fake" else "fake (no API key set)"
    if provider == "ollama":
        return f"ollama ({model}, local)"
    return f"{provider} ({model})"


def resolved_model_name() -> str:
    """The short model name shown to the employee, e.g. `gpt-oss-20b`.

    The full id (`openai/gpt-oss-20b`) still goes to the logs; the vendor prefix
    is plumbing and does not belong on a helpdesk screen.
    """
    _, model = resolved_provider_model()
    return model.rsplit("/", 1)[-1] if model else "offline demo"


def resolved_defense() -> str:
    defense = os.environ.get("INJECTRAG_DEFENSE", "off").strip().lower() or "off"
    if defense not in DEFENSES:
        raise ValueError(
            f"INJECTRAG_DEFENSE='{defense}' is not valid; use one of: {sorted(DEFENSES)}"
        )
    return defense


def resolved_corpus() -> str:
    corpus = os.environ.get("INJECTRAG_CORPUS", "poisoned").strip().lower() or "poisoned"
    if corpus not in CORPORA:
        raise ValueError(
            f"INJECTRAG_CORPUS='{corpus}' is not valid; use one of: {sorted(CORPORA)}"
        )
    return corpus


def demo_controls_enabled() -> bool:
    """Whether the browser may choose the corpus and the defense.

    On by default: this build exists to be demonstrated. Set
    INJECTRAG_DEMO_CONTROLS=0 to hide the controls and pin every request to the
    .env configuration -- the product surface, and what a scripted evaluation
    run should use.
    """
    return os.environ.get("INJECTRAG_DEMO_CONTROLS", "1").strip().lower() not in {
        "0", "false", "no", "off", ""
    }


def build_service(
    log_dir: str | None = None,
    defense: str | None = None,
    corpus: str | None = None,
) -> HelpdeskService:
    """Build the service exactly as run_demo.py:build_pipelines does.

    41 documents: the 36 clean ones plus the 5 frozen attacker tickets, whose ids
    become the attacker set. The clean corpus is the same index without those
    five. Unlike the documented snapshot runner, both are then allowed to grow as
    cases are filed.
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
        corpus=corpus if corpus is not None else resolved_corpus(),
    )
