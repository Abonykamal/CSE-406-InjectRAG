"""Embedding + in-memory cosine index.

BGE-small-en-v1.5 through FastEmbed/ONNX on CPU (D11), 384-dim normalized
vectors. The index is a numpy matrix rather than Qdrant -- for a ~40-document
corpus this is exact cosine search and needs no server. The retrieval interface
(build / search) is what a Qdrant adapter would later implement unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .chunking import Chunk

_MODEL_NAME = "BAAI/bge-small-en-v1.5"
_QUERY_PREFIX = ""  # bge-small-en-v1.5 uses a query instruction only for retrieval-tuned variants; keep symmetric here
_model = None


def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding

        _model = TextEmbedding(_MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    vecs = list(_get_model().embed(texts))
    return np.array(vecs, dtype=np.float32)


def embed_query(text: str) -> np.ndarray:
    return embed_texts([_QUERY_PREFIX + text])[0]


@dataclass
class Hit:
    rank: int
    score: float
    chunk_id: str
    document_id: str
    text: str


class ChunkIndex:
    """In-memory cosine index over chunks. Vectors are L2-normalized, so a dot
    product is cosine similarity."""

    def __init__(self, model_name: str = _MODEL_NAME):
        self.model_name = model_name
        self.chunks: list[Chunk] = []
        self._matrix: np.ndarray | None = None

    def build(self, chunks: list[Chunk]) -> None:
        self.chunks = []
        self._matrix = None
        self.add(chunks)

    def add(self, chunks: list[Chunk]) -> int:
        """Embed and append chunks to the live index. Returns the number added.

        This is what lets a ticket resolved at runtime become searchable without
        rebuilding: the new rows are normalized the same way and stacked onto the
        existing matrix, so search() is unchanged.
        """
        if not chunks:
            return 0
        mat = embed_texts([c.text for c in chunks])
        # FastEmbed BGE vectors are already normalized, but enforce it.
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        mat = (mat / norms).astype(np.float32)
        self.chunks.extend(chunks)
        self._matrix = mat if self._matrix is None else np.vstack([self._matrix, mat])
        return len(chunks)

    def truncate(self, n: int) -> None:
        """Keep only the first n chunks. Used to restore a clean snapshot instantly
        instead of re-embedding the whole corpus."""
        if n < 0 or n > len(self.chunks):
            raise ValueError(f"cannot truncate to {n} of {len(self.chunks)} chunks")
        self.chunks = self.chunks[:n]
        self._matrix = None if n == 0 else self._matrix[:n]

    def search(self, question: str, top_k: int = 5) -> list[Hit]:
        if self._matrix is None:
            raise RuntimeError("index not built")
        q = embed_query(question)
        q = q / (np.linalg.norm(q) or 1.0)
        scores = self._matrix @ q
        # descending score, stable chunk-ID tie-break
        order = sorted(
            range(len(self.chunks)),
            key=lambda i: (-float(scores[i]), self.chunks[i].chunk_id),
        )
        hits: list[Hit] = []
        for rank, i in enumerate(order[:top_k], start=1):
            c = self.chunks[i]
            hits.append(
                Hit(
                    rank=rank,
                    score=round(float(scores[i]), 4),
                    chunk_id=c.chunk_id,
                    document_id=c.document_id,
                    text=c.text,
                )
            )
        return hits
