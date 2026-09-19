"""InjectRAG — minimal RAG target for demonstrating indirect prompt injection.

This is the compact demonstration build. It implements the real pipeline stages
described in documentation/architecture.md -- ingestion, chunking, embedding,
index, retrieval, context assembly, generation, trace -- without the Docker /
Qdrant / FastAPI / SQLite / login / budget-ledger production wrapper. Module
boundaries match the documented architecture so the heavier pieces can replace
individual adapters later.
"""

__version__ = "0.1.0-demo"
