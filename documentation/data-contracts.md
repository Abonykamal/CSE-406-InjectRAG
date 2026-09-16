# Proposed data contracts

These are implementation requirements to refine during R03, not existing Python classes. D10 selects SQLite application state and Qdrant vector storage; exact artifact serialization remains to specify in R03. UTF-8 text and explicit schema versions are the proposed portable boundary. Validation errors name the offending record and field.

| Record | Required content | Invariants |
|---|---|---|
| Document | `schema_version`, `document_id`, `source_type`, `title`, `body`, `source_ref`, `content_hash` | Nonempty body; unique ID per corpus; supported source type; hash covers canonical content; preserve original input alongside normalized representation |
| Chunk | `chunk_id`, `document_id`, `ordinal`, `text`, start/end offsets, token count, document hash, chunker fingerprint | Stable identity for identical source and settings; offsets refer to normalized body using a declared unit; parent exists; no empty chunks |
| Index manifest | snapshot ID, document/chunk IDs and hashes, embedding identifier/revision/dimension, normalization and chunk settings, similarity metric, build/software fingerprint | Exact corpus membership; no duplicate vectors; reject incompatible embedding or preprocessing settings at load |
| Retrieval hit | chunk/document IDs, rank, score, text, snapshot ID | Defined score direction; ranks begin at 1; stable tie policy; retain multiple chunks per document if allowed by approved policy |
| Context result | ordered included chunks, excluded chunks and reasons, exact rendered messages, budget/accounting method, prompt hash | Distinguish retrieved from actually included; retain final text after any transformation; corpus cannot define provider role metadata |
| Query | `query_id`, `query_class`, `question`, split | Stable unique ID; no expected-answer fields supplied to RAG runtime |
| Answer key, observer only | query ID, accepted answer facts/markers, relevant document IDs, answerability, scoring version | Separate from question request; ambiguous answers explicitly reviewed; held-out key unavailable to attacker-side construction |
| Generation result | response text, provider/model identity, finish reason, usage when supplied, duration, error/status | Errors and truncation are distinguishable from complete answers; unavailable metadata recorded as unavailable |
| Run manifest | run ID, time, code revision and dirty-state fingerprint, config hash, corpus/index/query/prompt hashes, dependency/model revisions, seeds/settings, environment summary | Enough information to identify inputs; no API secrets; declared unavailable metadata rather than invented pinning |
| Trial trace | run/trial/query IDs, retrieval hits, context result, generation result, stage timings, status and retry count | Links to manifest; contains exact synthetic request/response needed for diagnosis; failed trials retained |

## Observer-only judge and audit records

D06 requires trial-linked judge inputs, answer-key/rubric versions, sanitized provider requests/responses, label and rationale, citation-support assessment, model/settings, status/errors, and usage when supplied. Preserve original judgments and human-audit corrections separately with selection/reviewer provenance. Failed or malformed judgments are unscored, not automatic answer failures. None of these records may enter victim inference.

## History assembly policy

D05 approves full same-thread user/assistant history by default, preserving roles and order without routine trimming or summarization. The generation input ends with fresh evidence followed by the current original question. Historical evidence bundles remain in artifacts, not replayed conversation. Preserve original answer text and trace exact role/order mapping. Count inputs for each selected model; SQLite storage is selected by D10; overflow handling and retention/resume remain pending.

## Follow-up rewrite and retrieval records

D05 requires a rewrite-stage record linked to thread/turn/trial identity: original question, exact selected history, canonical and sanitized provider requests, returned rewrite output, validated search text, provider/model/settings, usage/latency when available, and attempts/errors. Keep rewrite and answer-generation configurations distinct. Retain original-query and rewritten-query rankings, snapshot identity, fusion configuration, deduplicated selected chunks, and final context inclusion. Treat history and model-generated rewrites as untrusted content, not new application instructions. Exact rewrite validation remains pending. Record rewrite-stage status, fallback reason, and effective retrieval mode. On rewrite failure, use original-question retrieval and represent rewritten rankings as absent, not successful empty results.

## Selected model identities and pilot accounting — D11

Record gemini-3.8-flash separately for answer and observer-judge roles (low thinking), gemini-3.5-flash-lite for rewriting (minimal thinking), and BAAI/bge-small-en-v1.5 with the actual FastEmbed/ONNX artifact/tokenizer revisions and hashes. Embeddings have 384 dimensions; validate the 512-token input bound including prefixes/special tokens. Record Python 3.12 patch version, exact locked packages and image digests at setup.

D11 pilot counters track planned role calls, per-request attempts, cumulative inference attempts (at most 45, including at most five retries), and all API requests (at most 100, including metadata/token counting). Counters persist across resumes. Log exact token accounting and thinking/output-cap behavior, timeout/overlength/truncation status, quota waits, and unavailable usage explicitly. Preserve 40 planned inference requests: 15 answers, 20 judgments including five fabricated cases, and five rewrite fixtures. A failed judgment remains unscored. Model and quota configuration must not conflate separate roles with independent quota pools. See [D11](decisions.md#d11) for all limits; this is a design contract, not an existing implementation.

## Provider request and trial retention

D02 requires a provider-independent generation request/result boundary and a Gemini adapter initially. Retain both the canonical assembled request and the actual sanitized provider payload, with returned response content/metadata, requested and reported model identity, supported settings, timestamps, usage/latency when available, and each retry/error. Keep credentials and authentication/session secrets out of logs. Preserve unsupported/unavailable fields explicitly rather than fabricating equivalence across providers. Persist linked trial artifacts outside disposable container state; changing provider/model creates a new run configuration and baseline.

## Ticket workflow contract — scope accepted, details pending

D04 requires ticket identity, employee description, lifecycle status, technician resolution, and provenance to remain distinguishable. Unresolved tickets are not corpus-eligible. Seeded local accounts and API-enforced employee/technician roles are approved. Define authenticated actor and ticket-owner identities, session mechanism, SQLite schemas/transactions, transition/edit/reopen rules, and index publication tracking in R03/R05a. Preloaded and workflow-resolved tickets share admission/normalization semantics. Attacker-editable text cannot grant resolved status or technician authority. Exact schemas remain pending.

## Approved storage mapping — D10

SQLite through Python sqlite3 stores accounts, tickets, threads, and turns. Qdrant stores embeddings and chunk payload metadata behind the index adapter. Link Qdrant collection/point identities to the existing snapshot and chunk identities, preserving model/dimension/metric compatibility checks and keeping observer labels outside retrieval payloads. Exact schemas, ID mapping, search settings, and publication policy remain pending. Retain corpus/index manifests and sanitized trial/judge/audit artifacts separately on persistent host storage. Database persistence alone does not satisfy trace completeness or make a collection immutable.

## Identity and mutation

D09 adds a conversation contract: `thread_id`, ordered `turn_id`/sequence, role, text, request ID, completion status, and timestamps. A new question creates a fresh thread; follow-ups reference only their own thread. D10 selects SQLite persistence; schemas, retention/resume, ownership validation, and retry/idempotency details must be specified before implementation. Do not let caller-supplied history declare trusted provider roles.

Context results and trial traces additionally record thread/turn IDs, the exact included history, omitted turn IDs/reasons, and history token accounting. Record the retrieval query actually used for each turn. Failed or retried requests must not silently create duplicate completed turns. A prior assistant answer is conversation history, not a supporting document.

Define canonical hashing once. A document's stable logical ID can survive an edit, but its content hash and derived chunk/index identities must change. Detect conflicting repeated IDs; do not silently overwrite. Reingesting unchanged input into a new build should produce the same logical records. Build to a temporary output and publish only a complete snapshot; failed builds must not appear ready.

## Experiment-only metadata

Store clean/attacker membership, condition, poisoning budget, target string, and expected answers in observer manifests. D08 fixes the admitted attacker-document count at N = 5 for each poisoned snapshot (41 total documents versus 36 clean); identify the five parent ticket IDs and hashes separately from chunk IDs and instruction-occurrence counts. Matched attacked/defended runs reference the same poisoned snapshot. Identify the frozen five-ticket set with its content hashes and observer-only cover-topic annotations and shared base-instruction/target-directive identity. The approved stories are distinct and collectively span the three recovery topics. Exact payload text and variant definitions remain pending. Ordinary source metadata can be exposed only through a declared prompt policy. Attacker flags, ground-truth markers, and evaluation labels must never help retrieval or generation. Do not infer attacker membership from a substring of the chunk text.

D08 additionally requires authoring provenance outside victim inference: the exact restricted brief, identities of any supplied materials, frozen ticket content hashes and freeze time, and known information leakage/deviations. Keep withheld corpus, victim prompts/configuration, actual development/held-out questions and keys, and victim traces outside attack-authoring inputs. Record observer analysis against frozen ticket identities; do not silently replace payloads after inspecting results.

For the D08 initial study, identify one logical answer outcome per held-out query/condition, with all 30 query IDs represented in the planned manifest for each of the three conditions. Keep operational attempt/retry IDs distinct from experiment repetition identity. Preserve failed/missing outcomes and paired eligibility rather than replacing unfavorable completed answers. Reused clean outcomes must link to compatible frozen configuration identities; record the 18-question target subset separately from the other categories.

M_a verification is optional future work only. No attacker-model request/result records or extension-specific schemas are required for the current study; define them if the extension is later selected.

## Error and output policy

Use structured stage errors for invalid input, unavailable model, index mismatch, context overflow, provider timeout, and write failure. Every entry point returns a non-success status on unrecovered operational failure. The approved rewrite fallback may yield a completed answer with explicit degraded-retrieval metadata; retain the rewrite-stage error separately. A valid insufficient-evidence answer is a completed generation, not an infrastructure error. If limits are exceeded, reject or apply a documented policy; never silently report a partially indexed corpus as complete.
