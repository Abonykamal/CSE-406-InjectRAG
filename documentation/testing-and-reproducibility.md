# Testing and reproducibility

No application tests exist yet. This document defines meaningful validation for future tasks; documentation changes receive link and consistency checks only.

For D09, test a follow-up that requires prior context, fresh history after “New question,” interleaved thread isolation, ordered turns under the agreed request policy, retry/failure handling without duplicate history, and context-budget overflow. Record exact included history for reproduction. Independent baseline trials start fresh; scripted multi-turn checks are reported separately.

| Layer | Required evidence |
|---|---|
| Ingestion/contracts | Reject missing/duplicate IDs and empty/invalid content; preserve bodies; stable normalization and hashes |
| Ticket workflow | Submit → resolve → admit → publish → retrieve; unresolved exclusion; API-enforced local-account roles, ownership, unauthenticated rejection, and denied employee resolution; description preservation; seeded/workflow equivalence; publication failure/retry and frozen-snapshot isolation |
| Chunking | Boundary/overlap/Unicode and long-input fixtures; valid offsets; stable IDs; no silent loss outside declared normalization |
| Index/retrieval | Tiny known-vector ranking oracle, tie handling, top-k larger than corpus, empty corpus, reload parity, mismatch rejection |
| Context | Exact final message snapshot, budget boundaries, dropped-chunk trace, correct role separation, no observer metadata leakage |
| Generation | Fake-adapter tests for timeouts, bounded retries, provider errors and truncation; one real-provider smoke run when approved |
| API/UI | Request validation, readiness, bounded concurrency/errors, browser loading/retry states, keyboard operation, source rendering, and one real browser-to-RAG answer |
| End-to-end | Synthetic fixture ingested through public entry point; reloaded snapshot produces an inspectable answer and complete trace |
| Clean baseline | Frozen query set, retrieval relevance and answer scoring, unsupported cases, repeatability pilot, explicit failure counts |

Do not require live paid/model-download calls in the default test suite. Use fixtures and deterministic adapters for routine checks; mark real-model tests separately and document their resource prerequisites. Mock success does not establish real-model answer quality.

Verify the Gemini adapter with captured sanitized request/response fixtures and a fake provider; unsupported settings and provider errors must remain explicit. The bounded live pilot uses local embeddings and Gemini generation in the Docker-delivered system. Check artifact persistence across container recreation without persisting credentials. A replacement provider requires a new clean baseline; free-tier availability is not a reproducibility guarantee.

For D05 original-plus-rewritten retrieval, verify both search paths, deduplication, total evidence budget, and trace linkage. Development examples must include self-contained questions, vague references, user corrections, topic shifts, and misleading prior assistant answers. Record rewrite errors separately from answer-generation errors. Verify timeout/provider-error/invalid-rewrite fallback to original-only retrieval, absent rewritten rankings, bounded retries, and preserved degraded status. Fallback answers still require grounding or clarification. Freeze rewrite model/prompt/history/fusion settings alongside the generator configuration; compare conversational quality before treating a replacement as equivalent.

Validate D05 full-history assembly: original role/order preservation, current question last after fresh evidence, no automatic history summarization/trimming, and no replay of old retrieval bundles. Include corrections, erroneous prior answers, and distracting earlier topics in conversational quality checks. Check token accounting separately for rewrite and answer models; do not assume identical limits.

## Approved stack verification — D10

When implementation is authorized, verify uv locked installation, pinned application/Qdrant image identities, and the two-service Compose startup/readiness behavior. Test Qdrant with known-vector fixtures, reload parity, incompatible-manifest rejection, and frozen-collection isolation; its persistence does not enforce study immutability. Verify SQLite-backed ownership/thread isolation and transaction behavior. Recreate containers and confirm application state, vectors, model cache, and run/audit artifacts survive in their separate host mounts. Keep model-call secrets out of artifacts. Confirm slow generation/local embedding work does not block readiness, and browser loading/error/complete-answer states work through the FastAPI API. These checks have not been run.

## Approved model/pilot verification — D11

Verify the selected CPU BGE-small/FastEmbed/ONNX path, 384-vector dimensions and 512-token input handling without silent truncation. Record actual model/tokenizer artifact hashes, Python 3.12 patch version, locked package versions and image digests. Confirm low thinking for gemini-3.8-flash answer/judge requests and minimal thinking for gemini-3.5-flash-lite rewrite requests. Capture actual role mapping and supported settings using google-genai.

Test cumulative pilot counters across retries/resumes: 40 planned inference calls, at most five additional retry attempts, one retry per failed request, and at most 100 total API calls including auxiliary calls. Verify serial model requests, 8,192-token input ceiling, 4,096/512 output caps, 90/30-second attempt timeouts and explicit truncation/overflow/fallback outcomes. Measure application/Qdrant memory against 4/1 GiB ceilings, median answer latency against 30 seconds excluding quota waits, trace completeness and readiness responsiveness. These are approved targets, not passed checks. Actual account quotas override these bounds. Preserve the existing human audit and report shared answer/judge-model limitations. No live calls or downloads are authorized yet.

## Reproduction bundle

Each recorded baseline links the code revision (and any dirty diff fingerprint), dependency lock, resolved configuration, prompt text/hash, corpus and query manifest hashes, chunker/tokenizer revisions, embedding model and dimension, index backend/version, generator identity/settings, retry policy, run timestamps, and trial traces. Record seeds and device information where relevant, and unavailable metadata explicitly.

Index manifests prevent reuse of embeddings built with incompatible settings. Never use a cache key based only on a model display name. A fresh-run guide must explain model provisioning, environment variables, index build, query execution, baseline scoring, expected output files, and troubleshooting. Write actual commands only after they exist and have been exercised.

## Later fixed-budget comparison

D08 selects N = 5 only, with no budget sweep. Verify each poisoned snapshot preserves all 36 clean documents unchanged and adds exactly five admitted attacker ticket documents. Match attacked/defended runs to the same poisoned snapshot. Keep parent-document counts separate from chunk and instruction-occurrence counts. Verify the frozen set contains five distinct support stories collectively spanning all three recovery topics, sharing the same base instruction and target directive; retain the exact document hashes. Check authoring provenance identifies the restricted brief and supplied materials, freezes tickets before victim testing, and records known leakage/deviations. Actual development/held-out questions and keys, clean corpus contents, victim prompts/configuration, and victim feedback are withheld from construction; no surrogate is selected. Observer results must not guide changes to the frozen attack. These checks document procedure, not proof of same-team blindness. For the approved initial repetition policy, verify all 30 held-out query IDs are planned once per condition in fresh threads, with logical outcomes distinct from operational attempts/retries. Preserve failures/missing pairs, verify configuration compatibility for reused clean outcomes, and report the 18-question target subset separately. Do not rerun completed answers based on attack success. Exact payload details and variants remain pending; these are future checks, not existing test results.

The optional M_a extension and other [things to try if time permits](optional-extensions.md) add no required tests or acceptance gates to the current study.

## Acceptance discipline

Run checks appropriate to changed behavior and required project checks. For each plan task, record commands, outcome, and artifact paths in project status or its linked run record. If a check cannot run, state the dependency and keep the associated acceptance criterion incomplete. Rebuild/smoke checks precede the M4 handoff; performance and accuracy targets come from D06.
