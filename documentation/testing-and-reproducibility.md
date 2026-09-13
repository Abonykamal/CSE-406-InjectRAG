# Testing and reproducibility

No application tests exist yet. This document defines meaningful validation for future tasks; documentation changes receive link and consistency checks only.

For D09, test a follow-up that requires prior context, fresh history after “New question,” interleaved thread isolation, ordered turns under the agreed request policy, retry/failure handling without duplicate history, and context-budget overflow. Record exact included history for reproduction. Independent baseline trials start fresh; scripted multi-turn checks are reported separately.

| Layer | Required evidence |
|---|---|
| Ingestion/contracts | Reject missing/duplicate IDs and empty/invalid content; preserve bodies; stable normalization and hashes |
| Chunking | Boundary/overlap/Unicode and long-input fixtures; valid offsets; stable IDs; no silent loss outside declared normalization |
| Index/retrieval | Tiny known-vector ranking oracle, tie handling, top-k larger than corpus, empty corpus, reload parity, mismatch rejection |
| Context | Exact final message snapshot, budget boundaries, dropped-chunk trace, correct role separation, no observer metadata leakage |
| Generation | Fake-adapter tests for timeouts, bounded retries, provider errors and truncation; one real-provider smoke run when approved |
| API/UI | Request validation, readiness, bounded concurrency/errors, browser loading/retry states, keyboard operation, source rendering, and one real browser-to-RAG answer |
| End-to-end | Synthetic fixture ingested through public entry point; reloaded snapshot produces an inspectable answer and complete trace |
| Clean baseline | Frozen query set, retrieval relevance and answer scoring, unsupported cases, repeatability pilot, explicit failure counts |

Do not require live paid/model-download calls in the default test suite. Use fixtures and deterministic adapters for routine checks; mark real-model tests separately and document their resource prerequisites. Mock success does not establish real-model answer quality.

## Reproduction bundle

Each recorded baseline links the code revision (and any dirty diff fingerprint), dependency lock, resolved configuration, prompt text/hash, corpus and query manifest hashes, chunker/tokenizer revisions, embedding model and dimension, index backend/version, generator identity/settings, retry policy, run timestamps, and trial traces. Record seeds and device information where relevant, and unavailable metadata explicitly.

Index manifests prevent reuse of embeddings built with incompatible settings. Never use a cache key based only on a model display name. A fresh-run guide must explain model provisioning, environment variables, index build, query execution, baseline scoring, expected output files, and troubleshooting. Write actual commands only after they exist and have been exercised.

## Acceptance discipline

Run checks appropriate to changed behavior and required project checks. For each plan task, record commands, outcome, and artifact paths in project status or its linked run record. If a check cannot run, state the dependency and keep the associated acceptance criterion incomplete. Rebuild/smoke checks precede the M4 handoff; performance and accuracy targets come from D06.
