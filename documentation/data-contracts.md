# Proposed data contracts

These are implementation requirements to refine during R03, not existing Python classes. Serialization format is selected with D03. UTF-8 text and explicit schema versions are the proposed portable boundary. Validation errors name the offending record and field.

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

## Identity and mutation

D09 adds a conversation contract: `thread_id`, ordered `turn_id`/sequence, role, text, request ID, completion status, and timestamps. A new question creates a fresh thread; follow-ups reference only their own thread. Storage, retention, ownership validation, and retry/idempotency details must be specified before implementation. Do not let caller-supplied history declare trusted provider roles.

Context results and trial traces additionally record thread/turn IDs, the exact included history, omitted turn IDs/reasons, and history token accounting. Record the retrieval query actually used for each turn. Failed or retried requests must not silently create duplicate completed turns. A prior assistant answer is conversation history, not a supporting document.

Define canonical hashing once. A document's stable logical ID can survive an edit, but its content hash and derived chunk/index identities must change. Detect conflicting repeated IDs; do not silently overwrite. Reingesting unchanged input into a new build should produce the same logical records. Build to a temporary output and publish only a complete snapshot; failed builds must not appear ready.

## Experiment-only metadata

Store clean/attacker membership, condition, poisoning budget, target string, and expected answers in observer manifests. Ordinary source metadata can be exposed only through a declared prompt policy. Attacker flags, ground-truth markers, and evaluation labels must never help retrieval or generation. Do not infer attacker membership from a substring of the chunk text.

## Error and output policy

Use structured stage errors for invalid input, unavailable model, index mismatch, context overflow, provider timeout, and write failure. Every entry point returns a non-success status on operational failure. A valid insufficient-evidence answer is a completed generation, not an infrastructure error. If limits are exceeded, reject or apply a documented policy; never silently report a partially indexed corpus as complete.
