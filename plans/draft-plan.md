# InjectRAG — replacement implementation draft

Date: 2026-09-13. Status: **draft; major design decisions pending**.

This plan supersedes the previous README implementation checklist and does not adopt the report's implementation phases as a binding plan. It uses the detailed report's research intent while reviewing its assumptions. The immediate deliverable is a functioning, inspectable **clean RAG target** that later attack and defense experiments can use without rewriting the application.

No application implementation is authorized by a pending recommendation. This change creates planning/documentation files only. See [status](../documentation/project-status.md), [decisions](../documentation/decisions.md), and [report review](../documentation/design-review.md).

## 1. Scope and completion definition

The first implementation must ingest synthetic helpdesk knowledge, normalize and chunk documents, embed and persist them, retrieve relevant chunks for a question, assemble a bounded model request, generate an answer, and save a trace linking the answer to its exact inputs. Establish clean-system quality and a reproducible frozen baseline before constructing attacks.

A small clean corpus belongs early in the build: ingestion and retrieval cannot be validated without representative inputs. Expand and freeze that corpus later. The first system is not complete merely because a chat response is returned.

Defer attack payload generation, attacker-side optimization, poisoning-budget sweeps, spotlighting, full security scoring, production ticket authentication, and deployment. D01 is accepted: the first working application includes an API and a simple chat UI. A CLI alone does not satisfy this scope. Preserve extension points for experiments without implementing those later systems prematurely.

## 2. Decisions before dependent work

| Gate | User input needed | Work that may proceed before resolution |
|---|---|---|
| D01: delivery | API + simple chat UI accepted; question-scoped memory accepted (D09); Python-served UI delivery pending | API/UI contract and task planning |
| D02: resources and stack | Local preferred on Linux laptop; exact models/runtime and feasibility resource limits pending | Hardware inventory recorded; compare candidates without assuming Iris acceleration |
| D03: packaging | One Python project accepted; framework/tooling details pending | Refine separate packages and shared contracts |
| D04: corpus | Initial topics, synthetic scope, resolved/submitted ticket admission | Corpus schema and authoring checklist |
| D05: baseline behavior | Prompt, citation/abstention policy, context treatment, history storage/budget and follow-up retrieval | Trace design and candidate policy review |
| D06: readiness | Corpus/query counts, split, quality/resource thresholds and repetitions | Metric definitions and scoring examples |

D01 and D03 are approved; D02 has an accepted local preference. D09 approves question-scoped memory. UI delivery and initial corpus questions remain pending. Bring D04–D06 as a focused follow-up before their tasks; do not turn them into silent defaults. D07/D08 concern later attack-study validity and do not block ordinary clean ingestion/retrieval.

## 3. Proposed organization

Use subdirectories to separate the target from experiments and data. With D03 approved, use the [proposed repository structure](../documentation/repository-structure.md): `src/injectrag/rag/` for victim logic, thin selected entry points, `evaluation/` for baseline scoring, and later `experiments/` and `attacks/` packages. Keep versioned inputs in `data/`, runtime choices in `configs/`, prompts in `prompts/`, and generated state in ignored `artifacts/`.

Create application directories only when their tasks start. Do not create a second deployable project unless a separately built interface or another concrete requirement justifies it and the user approves. Paths follow the approved single-Python-project direction; refine internal files as implementation requires.

## 4. Task dependency map

```text
R00 decisions → R01 feasibility → R02 scaffold → R03 contracts/config
R03 + D04 → R04 seed corpus → R05 ingestion → R06 chunking
R01 + R03 → R07 embeddings
R06 + R07 → R08 index → R09 retrieval
R03 + D05 + selected model limits → R10 context
R01 + R03 → R11 generation adapter
R03 → R12 trace infrastructure
R09 + R10 + R11 + R12 → R13 pipeline/entry point
R13 → R13a API → R13b chat UI → R14 integration hardening
R04 + D06 → R15 complete corpus/query set and scorer
R14 + R15 → R16 baseline pilot/freeze → R17 handoff
```

This is dependency information, not a request to spawn agents. Tasks can be implemented in dependency order by one implementation agent. Application tasks remain **not implemented**. R00 is in progress: D01/D03 accepted and D02 direction recorded; R01 has hardware inventory only, not a completed feasibility check.

## 5. Agent-executable tasks

### R00 — Resolve design gates and record approvals

**Prerequisites:** read the report review, draft architecture, and decision register.

1. Preserve the accepted D01/D03 answers and local D02 preference; resolve only remaining details, without re-asking approved choices.
2. Record constraints, selected direction, and any unresolved exact technology choice.
3. Present D04–D06 before dependent tasks, with concrete corpus/prompt/readiness options.
4. Create accepted decision records only for actual approvals; amend downstream paths and scope accordingly.

**Deliverables:** decision records and updated plan/status. **Acceptance:** an agent can identify which choices are approved and which tasks remain gated. **Stop condition:** do not scaffold an unapproved language or invoke an unapproved paid runtime.

### R01 — Establish resource feasibility and select the minimal runtime

**Prerequisites:** D02 direction and permission scope; D03 language direction.

1. Use the [hardware inventory](../documentation/local-runtime-feasibility.md), rechecking dynamic memory/disk before a pilot. Inspect runtime tooling without dumping credentials.
2. Compare a small set of local embedding, generation, indexing, and package-tool choices against those resources and the API/UI scope. Plan a CPU-compatible pilot; treat Iris acceleration as unverified until tested. Measure memory with browser, API, embeddings, and generator present, plus latency under a bounded request policy. Hosted fallback requires a new user decision.
3. Propose exact candidates, provisioning size, estimated cost, and a bounded pilot; obtain approval for major selections and resource use.
4. Run a tiny embedding batch and one grounded generation request under the approved setup; record observed latency, dimensions, context limits, and any provisioning failures.
5. Record exact versions/revisions and limitations. If infeasible, bring evidence and alternatives back before changing runtime strategy.

**Deliverables:** accepted D02 details, feasibility note in documentation, dependency/version inputs. **Acceptance:** at least one real embedding and generation path works within approved constraints; mocks are not feasibility evidence.

### R02 — Scaffold the approved project and development environment

**Prerequisites:** D01/D03 accepted; R01 runtime selection.

1. Create the minimal package/entry-point structure from the approved layout.
2. Add dependency declaration and selected lockfile; separate routine testing dependencies from optional live-model integrations where useful.
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

**Prerequisites:** R03, D04; agree seed scope within D06 or obtain a specific seed approval.

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

1. Define separate document-batch and query embedding operations to accommodate model-specific input conventions.
2. Implement the selected adapter with bounded batches, explicit error handling, and recorded model revision/dimension.
3. Validate finite vectors and dimensions; apply the approved normalization consistently.
4. If caching is needed, key by text hash, model revision, and embedding settings; otherwise defer caching.
5. Provide a deterministic fake adapter for routine tests and a marked real-runtime smoke check.

**Deliverables:** embedding interface/adapter and real smoke artifact. **Acceptance:** document/query vectors use compatible dimensions; changed model/settings cannot reuse incompatible cached data; failures do not masquerade as valid vectors.

### R08 — Build and reload isolated index snapshots

**Prerequisites:** R06/R07.

1. Implement the selected index adapter with explicit similarity metric and score meaning.
2. Build from a complete chunk manifest into temporary output, then publish a ready snapshot.
3. Persist vector-to-chunk mappings and the full compatibility manifest.
4. Load snapshots only after validating model, dimension, normalization, and corpus/preprocessing identities.
5. Support a clean rebuild without duplicate insertion or modification of a frozen prior snapshot.

**Deliverables:** index build/load operations and manifest. **Acceptance:** fresh versus reloaded rankings match on known-vector fixtures; interrupted/incompatible builds fail clearly; rebuilding does not change corpus membership unexpectedly.

### R09 — Implement inspectable retrieval

**Prerequisites:** R08 and query embedding adapter.

1. Embed a question using the approved query mode and retrieve configured top-k chunks.
2. Define score direction, ties, repeated-document policy, empty-index behavior, and top-k exceeding collection size.
3. Return typed ranked hits with chunk/document identity and text.
4. Expose a retrieval-only inspection command or equivalent approved interface.
5. Measure relevant-source presence on seed development questions; inspect misses without accessing held-out answers for tuning. Include elliptical follow-ups and specify/approve how retrieval uses thread context before adding rewriting or another retrieval-policy change.

**Deliverables:** retriever and inspection output. **Acceptance:** a known-vector test establishes ranking independently of the implementation; real seed queries produce traces that identify evidence and ranking without ground-truth-assisted selection.

### R10 — Implement baseline prompt and context construction

**Prerequisites:** R03, D05, selected model/token limits; use typed retrieval fixtures until R09 is ready.

1. Version the approved baseline system prompt and ordinary source rendering format.
2. Assemble trusted instructions, the current thread’s selected prior user/assistant turns, current question, and newly retrieved evidence in explicit provider roles; corpus text and prior answers cannot become system instructions.
3. Calculate the available input budget including selected history, formatting, query, output reserve, and margin. Implement the approved history limit/overflow policy and log included/omitted turn IDs.
4. Apply approved inclusion/exclusion policy in rank order; record exact included text and excluded IDs/reasons.
5. Define no-evidence and oversized-query behavior; reserve a narrow context-builder interface for later defenses.

**Deliverables:** prompt file, context builder, exact-message fixtures. **Acceptance:** boundary tests verify budget behavior and role separation; no experiment labels/answer key enter messages; emitted traces distinguish top-k retrieval from actual exposure.

### R11 — Implement generation with explicit operational outcomes

**Prerequisites:** R01/R03 and approved resource budget.

1. Implement the selected generation adapter behind a small request/result interface.
2. Pass resolved model, temperature, output cap, and supported reproducibility settings explicitly.
3. Capture response text, finish reason, available usage, latency, and reported model identity.
4. Implement bounded timeout/retry behavior and classify provider errors and truncated responses.
5. Use fake responses for default tests and a marked real-model request for integration validation.

**Deliverables:** adapter, error cases, live smoke evidence. **Acceptance:** a failure returns structured failure rather than an empty successful answer; retries obey limits; secrets do not enter logs; unavailable provider metadata is honestly labeled.

### R12 — Implement trace and run-manifest persistence

**Prerequisites:** R03; can use fixtures before full pipeline integration.

1. Create run/trial identifiers and immutable resolved manifest records.
2. Serialize stage timings, ranked hits, exact final messages, inclusion decisions, generation outcomes, and retry counts.
3. Link each trial to corpus/index/config/prompt/model/query identities.
4. Make partial/failed runs inspectable, and prevent accidental overwrite of prior results.
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

**Prerequisites:** R13, approved Python API framework and request concurrency policy.

1. Define versioned thread/turn/question/answer/error schemas with answer text, source references, and request ID; keep observer-only labels outside public responses. Implement thread creation/reset and isolated history using the agreed storage/retention policy.
2. Implement a question endpoint and readiness endpoint; readiness must distinguish an unbuilt index or unavailable model from a ready application.
3. Validate request size and shape before inference. Map operational failures into documented non-success HTTP responses.
4. Load/reuse runtime resources deliberately and apply the approved bounded concurrency/queue policy; do not duplicate model instances unintentionally per request or worker.
5. Document the endpoint contract and startup/shutdown behavior; test with deterministic adapters and a real local model under the approved pilot.

**Deliverables:** API package and `documentation/api.md`. **Acceptance:** an HTTP request traverses the real shared pipeline; invalid input, unavailable runtime, and overload have explicit outcomes; a slow generation does not prevent readiness checks. Measure memory and latency rather than assuming concurrent inference is feasible.

### R13b — Build and integrate the simple browser chat UI

**Prerequisites:** R13a; approved UI delivery and detailed history policy implementing D09.

1. Create an accessible question form, transcript, loading indicator, answer panel, and source references.
2. Call the API; prevent accidental duplicate submission, preserve the question on error, and show actionable failure/retry states.
3. Render model/source text safely as content. Link only through the approved source-link policy; do not interpret model text as executable HTML.
4. Keep follow-ups in the active question thread, supplying prior turns to the model through the API. Add “New question” to begin a fresh thread; do not carry old turns into it or infer topic changes automatically.
5. Verify keyboard submission/focus, narrow-screen layout, empty input, delayed answer, API failure, and successful source display in a browser. Document actual launch and usage steps.

**Deliverables:** integrated chat UI and browser validation record. **Acceptance:** a user can launch the documented app, ask a question in the browser, see an answer and sources, and recover from an error; the resulting trace identifies the same API request. Mocked UI checks alone do not satisfy the real RAG integration check.

### R14 — Validate end-to-end failure handling and isolation

**Prerequisites:** R13a/R13b.

1. Test missing/incompatible snapshot, empty input, no usable evidence, context overflow, provider failure, and trace-write failure.
2. Verify same-thread follow-ups receive the correct ordered history, while new questions and interleaved threads remain isolated. Test retries/failures without duplicate turns, history-budget overflow, and immutable index state.
3. Verify the victim package does not depend on attack/scoring modules or consume answer keys.
4. Execute default checks and the approved real-model smoke path on the seed corpus.
5. Fix failures and update the troubleshooting guide with observed issues only.

**Deliverables:** integration tests and validation record. **Acceptance:** failures are visible, bounded, and reproducible; successful runs have complete provenance; no silent fallback changes the selected model or experiment condition.

### R15 — Complete the clean corpus, query split, and baseline scorer

**Prerequisites:** R04, D06; scorer consumes R12 contracts.

1. Expand synthetic corpus and questions to approved counts and topic distribution using the canonical policy.
2. Review answer keys, document relevance, unsupported cases, and paraphrase-family split boundaries.
3. Implement clean retrieval relevance, marker containment, answer-rubric recording, and completion/failure reporting.
4. Test scoring with fabricated responses containing warnings, both markers, missing markers, paraphrases, and errors.
5. Freeze held-out evaluation inputs with hashes; keep them outside attacker-side development material and document the procedural limitation. Use fresh threads for independent trials and a separate scripted multi-turn set to test D09; freeze turn order and report those results separately.

**Deliverables:** reviewed corpus/query manifests, answer keys, baseline scorer and scoring examples. **Acceptance:** denominators and missing/failed cases are explicit; correctness is not silently equated with string containment; RAG receives only question text and ordinary evidence.

### R16 — Run development pilot, freeze, and measure the baseline

**Prerequisites:** R14/R15 and approved readiness/resource thresholds.

1. Run the full clean pipeline on development questions and approved repetitions.
2. Inspect retrieval misses, evidence truncation, wrong answers, unsupported answers, latency, resource use, and output variability.
3. Adjust only approved development parameters; seek approval for major design changes and record rationale.
4. Freeze resolved configuration, prompts, corpus, query set, model/dependency identities, and index manifest.
5. Execute the frozen held-out baseline, preserve all failures, and compare with D06 thresholds. Do not tune against this result while continuing to call it held-out.
6. Write `documentation/baseline-results.md` with counts, rates, limitations, and artifact links.

**Deliverables:** baseline bundle and measured readiness report. **Acceptance:** agreed thresholds pass with declared reproducibility limits, or M4 remains incomplete with a concrete diagnosis. No attack-success requirement applies to this milestone.

### R17 — Reproduction check and next-phase handoff

**Prerequisites:** R16 readiness passed.

1. Exercise documented setup/build/query/score instructions from a clean environment using the approved resources.
2. Check that committed inputs and manifests identify every required external dependency and model provisioning step.
3. Update README, architecture, status, contracts, and decisions to describe the actual implementation.
4. Publish an internal handoff note listing public pipeline interfaces, frozen baseline identifiers, observer trace fields, and remaining limitations.
5. Prepare the next detailed attack/defense plan, resolving D07/D08 before implementing those decisions.

**Deliverables:** verified reproduction guide and completed clean-target handoff. **Acceptance:** another implementation agent can run the baseline and diagnose an individual trial without undocumented manual edits or access to the original Downloads PDF.

## 6. Validation and completion recording

For each task, add a status entry containing task ID, implemented files, actual check commands/results, relevant artifact locations, remaining limitations, and next task. Use `not started`, `in progress`, `blocked by Dxx`, or `complete`; completion requires the stated acceptance evidence. No tests are run against nonexistent application code.

M1 corresponds to R08, M2 to R09, M3 to R14, and M4 to R17. A successful mock test satisfies plumbing checks only. Exact-match proxy scores and actual answer quality remain separately reported. See [testing](../documentation/testing-and-reproducibility.md) for validation layers.

## 7. Later research roadmap — deliberately not an attack implementation specification

After M4, resolve attacker knowledge/chunking and comparison-design questions. Then detail separate tasks for attacker-controlled ticket ingestion into derived snapshots, bounded attacker-side verification using only permitted information, frozen-query experiment orchestration, exposure-aware scoring, and spotlighting comparison with defended-clean utility runs.

Preserve the clean snapshot and normal victim configuration. Implement the same admission path for attacker content; keep experiment labels outside the victim. Include a cover-only control if approved and audit whether instruction spans and correct evidence actually reached generation. Any change to threat model, baseline prompts, budget construction, or scoring claims requires a documented decision.

The report's desired outcome is a hypothesis. A useful clean RAG that resists an attempted injection remains a valid target and result; do not weaken it to force the expected outcome.
