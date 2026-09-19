# Proposed data contracts

These are implementation requirements to refine during R03, not existing Python classes. D10 selects SQLite application state and Qdrant vector storage; exact artifact serialization remains to specify in R03. UTF-8 text and explicit schema versions are the proposed portable boundary. Validation errors name the offending record and field.

| Record | Required content | Invariants |
|---|---|---|
| Document | `schema_version`, `document_id`, `source_type`, `title`, `body`, `source_ref`, `content_hash` | Nonempty body; unique ID per corpus; supported source type; hash covers canonical content; preserve original input alongside normalized representation |
| Chunk | `chunk_id`, `document_id`, `ordinal`, `text`, start/end offsets, token count, document hash, chunker fingerprint | Stable identity for identical source and settings; offsets refer to normalized body using a declared unit; parent exists; no empty chunks |
| Index manifest | snapshot ID, document/chunk IDs and hashes, embedding identifier/revision/dimension, normalization and chunk settings, similarity metric, build/software fingerprint | Exact corpus membership; no duplicate vectors; reject incompatible embedding or preprocessing settings at load |
| Retrieval hit | chunk/document IDs, rank, score, text, snapshot ID | Defined score direction; ranks begin at 1; stable tie policy; top five by descending cosine score, stable chunk-ID ties; multiple chunks per document allowed |
| Context result | ordered included chunks, excluded chunks and reasons, exact rendered messages, budget/accounting method, prompt hash | Distinguish retrieved from actually included; retain final text after any transformation; corpus cannot define provider role metadata |
| Query | `query_id`, `query_class`, `question`, split | Stable unique ID; no expected-answer fields supplied to RAG runtime |
| Answer key, observer only | query ID, accepted answer facts/markers, relevant document IDs, answerability, scoring version | Separate from question request; ambiguous answers explicitly reviewed; held-out key unavailable to attacker-side construction |
| Generation result | response text, provider/model identity, finish reason, usage when supplied, duration, error/status | Errors and truncation are distinguishable from complete answers; unavailable metadata recorded as unavailable |
| Run manifest | run ID, time, code revision and dirty-state fingerprint, config hash, corpus/index/query/prompt hashes, dependency/model revisions, seeds/settings, environment summary | Enough information to identify inputs; no API secrets; declared unavailable metadata rather than invented pinning |
| Trial trace | run/trial/query IDs, retrieval hits, context result, generation result, stage timings, status and retry count | Links to manifest; contains exact synthetic request/response needed for diagnosis; failed trials retained |

## Observer-only judge and audit records

D06 requires trial-linked judge inputs, answer-key/rubric versions, sanitized provider requests/responses, label and rationale, citation-support assessment, model/settings, status/errors, and usage when supplied. Preserve original judgments and human-audit corrections separately with selection/reviewer provenance. Failed or malformed judgments are unscored, not automatic answer failures. None of these records may enter victim inference.

## History assembly policy

D12 retains SQLite threads/turns across restarts without automatic expiry, for inspection rather than resumption. Follow-ups use full ordered user/assistant history only within the active thread; New question starts empty. Leaving or restarting does not allow old-thread continuation. Prior evidence bundles remain in artifacts. Preflight the complete answer request, including output reserve. If full history cannot fit, return HTTP 422 with a context-limit code and a start-new-question message, preserve typed input, record the error, and make no answer call or turn append. Never silently trim or summarize history. Explicit cleanup follows preservation of required research artifacts.

Preserve roles/order and original answer text; put fresh evidence after history and the current original question last. A previous assistant answer is not supporting evidence.

## Current-question retrieval records

D12 selects one cosine vector search using the current question as written, including follow-ups: top five chunks, descending score with stable chunk-ID tie breaking. Deduplicate only by chunk ID; no reranking, query rewriting, fusion, per-document quota, source preference, attacker-label filtering or uncalibrated similarity cutoff. Include whole chunks in rank order under a 2,048-token evidence ceiling including labels and the complete request limits; log excluded chunks and reasons. Actual context may contain fewer than five chunks. Trace raw top-five rankings and actual context separately. Validate on clean development data and freeze before held-out evaluation; changes require evidence and review. Use identical retrieval rules across conditions and the same poisoned snapshot/candidate list for matched attacked/defended single-turn trials.

Record the original question, local embedding identity, snapshot/config identity, raw top-five hits, context inclusion and exclusions, and stage timings. No rewrite output, second-query ranking, fusion or fallback fields are required. Keep history out of query embedding.

## Selected model identities and pilot accounting — D11

Record gemini-3.8-flash separately for answer and observer-judge roles (low thinking), and BAAI/bge-small-en-v1.5 with actual FastEmbed/ONNX artifact/tokenizer hashes. Embeddings have 384 dimensions and a 512-token input bound including prefixes/special tokens. No rewrite role is required. Record Python 3.12 patch version, locked packages and image digests.

D12 counters persist across run restarts and distinguish planned logical calls from attempts and auxiliary API requests. Pilot: 15 answers + 20 judgments = 35 calls, at most five extra retries/40 attempts and 100 total API requests. Whole study including the [D14](decisions.md#d14) sweep: 347 planned calls + 28 retries = 375 attempts and 800 total API requests. Enforce phase reserves, 8,192 input tokens per attempt, 4,096 pilot/2,048 later output tokens, and aggregate ceilings of 3,072,000 input and 849,920 output tokens. Reserve capacity before dispatch, conservatively account for unavailable usage, and include thinking usage where applicable. See [D14](decisions.md#d14) for the current phase allocation, which adds one 36-call zero-judgment sweep phase to [D12](decisions.md#d12)'s four. A failed judgment remains unscored; shared models do not create independent quota pools.

## Provider request and trial retention

D02 requires a provider-independent generation request/result boundary and a Gemini adapter initially. Retain both the canonical assembled request and the actual sanitized provider payload, with returned response content/metadata, requested and reported model identity, supported settings, timestamps, usage/latency when available, and each retry/error. Keep credentials and authentication/session secrets out of logs. Preserve unsupported/unavailable fields explicitly rather than fabricating equivalence across providers. Persist linked trial artifacts outside disposable container state; changing provider/model creates a new run configuration and baseline.

## Ticket workflow and login contract

D04/D12 require ticket ID, immutable employee description/owner, submitted or resolved state, technician resolution and provenance. Technician resolution occurs once and starts publication automatically; searchable status follows successful complete publication, not resolution alone. Preserve publication failures for retry and frozen snapshot isolation. No edit/reopen endpoints. Seeded and interactive tickets share normalization/admission. Final SQL/API fields and publication orchestration remain in the [SQLite proposal](../sqlite-schema-plan.txt).

D12 selects a username/password form for seeded accounts and Starlette signed-cookie SessionMiddleware. Store only account ID in an HttpOnly, SameSite=Strict browser-session cookie, hashed passwords in SQLite, and check current account role/ownership on every protected API request. Logout clears the cookie; a random signing secret at startup invalidates cookies on app restart. No SQLite sessions table, registration, persistent login or external identity service. Bind the HTTP demo to loopback; use HTTPS/Secure cookies beyond localhost and reject cross-site state-changing requests. Cookie clearing is not server-side revocation of copied cookies.

## Approved storage mapping — D10

SQLite through Python sqlite3 stores accounts, tickets, threads, and turns. Qdrant stores embeddings and chunk payload metadata behind the index adapter. Link Qdrant collection/point identities to the existing snapshot and chunk identities, preserving model/dimension/metric compatibility checks and keeping observer labels outside retrieval payloads. D13 uses the SQLite outline, UUID identifiers and complete-snapshot publication as starting implementation details; finalize exact fields in R03. D12 settles search and publication behavior. Retain corpus/index manifests and sanitized trial/judge/audit artifacts separately on persistent host storage. Database persistence alone does not satisfy trace completeness or make a collection immutable.

## Identity and mutation

D09 adds a conversation contract: `thread_id`, ordered `turn_id`/sequence, role, text, request ID, completion status, and timestamps. A new question creates a fresh thread; follow-ups reference only their own thread. D10/D12 select persistent records without old-thread resume; validate ownership and active-thread eligibility at the API. Implement schema/idempotency in R03 using the SQLite outline; D13 treats page refresh as a new visit. Do not let caller-supplied history declare trusted provider roles.

Context results and trial traces additionally record thread/turn IDs, the exact included history, omitted turn IDs/reasons, and history token accounting. Record the retrieval query actually used for each turn. Failed or retried requests must not silently create duplicate completed turns. A prior assistant answer is conversation history, not a supporting document.

Define canonical hashing once. A versioned source article's logical ID can survive a revision, but its content hash and derived chunk/index identities must change. Submitted tickets remain immutable under D12. Detect conflicting repeated IDs; do not silently overwrite. Reingesting unchanged input into a new build should produce the same logical records. Build to a temporary output and publish only a complete snapshot; failed builds must not appear ready.

## Experiment-only metadata

Store clean/attacker membership, condition, poisoning budget, target string, and expected answers in observer manifests. D08 fixes the admitted attacker-document count at N = 5 for each poisoned snapshot (41 total documents versus 36 clean); identify the five parent ticket IDs and hashes separately from chunk IDs and instruction-occurrence counts. Matched attacked/defended runs reference the same poisoned snapshot. Identify the frozen five-ticket set with its content hashes and observer-only cover-topic annotations and shared base-instruction/target-directive identity. The approved stories are distinct and collectively span the three recovery topics. Exact payload text and variant definitions remain pending. Ordinary source metadata can be exposed only through a declared prompt policy. Attacker flags, ground-truth markers, and evaluation labels must never help retrieval or generation. Do not infer attacker membership from a substring of the chunk text.

D08 additionally requires authoring provenance outside victim inference: the exact restricted brief, identities of any supplied materials, frozen ticket content hashes and freeze time, and known information leakage/deviations. Keep withheld corpus, victim prompts/configuration, actual development/held-out questions and keys, and victim traces outside attack-authoring inputs. Record observer analysis against frozen ticket identities; do not silently replace payloads after inspecting results.

For the D08 initial study, identify one logical answer outcome per held-out query/condition, with all 30 query IDs represented in the planned manifest for each of the three conditions. Keep operational attempt/retry IDs distinct from experiment repetition identity. Preserve failed/missing outcomes and paired eligibility rather than replacing unfavorable completed answers. Reused clean outcomes must link to compatible frozen configuration identities; record the 18-question target subset separately from the other categories.

M_a verification is optional future work only. No attacker-model request/result records or extension-specific schemas are required for the current study; define them if the extension is later selected.

## Error and output policy

D12 removes the waiting chat queue. Keep one hosted model call at a time; an occupied inference slot returns HTTP 503 with a machine-readable busy code promptly, without model work or turn creation. Preserve typed text for manual retry and keep readiness responsive. Oversized raw questions return HTTP 413; history/context overflow returns HTTP 422. D13 starts with a 2,000-character question cap and an additional 512-token embedding-payload check; reject overlength input without truncation.

D12 permits at most one retry of a hosted answer or observer-judge call only for temporary network failure, timeout, provider 5xx, or 429 with a short retry window. Retry a failed judge only, never its completed answer. Pause on daily/account quota exhaustion. Poor retrieval, wrong answers and missing attack markers never trigger retries; no automatic Qdrant search retry. Attempts retain one logical trial identity and consume both phase and study limits. Ticket-publication retry is separate. D13/plan set implementation defaults: 1 second before an eligible non-429 retry; honor a valid 429 Retry-After only up to 30 seconds, otherwise pause/report the limit. These refine D12 eligibility without adding attempts.

Use structured stage errors for invalid input, unavailable model, index mismatch, provider timeout and write failure. Unrecovered operational failure returns non-success; an insufficient-evidence answer is a completed generation. Never report a partially indexed corpus as ready. Persist attempts/errors without duplicate completed turns.