"""Deterministic paragraph-aware chunking.

Matches the D13 starting default in spirit: paragraph-aware, bounded size, with
overlap. Size is measured in words here rather than BGE tokens to keep the demo
dependency-light at chunk time; the embedding adapter separately enforces the
model's real 512-token input limit. Identical rules apply to clean and attacker
documents -- chunking never inspects membership.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

MAX_WORDS = 180
OVERLAP_WORDS = 30


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    ordinal: int
    text: str
    word_count: int


def _split_paragraphs(body: str) -> list[str]:
    parts = re.split(r"\n\s*\n", body.strip())
    return [p.strip() for p in parts if p.strip()]


def _pack(paragraphs: list[str]) -> list[str]:
    """Greedily merge adjacent paragraphs into chunks up to MAX_WORDS; split any
    single paragraph that is itself oversized."""
    units: list[str] = []
    buf: list[str] = []
    buf_words = 0

    def flush() -> None:
        nonlocal buf, buf_words
        if buf:
            units.append("\n\n".join(buf))
            buf, buf_words = [], 0

    for para in paragraphs:
        words = para.split()
        if len(words) > MAX_WORDS:
            flush()
            for i in range(0, len(words), MAX_WORDS - OVERLAP_WORDS):
                units.append(" ".join(words[i : i + MAX_WORDS]))
            continue
        if buf_words + len(words) > MAX_WORDS:
            flush()
        buf.append(para)
        buf_words += len(words)
    flush()
    return units


def chunk_document(document_id: str, body: str) -> list[Chunk]:
    units = _pack(_split_paragraphs(body))
    chunks: list[Chunk] = []
    for ordinal, text in enumerate(units):
        wc = len(text.split())
        h = hashlib.sha256(f"{document_id}:{ordinal}:{text}".encode("utf-8")).hexdigest()[:16]
        chunks.append(
            Chunk(
                chunk_id=f"{document_id}#c{ordinal}:{h}",
                document_id=document_id,
                ordinal=ordinal,
                text=text,
                word_count=wc,
            )
        )
    return chunks
