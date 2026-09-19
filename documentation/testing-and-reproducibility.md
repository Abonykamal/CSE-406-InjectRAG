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
| Generation | Fake-adapter tests for timeouts, bounded retries, provider errors and truncation; live integration evidence from the first budgeted R16 pilot answer |
| API/UI | Request validation, readiness, bounded concurrency/errors, browser loading/retry states, keyboard operation, source rendering, and one real browser-to-RAG answer |
| End-to-end | Synthetic fixture ingested through public entry point; reloaded snapshot produces an inspectable answer and complete trace |
| Clean baseline | Frozen query set, retrieval relevance and answer scoring, unsupported cases, repeatability pilot, explicit failure counts |

Do not require live paid/model-download calls in the default test suite. Use fixtures and deterministic adapters for routine checks; mark real-model tests separately and document their resource prerequisites. Mock success does not establish real-model answer quality.

Verify the Gemini adapter with captured sanitized request/response fixtures and a fake provider; unsupported settings and provider errors must remain explicit. The bounded live pilot uses local embeddings and Gemini generation in the Docker-delivered system. Check artifact persistence across container recreation without persisting credentials. A replacement provider requires a new clean baseline; free-tier availability is not a reproducibility guarantee.

For D12 retrieval, verify a single current-question search for first turns and follow-ups, cosine descending score, stable chunk-ID ties, top five, chunk-ID-only deduplication and no source/diversity preference. Verify there are no rewrite/reranker calls or Qdrant query retries. Check whole-chunk context inclusion under 2,048 evidence tokens including labels, with exclusions logged. Clean development fixtures cover vague references, corrections, topic shifts and misleading prior answers; expose limitations without modifying retrieval against attack outcomes.

Validate D05 full-history assembly: original role/order preservation, current question last after fresh evidence, no automatic history summarization/trimming, and no replay of old retrieval bundles. Include corrections, erroneous prior answers, and distracting earlier topics in conversational quality checks. Check complete answer-request accounting, including model context limit and output reserve; reject full-history overflow explicitly.

## Approved stack verification — D10

When implementation is authorized, verify uv locked installation, pinned application/Qdrant image identities, and the two-service Compose startup/readiness behavior. Test Qdrant with known-vector fixtures, reload parity, incompatible-manifest rejection, and frozen-collection isolation; its persistence does not enforce study immutability. Verify SQLite-backed ownership/thread isolation and transaction behavior. Recreate containers and confirm application state, vectors, model cache, and run/audit artifacts survive in their separate host mounts. Keep model-call secrets out of artifacts. Confirm slow generation/local embedding work does not block readiness, and browser loading/error/complete-answer states work through the FastAPI API. These checks have not been run.

## Approved model/pilot verification — D11

Verify the selected CPU BGE-small/FastEmbed/ONNX path, 384-vector dimensions and 512-token input handling without silent truncation. Record actual model/tokenizer artifact hashes, Python 3.12 patch version, locked package versions and image digests. Confirm low thinking for gemini-3.8-flash answer/judge requests with no required rewrite requests. Capture actual role mapping and supported settings using google-genai.

Test cumulative phase/study counters across run restarts. Pilot: 35 planned calls, five extra retries, 40 attempts, 100 total API requests. Whole study including the D14 sweep: 347 calls plus 28 retries, 375 attempts, 800 total API requests, 3,072,000 input and 849,920 output tokens. Check D12 phase reserves; one retry only for eligible transient answer/judge failures, with a judge failure never regenerating the answer. Verify 8,192 input tokens, 4,096 pilot/2,048 later output caps, 90-second attempt timeout and explicit quota/budget stops. Include thinking usage and conservative reservations when usage is unavailable. Measure 4/1 GiB application/Qdrant pilot memory ceilings and 30-second median answer latency excluding quota waits. These are future checks, not passed tests; actual account quotas take precedence.

## Reproduction bundle

Each recorded baseline links the code revision (and any dirty diff fingerprint), dependency lock, resolved configuration, prompt text/hash, corpus and query manifest hashes, chunker/tokenizer revisions, embedding model and dimension, index backend/version, generator identity/settings, retry policy, run timestamps, and trial traces. Record seeds and device information where relevant, and unavailable metadata explicitly.

Index manifests prevent reuse of embeddings built with incompatible settings. Never use a cache key based only on a model display name. A fresh-run guide must explain model provisioning, environment variables, index build, query execution, baseline scoring, expected output files, and troubleshooting. Write actual commands only after they exist and have been exercised.

## Later fixed-budget comparison

D08 selects N = 5 for the three main conditions. Verify the main poisoned snapshot preserves all 36 clean documents unchanged and adds exactly five admitted attacker ticket documents. Match attacked/defended runs to the same poisoned snapshot. For the [D14](decisions.md#d14) R22 sweep, additionally verify that Γ₁ and Γ₃ are literal subsets of the frozen Γ₅ by parent content hash, that their snapshots contain 37 and 39 documents against the same unchanged 36 clean documents, that the hash-ascending subset ordering was recorded in the R18 freeze record before any sweep run, and that no sweep run triggers a judge call. Reuse the R20 attacked outcomes as the N = 5 point instead of regenerating them. Keep parent-document counts separate from chunk and instruction-occurrence counts. Verify the frozen set contains five distinct support stories collectively spanning all three recovery topics, sharing the same base instruction and target directive; retain the exact document hashes. Check authoring provenance identifies the restricted brief and supplied materials, freezes tickets before victim testing, and records known leakage/deviations. Actual development/held-out questions and keys, clean corpus contents, victim prompts/configuration, and victim feedback are withheld from construction; no surrogate is selected. Observer results must not guide changes to the frozen attack. These checks document procedure, not proof of same-team blindness. For the approved initial repetition policy, verify all 30 held-out query IDs are planned once per condition in fresh threads, with logical outcomes distinct from operational attempts/retries. Preserve failures/missing pairs, verify configuration compatibility for reused clean outcomes, and report the 18-question target subset separately. Do not rerun completed answers based on attack success. Exact payload details and variants remain pending; these are future checks, not existing test results.

The optional M_a extension and other [things to try if time permits](optional-extensions.md) add no required tests or acceptance gates to the current study.

## Acceptance discipline

Run checks appropriate to changed behavior and required project checks. For each plan task, record commands, outcome, and artifact paths in project status or its linked run record. If a check cannot run, state the dependency and keep the associated acceptance criterion incomplete. Local rebuild/replay checks and retained pilot evidence precede the M4 handoff; performance and accuracy targets come from D06.

## Application-policy acceptance checks — D12

Verify signed-cookie tamper rejection, hashed passwords, per-request SQLite roles/ownership, cross-site mutation rejection, logout cookie clearing and startup-secret invalidation. No SQLite sessions table is required. Verify immutable ticket description and one-way resolution, automatic publication, visible publication failure/retry and frozen-snapshot isolation.

Persist history across restart but reject old-thread continuation after leaving/restarting; New question is empty. Verify HTTP 503 busy without a waiting queue, HTTP 413 raw-question overflow and HTTP 422 context overflow. All preserve input and avoid model work/turn append; readiness remains responsive. Keep ordinary transient retries within the accepted phase/study limits and confirm no duplicate turns. D13/plan set refresh as a new visit and retry waits at 1 second for eligible non-429 errors, or valid Retry-After at most 30 seconds for 429; test these starting settings.

## Avoid duplicate hosted validation

R11/R13/R14 use fake provider outcomes and real local retrieval until the first planned R16 pilot answer supplies shared hosted integration evidence. Rebuild/reload indexes and replay retained responses for reproduction; no additional smoke, demonstration or repeated baseline calls are allocated. A changed configuration requiring new hosted outcomes needs a revised budget.
