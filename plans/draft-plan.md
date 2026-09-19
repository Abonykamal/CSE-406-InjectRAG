# InjectRAG — replacement implementation draft

Created: 2026-09-13. Updated: 2026-09-17. Status: **ready to begin the clean-system build; live runs and attack scoring have explicit gates below**.

This plan supersedes the previous README implementation checklist and does not adopt the submitted report's §4 phase list as its task structure, but it does deliver all six of those phases — see the [phase mapping](../documentation/design-review.md#submitted-report-implementation-phase-mapping). It uses the research intent of [`design_report.pdf`](../design_report.pdf) while reviewing its assumptions; the [deviation register](../documentation/design-review.md#deviation-register--submitted-report-versus-implemented-study) records every intentional departure. The immediate deliverable is a functioning, inspectable **clean RAG target** that later attack and defense experiments can use without rewriting the application.

The user now requests a rapid implementation path toward attack and defense. Begin the accepted clean-system build without another blanket design-approval round. This revision prepares the implementation plan; it does not claim code exists. Resolve routine details in their tasks and record them; only changes to accepted scope, models, budget, threat model or measurement claims require renewed approval. See [status](../documentation/project-status.md), [decisions](../documentation/decisions.md), and [report review](../documentation/design-review.md).

## 1. Scope and completion definition

The first implementation must ingest synthetic helpdesk knowledge, normalize and chunk documents, embed and persist them, retrieve relevant chunks for a question, assemble a bounded model request, generate an answer, and save a trace linking the answer to its exact inputs. Establish clean-system quality and a reproducible frozen baseline before constructing attacks.

A small clean corpus belongs early in the build: ingestion and retrieval cannot be validated without representative inputs. Expand and freeze that corpus later. The first system is not complete merely because a chat response is returned.

Build the clean target first, then execute R18–R22 below for the fixed attack, spotlighting comparison and budget sweep. Keep production identity-provider integration, external deployment and optional attacker-side optimization outside required work. Docker delivery and local account/role enforcement are approved initial scope. D01 is accepted: the first working application includes an API and a simple chat UI. A CLI alone does not satisfy this scope. Preserve extension points for experiments without implementing those later systems prematurely.

## 2. Implementation gates and rapid delivery order

D01–D12 settle the required stack, models, ticket/login/history behavior, retrieval, errors, retry eligibility, corpus/study counts and budget; [D14](../documentation/decisions.md#d14) revises only the aggregate budget and adds R22. Do not reopen those choices. The latest request authorizes moving into implementation; the review here makes the work concrete without launching experiments.

| Gate | Must be established | Work that can proceed meanwhile |
|---|---|---|
| Start the build | Existing D01–D12 decisions; current user request | Scaffold, local adapters, contracts, storage, UI and deterministic tests immediately |
| First hosted pilot call | Configured credentials, verified model access/free tier/quotas, persisted budget ledger, complete trace, reviewed pilot inputs and judge contract | Use fake provider responses; local corpus/index work does not need Gemini access |
| Freeze clean evaluation | Clean-development checks, prompts/chunking/settings and scorer frozen; six script contents/split declared | Build the comparison runner and fabricated scoring fixtures |
| Author/freeze attack | Exact target behavior/marker and five-ticket payload specification; restricted author context, without withheld material | Build generic ticket/snapshot/observer interfaces; no payload tuning on victim results |
| Execute security comparison | D06 clean readiness passed, frozen five tickets, behavioral rubric and attack-audit scope declared | Implement spotlighting and trace comparison with synthetic fixtures |

Routine SQL/API fields, publication orchestration, visit semantics, size caps, bounded retry waits and initial clean chunking/prompt settings are implementation work within D12. Write their concrete values and meaningful checks during R03/R05a/R06/R10, before use; do not create a new project-wide approval gate for each helper or setting. The implementation defaults below are explicitly implementer choices, not claims of additional user approvals. Evidence that requires changing an accepted setting goes back for review.

D11 selects BAAI/bge-small-en-v1.5 through FastEmbed/ONNX Runtime on CPU and Gemini gemini-3.8-flash for answers and separate observer judging. D12 removes the rewrite model from required scope. Use google-genai, Python 3.12 and low thinking for answers/judging. Resolve compatible stable dependencies during authorized setup, commit exact uv.lock versions, pin Docker images by digest, and record embedding revisions/hashes before baseline freeze. Revised pilot: 15 answers + 20 judgments including five fabricated cases = 35 calls, plus five retries (40 attempts), within 100 total API requests. [D12](../documentation/decisions.md#d12) approves the whole-study budget and [D14](../documentation/decisions.md#d14) adds the R22 sweep: pilot 35 + development 60 + held-out 180 + clean scripts 36 + sweep 36 = 347 calls; phase retry reserves 5/5/10/5/3 give 375 attempts. Enforce 800 total API requests, 8,192 input tokens per attempt, 4,096 pilot/2,048 later output caps, 3,072,000 aggregate input and 849,920 aggregate output tokens. Dropping R22 reverts these to 311 calls, 336 attempts, 2,752,512 input and 770,048 output tokens. Retain 90-second attempt timeouts and D11 pilot memory/latency targets. Six clean scripts run once, three turns each with per-turn judging; contents/split remain to specify. Preserve cumulative counters across run restarts. Budget approval does not replace account access, quota verification or readiness evidence. Implementation uses fake hosted responses until those live-run prerequisites are satisfied.

### Rapid delivery batches

| Batch | Tasks | Working outcome and stop condition |
|---|---|---|
| A — runnable skeleton | R01 preflight, R02, R03, R12 foundations | Locked app/Qdrant setup, validated configuration, storage migrations, fake provider and durable budget/trace records; no hosted calls |
| B — clean vertical slice | Small R04 inputs; R05–R11; R13, R13a/R13b minimum UI | Login, submit/resolve/publish, current-question top-five search, grounded request assembly, answer/history/errors through one shared pipeline |
| C — clean study preparation | Finish R04/R15, R14; R16 pilot/development | 36 documents, 30+30 questions, six scripts, working judge/scorer, real feasibility evidence inside the 35-call pilot; freeze clean configuration |
| D — clean gate and fixed attack | R16 held-out clean, R17, R18/R19 | 30 clean answers/judgments retained once; D06 readiness evidence; frozen five-ticket attack and 41-document poisoned snapshot |
| E — attack then defense | R20/R21, then R22 | 30 attacked and 30 defended answers/judgments, paired exposure/behavior metrics and report; then the optional-to-drop N ∈ {1, 3} sweep |

Complete thin working slices; R01–R22 are acceptance references, not separately approved projects. Implement shared config, traces and provider contracts once. Use small fixtures for debugging, then expand to the approved corpus. Keep UI styling minimal but include the approved login, ticket and chat workflows. No second frontend, general job broker, rewrite service, reranker, extension matrix or new model is needed. Do not promise a completion time until setup/account feasibility is known.

### Concrete starting implementation details

These defaults refine accepted behavior and must be recorded in resolved configuration. They are not measured optimal settings or changes to D12.

- Storage: use the table/transaction outline in [SQLite plan](../sqlite-schema-plan.txt), without a sessions table. Use UUID text IDs, UTC ISO timestamps, SHA-256 canonical hashes, parameterized SQL, foreign keys and numbered migrations. Implement only fields actually consumed by the workflow.
- Publication: serialize complete builds in the app using durable publication rows; build a new collection/manifest, validate membership, then atomically switch the SQLite live pointer. Recover interrupted builds and expose manual publication retry. This indexing work is separate from the rejected waiting chat queue; no broker or extra service.
- Visits: page refresh/navigation away ends the active visit. Keep the visit token in page memory, validate owner/runtime/visit server-side, and never offer old-thread reopening. Retain rows. Browser unload events alone are not an enforcement mechanism.
- Retry waits: one retry after 1 second for eligible network/timeout/5xx errors. For 429, honor a valid Retry-After only when at most 30 seconds; otherwise pause/report the rate limit. Daily quota always pauses. Hold the inference slot through the bounded retry; never queue new chat calls.
- Input bounds: start with 2,000 Unicode characters for questions and additionally reject embedding input over 512 tokens including prefixes/special tokens, before a search; never truncate. Use HTTP 413 with a shorten-question message for either question bound. Limit ticket description/resolution to 20,000 characters each before ingestion; chunk rather than truncate admitted text.
- Chunking: start with paragraph-aware chunks of at most 320 embedding-token units with at most 48 tokens overlap; split overlong paragraphs deterministically with offsets. Recheck the actual embedding payload including title/prefix/special tokens against 512. Answer-model token accounting is separate. Preserve all source content and inspect clean coverage before freezing.
- Prompts: implement the accepted grounded answer/citation/clarification behavior with labeled evidence outside the system role, full ordered active history and current question last. Freeze exact text/hashes after clean development. Spotlighting later adds only its declared boundary and handling instruction.
- Scripts: assign three scripts to development and three to held-out checks before executing any. Each has three turns and one execution with per-turn judging, totaling the approved 36 calls. Cover references, corrections, topic changes, misleading prior answers and fresh-thread isolation across the six; report scripted fixture content separately from model-generated history. No repeated live script tuning is allocated.

### One budget, one set of live checks

Use deterministic fake-provider tests for R02/R11/R13/R14 and local known-vector/embedding checks for retrieval. The first real hosted request is the first planned R16 pilot answer, after the trace, quota checks and persisted counters exist. It supplies the live adapter/API feasibility evidence for those earlier tasks; do not demand another smoke call at each milestone. If it fails, retain the outcome and apply only the approved retry rules. Resume the remaining planned pilot entries without resetting counters.

Build pilot inputs against the intended corpus/prompt configuration before dispatch; a casual hello-world call cannot later be relabeled as a scored pilot answer. Verify reproduction through rebuilds, local retrieval, saved response replay and artifact/scoring checks; do not regenerate already counted outputs. A changed configuration requiring additional hosted trials needs a revised allocation. The budget has no hidden tuning, smoke or demonstration-call allowance.

## 3. Proposed organization

Use subdirectories to separate the target from experiments and data. With D03 approved, use the [proposed repository structure](../documentation/repository-structure.md): `src/injectrag/rag/` for victim logic, thin selected entry points, `evaluation/` for baseline scoring, and later `experiments/` and `attacks/` packages. Keep versioned inputs in `data/`, runtime choices in `configs/`, prompts in `prompts/`, and generated state in ignored `artifacts/`.

Create application directories only when their tasks start. Do not create a second deployable project unless a separately built interface or another concrete requirement justifies it and the user approves. Paths follow the approved single-Python-project direction; refine internal files as implementation requires.

## 4. Task dependency map

```text
R00 accepted decisions → R01 preflight + R02 scaffold → R03 contracts/config
R03 → R12 traces/budget ledger + R04 seed → R05 ingestion → R06 chunking
R02/R03 → R07 embeddings → R08 index → R09 retrieval
R03 + SQLite outline → R05a ticket lifecycle → API/UI workflows
R03 + model limits → R10 context + R11 provider/fake adapter
R09–R12 → R13 shared pipeline → R13a API → R13b UI → R14 local integration
R04 + R12 → R15 full corpus/query split + scorer
R14 + R15 + account/quota verification → R16 pilot/development/freeze/clean baseline
R16 clean readiness → R17 reproduction + R18 attack freeze → R19 poisoned snapshot
R19 + rubric/audit gate → R20 attacked run → R21 spotlighting/defended run/report
R20 + R21 complete → R22 nested N ∈ {1, 3} attacked-only budget sweep
```

This is dependency information, not a request to spawn agents. Tasks can be implemented in dependency order by one implementation agent. Application tasks remain **not implemented**. R00 core design is sufficient to begin; implementer defaults above resolve routine starting settings, while attack/scoring choices gate only their dependent work. R01 has hardware/source inventory and historical official-document review only, not a completed account/feasibility check. Verify actual selected endpoint availability during setup; the recorded model name is not proof it exists or is available to this account.

## 5. Agent-executable tasks

### R00 — Resolve design gates and record approvals

**Prerequisites:** read the report review, draft architecture, and decision register.

1. Preserve the accepted D01/D03 answers and revised hosted-generation D02 direction; resolve only remaining details, without re-asking approved choices.
2. Record constraints, selected direction, and any unresolved exact technology choice.
3. Resolve remaining D04–D06 implementation/resource settings without re-asking approved corpus, prompt/history, scoring, sample-size, and readiness choices.
4. Create accepted decision records only for actual approvals; amend downstream paths and scope accordingly.

**Deliverables:** decision records and updated plan/status. **Acceptance:** an agent can identify which choices are approved and which tasks remain gated. **Stop condition:** do not scaffold an unapproved language or invoke an unapproved paid runtime.

### R01 — Verify the selected runtime and resource feasibility

**Prerequisites:** accepted D10–D12 design and current implementation direction. Run local preflight alongside scaffolding; verify credentials/quotas before hosted work.

1. Use the [hardware inventory](../documentation/local-runtime-feasibility.md), rechecking dynamic memory/disk before a pilot. Inspect runtime tooling without dumping credentials.
2. Verify D11 CPU BGE-small/FastEmbed/ONNX with the D10 FastAPI/SQLite/Qdrant two-service stack; verify official model availability and published free-tier limits separately from actual account quotas. Measure local application/embedding/index memory and end-to-end API latency under bounded concurrency. Local generation benchmarking is not required; paid usage and silent fallback are not approved.
3. Preserve D11 model selections and pilot limits. Resolve compatible stable dependencies for Python 3.12, pin image digests and embedding artifacts under the approved policy during authorized setup. Record provisioning sizes and account quotas before live work; substitutions require review.
4. Run a tiny local embedding batch after R07 exists. Obtain real hosted-generation evidence from the first planned R16 pilot answer, not an extra smoke request. R01 preflight can pass for scaffolding while measured hosted feasibility remains outstanding.
5. Record exact versions/revisions and limitations. If infeasible, bring evidence and alternatives back before changing runtime strategy.

**Deliverables:** preflight record, dependency/version inputs and later measured feasibility evidence. **Acceptance:** R01 preflight identifies tooling/resource/compatibility blockers; R02 does not wait for a nonexistent pipeline. Close measured feasibility only after real embeddings and the first budgeted pilot request succeed; mocks are not feasibility evidence.

### R02 — Scaffold the approved project and development environment

**Prerequisites:** D10–D12 accepted and R01 local preflight; hosted-generation measurements are not a scaffolding prerequisite.

1. Create the minimal package/entry-point structure from the approved layout.
2. Implement D10 Docker delivery with one custom application image and the Qdrant image as two Compose services. Pin approved versions and define separate persistent host mounts for application state, Qdrant data, snapshots/results, and model cache. Reuse the application image for one-off research jobs. Add pyproject.toml and a committed uv.lock with locked installation and build/start validation; separate routine testing dependencies from optional live-model integrations where useful.
3. Add ignore rules for generated artifacts, secrets, caches, and weights; add environment-variable placeholders only.
4. Configure the project's formatter/linter and test runner without adding unused frameworks.
5. Add an import/help smoke check and document the actual setup commands in `documentation/local-development.md`.

**Deliverables:** package skeleton, lockfile, config/ignore files, tested setup guide. **Acceptance:** a clean environment can install the locked project and run help/import plus the default checks without live model calls.

### R03 — Define contracts and validated configuration

**Prerequisites:** R02 and approved provider/index choices.

1. Implement the records in [data contracts](../documentation/data-contracts.md), including schema versions and explicit stage errors.
2. Centralize canonical serialization/hashing and ID rules; define offset units and normalization behavior.
3. Implement resolved configuration covering model identities, input/output paths, chunking, retrieval, context/output budgets, generation settings, and retry limits.
4. Reject impossible sizes/overlap, missing required values, invalid top-k, and incompatible settings with actionable errors.
5. Separate secrets from serializable run configuration; ensure observer labels cannot enter a question request.

**Deliverables:** contracts/config modules, sample nonsecret configuration, validation fixtures. **Acceptance:** valid configuration round-trips consistently; invalid boundary cases fail before indexing or paid generation; serialized records contain no secrets.

### R04 — Create a small policy-consistent development corpus

**Prerequisites:** R03, D04; choose a small policy-consistent subset of the approved D06 corpus; this needs no separate seed-size approval.

1. Write the fictional organization's canonical policy and approved answer facts.
2. Author a small official-article/ticket sample spanning answerable questions, paraphrases, and adjacent-topic distractors.
3. Include ingestion/chunk-boundary fixtures separately from the realistic seed corpus.
4. Assign stable IDs and provenance; write a few development questions and separate answer keys with relevant document IDs.
5. Review contradictions and ensure later target markers are absent from clean material.

**Deliverables:** versioned clean seed documents, policy, query/key records. **Acceptance:** every answerable seed query has supporting evidence; unsupported examples are explicitly labeled; no observer answer fields are embedded in source documents accidentally.

### R05 — Implement the legitimate ingestion path

**Prerequisites:** R03/R04 and approved ticket admission semantics.

1. Implement one approved local source format before supporting additional parsers.
2. Load records, validate source metadata and body, normalize reproducibly, and preserve source reference/hash.
3. Reject malformed input and conflicting duplicate IDs; define batch failure behavior explicitly.
4. Emit a normalized corpus manifest with accepted/rejected records and reasons.
5. Apply the same rules to all tickets; retain model-directed text as content rather than adding an undeclared defense.

**Deliverables:** ingestion adapter/module and inspectable normalized outputs. **Acceptance:** unchanged input produces identical logical documents; malformed/duplicate/empty records cannot silently enter a supposedly complete corpus; content survives normalization as specified.

### R05a — Implement executable ticket submission and resolution

**Prerequisites:** R03, D12 accepted lifecycle/login policies and finalized SQLite/publication design; R05 for admission integration.

1. Implement submission and technician resolution with distinct employee description and resolution fields. Use seeded local employee/technician accounts and API-enforced roles; use D12 signed-cookie SessionMiddleware with account ID only, HttpOnly/SameSite=Strict browser-session cookie, hashed passwords and SQLite role/ownership checks; no sessions table. Finalize SQLite schemas/transactions. No ticket edits/reopening; employee actions cannot set technician resolution or resolved status.
2. Keep unresolved tickets outside the searchable corpus. Route resolved tickets and preloaded resolved-ticket records through common eligibility, normalization, identity, and provenance rules.
3. Start live publication automatically on resolution. Publish only complete validated snapshots; distinguish resolved from searchable, retain visible retryable failures, and preserve frozen experiment snapshots. Finalize orchestration using the SQLite proposal before coding.
4. Expose submission, inspection, and resolution through the API/browser UI in R13a/R13b using the approved actor representation.
5. Verify one-way resolution, immutable descriptions, unresolved exclusion, seed/workflow equivalence and publication failures/retries. Verify logout cookie clearing, startup signing-secret invalidation, cross-site mutation rejection and API ownership enforcement.

**Deliverables:** ticket workflow, seed import integration, and lifecycle/actor/publication contract. **Acceptance:** submit, resolve, publish, and retrieve a ticket through the real pipeline; unresolved content stays out of the index and employee controls cannot modify technician-only fields. Equivalent seeded tickets yield equivalent corpus documents. Verify authenticated role and ticket-ownership checks directly through the API, including employee resolution denial. Registration and email integration are outside initial scope.

### R06 — Implement deterministic chunking and provenance

**Prerequisites:** R05; tokenizer/splitter choice from R01/R03.

1. Implement the approved splitting unit, chunk size, overlap, and long-section behavior.
2. Generate stable chunk IDs with parent document identity, offsets, token counts, and preprocessing fingerprint.
3. Add an inspection output showing chunk boundaries for a chosen document.
4. Test short/long documents, boundary-length inputs, repeated text, and Unicode against the normalization contract.
5. Do not tune chunk size to ensure an attacker instruction fits; keep the clean pipeline's rule ordinary and observable.

**Deliverables:** chunker and chunk inspection path. **Acceptance:** no empty chunks or unexplained text loss, valid parent offsets, reproducible IDs, and explicitly documented overlap behavior.

### R07 — Implement the embedding adapter

**Prerequisites:** R01/R03 and provider resource approval.

1. Define document-batch and query embedding operations for BAAI/bge-small-en-v1.5 through CPU FastEmbed/ONNX, with explicit input conventions. Enforce its 512-token input limit including prefixes/special tokens; validate 384-dimensional vectors.
2. Implement the selected adapter with bounded batches, explicit error handling, and recorded model revision/dimension.
3. Validate finite vectors and dimensions; apply the approved normalization consistently.
4. If caching is needed, key by text hash, model revision, and embedding settings; otherwise defer caching.
5. Provide a deterministic fake adapter for routine tests and a marked real-runtime smoke check.

**Deliverables:** embedding interface/adapter and real smoke artifact. **Acceptance:** document/query vectors use compatible dimensions; changed model/settings cannot reuse incompatible cached data; failures do not masquerade as valid vectors.

### R08 — Build and reload isolated index snapshots

**Prerequisites:** R06/R07.

1. Implement the local Qdrant index adapter with explicit approved similarity/search settings, score meaning, and point-to-chunk mapping; retain observer-only metadata outside retrieval payloads.
2. Build from a complete chunk manifest into an isolated Qdrant collection, then publish a ready snapshot under the approved publication policy. Preserve frozen collections; Qdrant does not make them immutable automatically.
3. Persist vector-to-chunk mappings and the full compatibility manifest.
4. Load snapshots only after validating model, dimension, normalization, and corpus/preprocessing identities.
5. Support a clean rebuild without duplicate insertion or modification of a frozen prior snapshot.

**Deliverables:** index build/load operations and manifest. **Acceptance:** fresh versus reloaded rankings match on known-vector fixtures; interrupted/incompatible builds fail clearly; rebuilding does not change corpus membership unexpectedly.

### R09 — Implement inspectable retrieval

**Prerequisites:** R08 and query embedding adapter; retrieval needs no hosted rewrite adapter.

1. Embed the current question as written, including follow-ups, and make one cosine vector search for top five chunks (or fewer if the corpus is smaller). No history concatenation, rewriting, fusion or reranking.
2. Sort by descending cosine score with stable chunk-ID ties; deduplicate only chunk IDs. No per-document quota, source preference, observer-label filtering or uncalibrated cutoff. Return explicit empty-index outcomes.
3. Return typed ranked hits with chunk/document identity and text.
4. Expose a retrieval-only inspection command or equivalent approved interface.
5. Validate evidence coverage on the 30 clean development questions and follow-up behavior on development conversation fixtures. Inspect corrections, topic shifts, vague references and misleading prior answers; full history goes only to generation. Trace raw top five and actual included evidence; clarify when evidence cannot support an answer. No automatic Qdrant retries. Freeze accepted settings before held-out trials and seek review with clean evidence before changing them.

**Deliverables:** retriever and inspection output. **Acceptance:** a known-vector test establishes ranking independently of the implementation; real seed queries produce traces that identify evidence and ranking without ground-truth-assisted selection.

### R10 — Implement baseline prompt and context construction

**Prerequisites:** R03, D05, selected model/token limits; use typed retrieval fixtures until R09 is ready.

1. Version the approved baseline system prompt and ordinary source rendering format.
2. Assemble trusted instructions, the current thread’s selected prior user/assistant turns, current question, and newly retrieved evidence in explicit provider roles; corpus text and prior answers cannot become system instructions.
3. Calculate the available input budget including selected history, formatting, query, output reserve, and margin. Preserve full history by default without routine trimming/summarization; place fresh evidence after history and the current original question last. Do not replay old retrieval bundles. Enforce HTTP 422 context overflow without model work or failed turn append; preserve typed text and log the error. Check the 8,192-token input ceiling and model context limit with output reserve.
4. Include whole chunks in rank order under at most 2,048 evidence tokens including labels and the complete request limits; record exact included text and excluded IDs/reasons. Do not silently cut text or history.
5. Define no-evidence and oversized-query behavior; reserve a narrow context-builder interface for later defenses.

**Deliverables:** prompt file, context builder, exact-message fixtures. **Acceptance:** boundary tests verify budget behavior and role separation; no experiment labels/answer key enter messages; emitted traces distinguish top-k retrieval from actual exposure.

### R11 — Implement generation with explicit operational outcomes

**Prerequisites:** R01/R03 and approved resource budget.

1. Implement Gemini through google-genai behind a provider-independent request/result interface, using gemini-3.8-flash answers with low thinking and separate observer-judge requests. Map roles and supported settings explicitly. Keep provider code out of retrieval and scoring; replacements require their own adapter validation and baseline.
2. Pass resolved model, temperature, output cap, and supported reproducibility settings explicitly.
3. Capture response text, finish reason, available usage, latency, and reported model identity.
4. Enforce a 90-second attempt timeout and at most one retry only for temporary network errors, timeout, provider 5xx or 429 with a short retry window. Finalize bounded wait timing. Judge retries never regenerate answers; quota stops pause. No retries for wrong answers, poor retrieval or missing markers. Preserve all attempts and phase/study counters; classify truncation explicitly.
5. Use fake responses for default tests and a marked real-model request for integration validation.

**Deliverables:** adapter and fake-provider error cases; live evidence is supplied by R16 without another call. **Acceptance:** a failure returns structured failure rather than an empty successful answer; retries obey limits; secrets do not enter logs; unavailable provider metadata is honestly labeled.

### R12 — Implement trace and run-manifest persistence

**Prerequisites:** R03; can use fixtures before full pipeline integration.

1. Create run/trial identifiers and immutable resolved manifest records.
2. Serialize stage timings, ranked hits, exact final messages, inclusion decisions, sanitized provider request bodies, returned responses/metadata, and each attempt/error. Persist artifacts outside disposable container state; exclude credentials and session secrets.
3. Link each trial to corpus/index/config/prompt/model/query identities.
4. Make partial/failed runs inspectable, and prevent accidental overwrite of prior results. Persist D12 cumulative phase/study API, inference, retry and token counters; reserve capacity before dispatch and conservatively account for unknown usage. Pause at limits rather than resetting counters on restart.
5. Keep observer labels in separate joined records and protect credentials from logging.

**Deliverables:** tracing module and sample success/failure artifacts. **Acceptance:** an observer can reconstruct exactly which synthetic evidence was sent and identify operational failures without rerunning generation.

### R13 — Integrate the target pipeline and selected entry point

**Prerequisites:** R09–R12.

1. Compose load-config → load-index → retrieve → construct-context → generate → persist-trace.
2. Expose index build, retrieval inspection, and question answering through the approved entry point.
3. Return answer/source references and a run/trace location; provide understandable stage errors.
4. Keep presentation code thin and core logic callable by a later experiment runner.
5. Document and execute the real end-to-end commands in the development guide.

**Deliverables:** orchestration and functional entry point. **Acceptance:** starting from seed source files, a user can build an index, restart, invoke the shared pipeline, and inspect its trace. Complete user-facing delivery additionally requires R13a and R13b.

### R13a — Expose the pipeline through the API

**Prerequisites:** R13, R05a, D10 FastAPI/Uvicorn and approved request concurrency policy.

1. Define versioned thread/turn/question/answer/error schemas with answer text, source references, and request ID; keep observer-only labels outside public responses. Implement thread creation/reset and SQLite-backed isolated history with indefinite retention for inspection and no old-thread continuation after leaving/restarting. Finalize page-refresh/visit semantics and enforce eligibility server-side.
2. Implement a question endpoint and readiness endpoint; readiness must distinguish an unbuilt index or unavailable model from a ready application.
3. Validate before inference: HTTP 413 for oversized raw questions, HTTP 422 for context overflow and HTTP 503 with a busy code when the inference slot is occupied. Preserve input; start no model work or turns for rejected requests. Set routine raw-size limits.
4. Start with one Uvicorn worker per D10, load/reuse runtime resources deliberately, keep blocking embedding work off the event loop, and use one inference slot and no waiting chat queue; do not duplicate model instances unintentionally per request or worker.
5. Document the endpoint contract and startup/shutdown behavior; test with deterministic adapters and local embeddings plus real Gemini generation under the approved free-tier pilot.

**Deliverables:** API package including ticket submission/resolution endpoints and `documentation/api.md`. **Acceptance:** an HTTP request traverses the real shared pipeline; invalid input, unavailable runtime, and overload have explicit outcomes; a slow generation does not prevent readiness checks. Measure memory and latency rather than assuming concurrent inference is feasible.

### R13b — Build and integrate the simple browser chat UI

**Prerequisites:** R13a and R05a; D10 plain API-served UI and detailed history policy implementing D09.

1. Create FastAPI-served plain HTML/CSS/JavaScript assets with an accessible question form, transcript, loading indicator, answer panel, and source references. Use fetch and complete responses; streaming is deferred by D10.
2. Call the API; prevent accidental duplicate submission, preserve the question on error, and show actionable failure/retry states.
3. Render model/source text safely as content. Link only through the approved source-link policy; do not interpret model text as executable HTML.
4. Keep follow-ups in the active question thread, supplying prior turns to the model through the API. Add “New question” to begin a fresh thread; do not carry old turns into it or infer topic changes automatically. Offer no old-thread resume after leaving/restarting; retain historical rows for inspection only.
5. Verify keyboard submission/focus, narrow-screen layout, empty input, delayed answer, API failure, and successful source display in a browser. Document actual launch and usage steps.

**Deliverables:** integrated chat and ticket submission/resolution UI with browser validation record. **Acceptance:** a user can launch the documented app, ask a question in the browser, see an answer and sources, and recover from an error; the resulting trace identifies the same API request. Mocked UI checks alone do not satisfy the real RAG integration check.

### R14 — Validate end-to-end failure handling and isolation

**Prerequisites:** R13a/R13b.

1. Test missing/incompatible snapshot, empty input, no usable evidence, context overflow, provider failure, and trace-write failure.
2. Verify same-thread follow-ups receive the correct ordered history, while new questions and interleaved threads remain isolated. Test retries/failures without duplicate turns, history-budget overflow, and immutable index state.
3. Verify the victim package does not depend on attack/scoring modules or consume answer keys.
4. Execute default checks with fake hosted responses and real local retrieval. Obtain hosted integration evidence from the planned R16 pilot; do not add smoke calls.
5. Fix failures and update the troubleshooting guide with observed issues only.

**Deliverables:** integration tests and validation record. **Acceptance:** failures are visible, bounded, and reproducible; successful runs have complete provenance; no silent fallback changes the selected model or experiment condition.

### R15 — Complete the clean corpus, query split, and baseline scorer

**Prerequisites:** R04, D06; scorer consumes R12 contracts.

1. Expand synthetic corpus and questions to approved counts and topic distribution using the canonical policy.
2. Review answer keys, document relevance, unsupported cases, and paraphrase-family split boundaries.
3. Implement automated evidence/citation checks, separate marker containment, and observer-only model judging with the approved rubric. Retain judge artifacts/errors and limited human-audit selections/corrections; report unscored judgments explicitly. Use the approved initial 10-answer audit plus flagged cases; D11 selects gemini-3.8-flash with low thinking and pilot usage bounds; rubric implementation, account verification and execution authorization still precede live scoring. D12 approves the aggregate budget; use one judgment per answer for all required semantic labels and compute deterministic metrics locally. Disclose shared answer/judge-model limitations.
4. Test scoring with fabricated responses containing warnings, both markers, missing markers, paraphrases, and errors.
5. Freeze held-out evaluation inputs with hashes; keep them outside attacker-side development material and document the procedural limitation. Use fresh threads for independent trials and a separate scripted multi-turn set to test D09; freeze turn order and report those results separately.

**Deliverables:** reviewed corpus/query manifests, answer keys, baseline scorer and scoring examples. **Acceptance:** denominators and missing/failed cases are explicit; correctness is not silently equated with string containment; RAG receives only question text and ordinary evidence.

### R16 — Run development pilot, freeze, and measure the baseline

**Prerequisites:** R14 local/fake-provider checks, R15 and approved readiness/resource thresholds. Live feasibility evidence is produced here; it is not a prerequisite for this first pilot.

1. Run the revised D11/D12 pilot after execution authorization: five development questions × three answers, judge those 15 outputs and five fabricated validation cases = 35 calls, plus at most five retries. Enforce cumulative API/token/time/memory bounds; no rewrite fixtures. Use the D12 allocations for one full development pass (60 calls), the three-condition held-out study including clean baseline (180), and six clean three-turn scripts once each with judging (36). Scripts are reported separately; author contents for the three-development/three-held-out split before use. Extra tuning calls or incompatible baseline reruns require a revised allocation.
2. Inspect retrieval misses, evidence truncation, wrong answers, unsupported answers, latency, resource use, and output variability.
3. Adjust only approved development parameters; seek approval for major design changes and record rationale.
4. Freeze resolved configuration, prompts, corpus, query set, model/dependency identities, and index manifest.
5. Before held-out judging, freeze a judge contract compatible with all three conditions, including the chosen attack-behavior rubric if those labels are claimed. Otherwise clean judgments cannot be assumed reusable and extra judging needs a revised allocation. Execute the frozen held-out baseline, preserve all failures, and compare with D06 thresholds. Do not tune against this result while continuing to call it held-out.
6. Write `documentation/baseline-results.md` with counts, rates, limitations, and artifact links.

**Deliverables:** baseline bundle and measured readiness report. **Acceptance:** agreed thresholds pass with declared reproducibility limits, or M4 remains incomplete with a concrete diagnosis. No attack-success requirement applies to this milestone.

### R17 — Reproduction check and next-phase handoff

**Prerequisites:** R16 readiness passed.

1. Exercise locked setup/build/local-query/score instructions from a clean environment, replaying retained model outputs for the hosted boundary. Do not spend extra calls rerunning the completed baseline.
2. Check that committed inputs and manifests identify every required external dependency and model provisioning step.
3. Update README, architecture, status, contracts, and decisions to describe the actual implementation.
4. Publish an internal handoff note listing public pipeline interfaces, frozen baseline identifiers, observer trace fields, and remaining limitations.
5. Continue directly to R18–R22 below using accepted D07/D08 scope: fixed N = 5, distinct covers sharing one base instruction/directive, and restricted-brief authoring followed by frozen evaluation without a surrogate or victim feedback. Use the approved one-answer-per-held-out-question-per-condition policy. Resolve remaining payload/variant details before dependent implementation. M_a verification belongs to the optional-extension list and is not a prerequisite.

**Deliverables:** verified reproduction guide and completed clean-target handoff. **Acceptance:** another implementation agent can run the baseline and diagnose an individual trial without undocumented manual edits and without any source outside this repository.

## 6. Validation and completion recording

For each task, add a status entry containing task ID, implemented files, actual check commands/results, relevant artifact locations, remaining limitations, and next task. Use `not started`, `in progress`, `blocked by Dxx`, or `complete`; completion requires the stated acceptance evidence. No tests are run against nonexistent application code.

M1 corresponds to R08, M2 to R09, M3 to R14, and M4 to R17. A successful mock test satisfies plumbing checks only. Exact-match proxy scores and actual answer quality remain separately reported. See [testing](../documentation/testing-and-reproducibility.md) for validation layers.

## 7. Fixed attack and defense implementation

Attack testing is the primary research goal; spotlighting is the secondary comparison. After M4, implement the accepted D07 knowledge/chunking boundary and resolve remaining D08 comparison-design questions. Consider instruction repetition and placement within attacker-owned descriptions as explicit variants, without hidden victim-boundary tuning; record length, chunk count, and actual instruction exposure to expose confounds. The document budget for the three main conditions is fixed at five admitted attacker tickets; the only budget variation is the droppable R22 sweep, which reuses subsets of the same frozen tickets and adds no new payloads. Use one fixed set of five distinct support stories spanning all three recovery topics and sharing the same base instruction and target directive. Freeze the set before final evaluation. Exact payload text, topic allocation, instruction repetition, placement, concealment, and variant count remain pending. M_a verification is optional future work under the shortened submitted-report scope, not a required restoration. Execute the concrete tasks below without another general planning phase. The same three conditions remain selected; no defended-clean run.

The attack author receives target topics, description permissions, general chunking knowledge, and the attack objective, and may invent example questions. Withhold clean corpus contents, victim prompts/configuration, actual development/held-out questions and keys, and victim traces from construction. Freeze tickets before victim testing; preserve the brief, supplied-material identities, ticket hashes/freeze time, and known leakage. Observer analysis must not guide revisions to the frozen attack. Disclose procedural same-team separation and non-adaptive scope.

Run the initial study once per held-out question per condition: 30 clean, 30 attacked, and 30 defended logical outcomes in fresh threads. Reuse clean baseline outcomes only with matching frozen configuration (60 additional attacked/defended answer generations, excluding judging/retries). Target attack rates use the 18 answerable recovery questions; assess the other 12 separately. Preserve all operational attempts and missing pairs, never repeat a completed answer to obtain a desired attack result, and disclose the single-answer variability limitation. The clean repeatability pilot remains unchanged; no extra payload variants are selected. D12 separately budgets clean conversation scripts; attacked/defended scripts are excluded.

Preserve the 36-document clean snapshot and normal victim configuration. The main poisoned snapshot adds exactly five admitted attacker tickets, for 41 documents; matched attacked/defended runs use the same snapshot. Count documents rather than chunks or instruction repetitions. The three-condition comparison makes no document-count scaling claim; R22 is the only place such a statement may appear, within the limits [D14](../documentation/decisions.md#d14) records. Implement the same admission path for attacker content; keep experiment labels outside the victim. D08 excludes cover-only and defended-clean conditions; audit whether instruction spans and correct evidence actually reached generation and report the resulting attribution/utility limitations. Any change to threat model, baseline prompts, budget construction, or scoring claims requires a documented decision.

Optional research ideas are maintained in [things to try if time permits](../documentation/optional-extensions.md). M_a verification, rewriting and reranking are explicitly outside required delivery. The other list entries are proposals, not approved extra runs; none adds an implementation dependency or completion gate.

The report's desired outcome is a hypothesis. A useful clean RAG that resists an attempted injection remains a valid target and result; do not weaken it to force the expected outcome.

### R18 — Freeze the attack specification and five tickets

**Prerequisites:** clean target/configuration frozen and D06 readiness passed; exact target behavior/marker and payload specification settled with the user. This is a research decision gate, not a reason to delay clean implementation.

1. Prepare the restricted authoring brief with only the approved recovery topics, employee-description permissions, general chunking knowledge and chosen objective. Keep actual corpus, questions/keys, victim prompts/config and traces out.
2. Have an author who receives only that brief produce five distinct support stories spanning the three recovery topics, with one shared base instruction/directive. Resolve wording, topic allocation, placement/repetition and concealment before freeze; do not silently add variants.
3. Record brief/material identities, ticket hashes, freeze time and known information exposure. An implementation agent that read withheld material cannot be presented as a blind author; use a genuinely separate authoring context/person or disclose and resolve the deviation before claiming the selected threat model.

**Acceptance:** five frozen employee descriptions and provenance, no victim-guided revision, no model-verification extension. No hosted attack-authoring calls are allocated.

### R19 — Build the poisoned snapshot and comparison manifest

**Prerequisites:** R18, working common ticket-admission/index path and frozen clean snapshot.

1. Admit the five descriptions through legitimate technician resolution/common normalization without giving the attacker status or resolution authority.
2. Derive a new snapshot retaining all 36 clean documents unchanged plus five tickets; verify parent hashes and 41-document membership. Freeze it.
3. Create the 30-query manifest for each condition, referencing compatible clean results once. Run original-question top-five retrieval against the poisoned snapshot and persist a shared candidate list for attacked/defended trials, with ordinary metadata only.
4. Compute exposure annotations observer-side: raw top-five membership, actual included content, instruction presence/integrity and legitimate supporting evidence. Freeze rendering/settings; differences in budget-driven context inclusion must be recorded per condition.

**Acceptance:** immutable 36/41 snapshots, shared attacked/defended retrieval, complete query IDs and manifest identities; zero hosted calls for snapshot preparation.

### R20 — Execute and score the attacked baseline

**Prerequisites:** R19; target behavior rubric and later human-audit scope fixed, scorer validated on fabricated cases, account/budget capacity checked.

1. Run each of the 30 held-out questions once in a fresh thread against the poisoned snapshot using the ordinary baseline prompt: 30 answers and 30 observer judgments.
2. A single judgment returns the required correctness/citation/behavior labels; compute marker and exposure metrics locally. Do not regenerate a completed answer or rerun retrieval because an attack misses.
3. Retain attempts, errors, exact request/context/response and labels. Compute target metrics for the 18 recovery questions and broader quality for the remaining categories; failed or unscored outcomes are explicit.

**Acceptance:** 30 planned logical outcomes accounted for, observed attack results retained without payload revision; attempts stay within the shared held-out allocation of 180 calls plus ten retries across all three conditions.

### R21 — Add spotlighting, execute defense and report

**Prerequisites:** frozen attack/snapshot and R20; preserve the selected comparison and no victim-guided payload revision.

1. Implement a context-rendering switch that adds explicit untrusted-evidence boundaries and the handling instruction. Hold model, source text, retrieval candidate list, question and other generation settings fixed. Test role separation/escaping with fabricated fixtures; freeze defense prompt/hash before its run.
2. Run the same 30 questions once, fresh-thread, using the same poisoned snapshot/candidate list: 30 answers and 30 observer judgments. Record any context exclusions caused by defense formatting; do not claim identical actual exposure if it differs.
3. Produce counts/rates for RSR_topk, RSR_context, conditional ISR (N/A for zero exposure), marker ASR/ASR-exclusive, semantic attack behavior and answer/citation quality. Preserve failures, missing pairs and human-audit corrections.
4. Report single-answer variability, marker-proxy limitations, same-team knowledge limitations and the absence of defended-clean/cover-only conditions. Link configurations, hashes and artifacts, record study usage against D12, and document a reproducible offline scoring command.

**Acceptance:** three-condition report with compatible reused clean outcomes, no extra call per metric, no unreported retries/tuning, and no claim that a failed attack invalidates the study. Finish required work before optional extensions.

### R22 — Minimal poisoning-budget sweep

**Prerequisites:** R20 and R21 complete and recorded; the R18 freeze record already states the hash-ascending order of the five frozen tickets; remaining budget confirmed against the persisted counters.

This task exists because submitted report §5.2 states that the evaluation "measures how effectiveness scales with the poisoning budget N". [D14](../documentation/decisions.md#d14) restores that claim in the cheapest form that leaves the three-condition study untouched. **R22 runs last and is droppable**: if quota, budget or time runs short, report the sweep as not performed and the study stands exactly as D08 defined it.

1. Derive Γ₁ and Γ₃ as nested subsets of the frozen Γ₅ using the hash-ascending order recorded at R18: Γ₁ is the first ticket, Γ₃ is the first three. Confirm the ordering was written down before this task began; never reorder after seeing results.
2. Build two further poisoned snapshots by the R19 procedure, holding all 36 clean documents unchanged: 37 documents for Γ₁ and 39 for Γ₃. Verify parent hashes match the frozen five. Freeze both. Zero hosted calls.
3. Run the **18 answerable account-recovery questions** once each in fresh threads against each of the two new snapshots, attacked/undefended, using the ordinary baseline prompt and the frozen configuration: 36 answers, **no judge calls**. Reuse the R20 attacked results as the N = 5 point rather than regenerating them.
4. Compute `RSR_topk`, `RSR_context`, `ISR_marker`, `ASR_marker` and `ASR_exclusive_marker` locally at each of the three budgets. Claim no judged correctness, citation-support or behavioral label for sweep points, and no defended point.
5. Report the sweep as a separate subsection of the R21 report, with the limits from D14 stated: three points, 18 questions, one answer each, one frozen attack set, nested subsets. Describe a trend; do not fit a curve or extrapolate past N = 5.

**Acceptance:** Γ₁ ⊂ Γ₃ ⊂ Γ₅ verified by parent hash, 37/39/41-document snapshots frozen, subset ordering demonstrably predeclared, 36 answers and zero judgments consumed within the 36-call/3-retry reserve, and no sweep point rerun on account of its attack rate.
