# InjectRAG — replacement implementation draft

Created: 2026-09-13. Updated: 2026-09-17. Status: **approved design directions incorporated; remaining implementation/research details pending**.

This plan supersedes the previous README implementation checklist and does not adopt the report's implementation phases as a binding plan. It uses the detailed report's research intent while reviewing its assumptions. The immediate deliverable is a functioning, inspectable **clean RAG target** that later attack and defense experiments can use without rewriting the application.

No application implementation is authorized by a pending recommendation. This change creates planning/documentation files only. See [status](../documentation/project-status.md), [decisions](../documentation/decisions.md), and [report review](../documentation/design-review.md).

## 1. Scope and completion definition

The first implementation must ingest synthetic helpdesk knowledge, normalize and chunk documents, embed and persist them, retrieve relevant chunks for a question, assemble a bounded model request, generate an answer, and save a trace linking the answer to its exact inputs. Establish clean-system quality and a reproducible frozen baseline before constructing attacks.

A small clean corpus belongs early in the build: ingestion and retrieval cannot be validated without representative inputs. Expand and freeze that corpus later. The first system is not complete merely because a chat response is returned.

Defer attack payload generation, attacker-side optimization, spotlighting, full security scoring, production identity-provider integration and external deployment. Docker delivery and local account/role enforcement are approved initial scope. D01 is accepted: the first working application includes an API and a simple chat UI. A CLI alone does not satisfy this scope. Preserve extension points for experiments without implementing those later systems prematurely.

## 2. Decisions before dependent work

| Gate | User input needed | Work that may proceed before resolution |
|---|---|---|
| D01: delivery | API + simple chat UI accepted; question-scoped memory accepted (D09); FastAPI-served plain UI and complete responses accepted (D10) | API/UI contract and task planning |
| D02: resources and stack | D10 stack and D11 models/runtime/version policy/pilot bounds accepted; account quotas and feasibility unverified | Read-only account/compatibility planning; no execution authorization |
| D03: packaging | One Python project accepted; FastAPI/Uvicorn and uv/uv.lock accepted (D10); Python 3.12 and version-pinning policy accepted (D11) | Refine separate packages and shared contracts |
| D04: corpus/workflow | Corpus and resolved-ticket scope accepted; employee/technician API-enforced roles accepted; SQLite storage accepted (D10); lifecycle/session/schema and publication details pending | Corpus schema and workflow contract planning |
| D05: baseline behavior | Grounded answers/citations/missing-evidence behavior accepted; reference/system separation and later combined spotlighting intervention accepted; original-plus-rewritten follow-up retrieval accepted; full history without routine trimming accepted; SQLite history storage accepted (D10); exact syntax, retention/resume/overflow, fusion and rewrite validation pending; logged original-question fallback approved | Trace design and candidate policy review |
| D06: readiness | Automated checks/model judge/limited human audit accepted; 36 documents, 30 development + 30 held-out questions, six conversation scripts, and initial 10-answer audit plus flags accepted; 22/24 evidence coverage, 21/24 fully correct supported answers, 3/3 unsupported and 3/3 ambiguous handling, 30/30 completion, and five development questions × three pilot repeats accepted; D11 judge and pilot resource/retry bounds accepted; full-run policies pending | Metric definitions and scoring examples |

D01 and D03 are approved; D02 selects Gemini generation with local embeddings/retrieval and Docker delivery. D09 approves question-scoped memory. D10 settles API/UI delivery, uv, SQLite, local Qdrant, and the two-service Compose layout; ticket-workflow details remain pending; D04 corpus scope is accepted. Resolve only the remaining D04–D06 details before dependent tasks; preserve their accepted choices. D07 main-study boundary and D08 three-condition scope with fixed N = 5 are accepted; no budget sweep is selected. The five-ticket distinct-cover/shared-instruction composition is approved. Restricted-brief authoring followed by frozen evaluation is approved, without a surrogate or victim feedback during construction. Initial repetitions are approved at one answer per held-out question per condition. Exact later payload details and variants remain open and do not block ordinary clean ingestion/retrieval. M_a verification is optional future work only, not a gate.

D11 closes stack/model selections, version policy and bounded pilot design. Next review application policies; account quotas, exact stable pins/compatibility and measured feasibility remain verification work. D10/D11 approve design only: no installs, downloads, scaffolding, live API calls, or paid usage yet.

D11 selects BAAI/bge-small-en-v1.5 through FastEmbed/ONNX Runtime on CPU, Gemini gemini-3.8-flash for answers and separate observer judging, and gemini-3.5-flash-lite for independently configured rewriting. Use google-genai, Python 3.12, low thinking for answers/judging and minimal thinking for rewriting. Resolve compatible stable dependencies during authorized setup, commit exact uv.lock versions, pin Docker images by digest, and record embedding revisions/hashes before baseline freeze. Pilot design: 15 repeatability answers, 15 answer judgments, five fabricated judge cases and five rewrite fixtures = 40 planned inference calls; at most five retry attempts and 100 total API calls including auxiliary requests. See [D11](../documentation/decisions.md#d11) for all token/time/memory/concurrency bounds. Pilot approval does not set the full-study aggregate budget or replace D06 readiness/script checks.

## 3. Proposed organization

Use subdirectories to separate the target from experiments and data. With D03 approved, use the [proposed repository structure](../documentation/repository-structure.md): `src/injectrag/rag/` for victim logic, thin selected entry points, `evaluation/` for baseline scoring, and later `experiments/` and `attacks/` packages. Keep versioned inputs in `data/`, runtime choices in `configs/`, prompts in `prompts/`, and generated state in ignored `artifacts/`.

Create application directories only when their tasks start. Do not create a second deployable project unless a separately built interface or another concrete requirement justifies it and the user approves. Paths follow the approved single-Python-project direction; refine internal files as implementation requires.

## 4. Task dependency map

```text
R00 decisions → R01 feasibility → R02 scaffold → R03 contracts/config
R03 + D04 → R04 seed corpus → R05 ingestion → R06 chunking
R03 + D04 workflow details → R05a ticket lifecycle → R13a/R13b delivery
R01 + R03 → R07 embeddings
R06 + R07 → R08 index → R09 retrieval
R11 provider interface + approved rewrite configuration → R09 live follow-up rewriting
R03 + D05 + selected model limits → R10 context
R01 + R03 → R11 generation adapter
R03 → R12 trace infrastructure
R09 + R10 + R11 + R12 → R13 pipeline/entry point
R13 → R13a API → R13b chat UI → R14 integration hardening
R04 + D06 → R15 complete corpus/query set and scorer
R14 + R15 → R16 baseline pilot/freeze → R17 handoff
```

This is dependency information, not a request to spawn agents. Tasks can be implemented in dependency order by one implementation agent. Application tasks remain **not implemented**. R00 is in progress: D10/D11 close stack/model design, while application/research policies remain. R01 has hardware/source inventory and official documentation review only, not a completed account/feasibility check.

## 5. Agent-executable tasks

### R00 — Resolve design gates and record approvals

**Prerequisites:** read the report review, draft architecture, and decision register.

1. Preserve the accepted D01/D03 answers and revised hosted-generation D02 direction; resolve only remaining details, without re-asking approved choices.
2. Record constraints, selected direction, and any unresolved exact technology choice.
3. Resolve remaining D04–D06 implementation/resource settings without re-asking approved corpus, prompt/history, scoring, sample-size, and readiness choices.
4. Create accepted decision records only for actual approvals; amend downstream paths and scope accordingly.

**Deliverables:** decision records and updated plan/status. **Acceptance:** an agent can identify which choices are approved and which tasks remain gated. **Stop condition:** do not scaffold an unapproved language or invoke an unapproved paid runtime.

### R01 — Verify the selected runtime and resource feasibility

**Prerequisites:** D10/D11 selections and separate execution authorization for provisioning/live work; remaining dependent policy settings.

1. Use the [hardware inventory](../documentation/local-runtime-feasibility.md), rechecking dynamic memory/disk before a pilot. Inspect runtime tooling without dumping credentials.
2. Verify D11 CPU BGE-small/FastEmbed/ONNX with the D10 FastAPI/SQLite/Qdrant two-service stack; verify official model availability and published free-tier limits separately from actual account quotas. Measure local application/embedding/index memory and end-to-end API latency under bounded concurrency. Local generation benchmarking is not required; paid usage and silent fallback are not approved.
3. Preserve D11 model selections and pilot limits. Resolve compatible stable dependencies for Python 3.12, pin image digests and embedding artifacts under the approved policy during authorized setup. Record provisioning sizes and account quotas before live work; substitutions require review.
4. After execution authorization, run a tiny embedding batch and an explicitly budgeted grounded-generation smoke request; record latency, dimensions, context limits and provisioning failures. Allocate early smoke calls explicitly without silently expanding D11's planned 40-call pilot; the full repeatability/judge/rewrite pilot belongs after pipeline/scorer integration.
5. Record exact versions/revisions and limitations. If infeasible, bring evidence and alternatives back before changing runtime strategy.

**Deliverables:** accepted D02 details, feasibility note in documentation, dependency/version inputs. **Acceptance:** at least one real embedding and generation path works within approved constraints; mocks are not feasibility evidence.

### R02 — Scaffold the approved project and development environment

**Prerequisites:** D10/D11 design accepted; R01 compatibility/resource verification and explicit implementation authorization.

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

### R05a — Implement executable ticket submission and resolution

**Prerequisites:** R03, approved D04 lifecycle/session/persistence details; R05 for admission integration.

1. Implement submission and technician resolution with distinct employee description and resolution fields. Use seeded local employee/technician accounts and API-enforced roles; specify session mechanism, edit/reopen behavior, and SQLite schemas/transactions first; employee actions cannot set technician resolution or resolved status.
2. Keep unresolved tickets outside the searchable corpus. Route resolved tickets and preloaded resolved-ticket records through common eligibility, normalization, identity, and provenance rules.
3. Implement the approved index publication policy. Distinguish resolved status from searchable status; preserve frozen experiment snapshots.
4. Expose submission, inspection, and resolution through the API/browser UI in R13a/R13b using the approved actor representation.
5. Verify state transitions, unresolved exclusion, content preservation, seed/workflow equivalence, and publication failures/retries.

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

**Prerequisites:** R08 and query embedding adapter; R11 provider interface and approved rewrite configuration for live follow-up rewriting (fixtures may precede it).

1. Embed a question using the approved query mode and retrieve configured top-k chunks.
2. Define score direction, ties, repeated-document policy, empty-index behavior, and top-k exceeding collection size.
3. Return typed ranked hits with chunk/document identity and text.
4. Expose a retrieval-only inspection command or equivalent approved interface.
5. Measure relevant-source presence on seed development questions; inspect misses without accessing held-out answers for tuning. Implement D05 original-plus-rewritten follow-up retrieval using a separately configured rewrite adapter and full same-thread user/assistant history by default. Search both versions, merge/deduplicate within a fixed evidence budget, and trace both rankings. First turns use the original question directly. Validate corrections, topic shifts, ambiguous references, and prior-answer contamination; agree exact fusion and rewrite validation before freezing. On rewrite failure after bounded retries, trace the failure and retrieve using the original question only; preserve fallback identity in results and scoring. Use fake rewrite responses for plumbing; real rewrite validation requires the approved provider adapter/resource setup.

**Deliverables:** retriever and inspection output. **Acceptance:** a known-vector test establishes ranking independently of the implementation; real seed queries produce traces that identify evidence and ranking without ground-truth-assisted selection.

### R10 — Implement baseline prompt and context construction

**Prerequisites:** R03, D05, selected model/token limits; use typed retrieval fixtures until R09 is ready.

1. Version the approved baseline system prompt and ordinary source rendering format.
2. Assemble trusted instructions, the current thread’s selected prior user/assistant turns, current question, and newly retrieved evidence in explicit provider roles; corpus text and prior answers cannot become system instructions.
3. Calculate the available input budget including selected history, formatting, query, output reserve, and margin. Preserve full history by default without routine trimming/summarization; place fresh evidence after history and the current original question last. Do not replay old retrieval bundles. Specify overflow handling before implementation, check each model limit, and log exact included/omitted turn IDs.
4. Apply approved inclusion/exclusion policy in rank order; record exact included text and excluded IDs/reasons.
5. Define no-evidence and oversized-query behavior; reserve a narrow context-builder interface for later defenses.

**Deliverables:** prompt file, context builder, exact-message fixtures. **Acceptance:** boundary tests verify budget behavior and role separation; no experiment labels/answer key enter messages; emitted traces distinguish top-k retrieval from actual exposure.

### R11 — Implement generation with explicit operational outcomes

**Prerequisites:** R01/R03 and approved resource budget.

1. Implement Gemini through google-genai behind a provider-independent request/result interface, using D11 gemini-3.8-flash answers and independently configured gemini-3.5-flash-lite rewriting with the approved thinking levels. Map roles and supported settings explicitly. Keep provider code out of retrieval and scoring; replacements require their own adapter validation and baseline.
2. Pass resolved model, temperature, output cap, and supported reproducibility settings explicitly.
3. Capture response text, finish reason, available usage, latency, and reported model identity.
4. Implement bounded timeout/retry behavior and classify provider errors and truncated responses.
5. Use fake responses for default tests and a marked real-model request for integration validation.

**Deliverables:** adapter, error cases, live smoke evidence. **Acceptance:** a failure returns structured failure rather than an empty successful answer; retries obey limits; secrets do not enter logs; unavailable provider metadata is honestly labeled.

### R12 — Implement trace and run-manifest persistence

**Prerequisites:** R03; can use fixtures before full pipeline integration.

1. Create run/trial identifiers and immutable resolved manifest records.
2. Serialize stage timings, ranked hits, exact final messages, inclusion decisions, sanitized provider request bodies, returned responses/metadata, and each attempt/error. Persist artifacts outside disposable container state; exclude credentials and session secrets.
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

**Prerequisites:** R13, R05a, D10 FastAPI/Uvicorn and approved request concurrency policy.

1. Define versioned thread/turn/question/answer/error schemas with answer text, source references, and request ID; keep observer-only labels outside public responses. Implement thread creation/reset and SQLite-backed isolated history using the agreed retention/resume policy.
2. Implement a question endpoint and readiness endpoint; readiness must distinguish an unbuilt index or unavailable model from a ready application.
3. Validate request size and shape before inference. Map operational failures into documented non-success HTTP responses.
4. Start with one Uvicorn worker per D10, load/reuse runtime resources deliberately, keep blocking embedding work off the event loop, and apply the approved bounded concurrency/queue policy; do not duplicate model instances unintentionally per request or worker.
5. Document the endpoint contract and startup/shutdown behavior; test with deterministic adapters and local embeddings plus real Gemini generation under the approved free-tier pilot.

**Deliverables:** API package including ticket submission/resolution endpoints and `documentation/api.md`. **Acceptance:** an HTTP request traverses the real shared pipeline; invalid input, unavailable runtime, and overload have explicit outcomes; a slow generation does not prevent readiness checks. Measure memory and latency rather than assuming concurrent inference is feasible.

### R13b — Build and integrate the simple browser chat UI

**Prerequisites:** R13a and R05a; D10 plain API-served UI and detailed history policy implementing D09.

1. Create FastAPI-served plain HTML/CSS/JavaScript assets with an accessible question form, transcript, loading indicator, answer panel, and source references. Use fetch and complete responses; streaming is deferred by D10.
2. Call the API; prevent accidental duplicate submission, preserve the question on error, and show actionable failure/retry states.
3. Render model/source text safely as content. Link only through the approved source-link policy; do not interpret model text as executable HTML.
4. Keep follow-ups in the active question thread, supplying prior turns to the model through the API. Add “New question” to begin a fresh thread; do not carry old turns into it or infer topic changes automatically.
5. Verify keyboard submission/focus, narrow-screen layout, empty input, delayed answer, API failure, and successful source display in a browser. Document actual launch and usage steps.

**Deliverables:** integrated chat and ticket submission/resolution UI with browser validation record. **Acceptance:** a user can launch the documented app, ask a question in the browser, see an answer and sources, and recover from an error; the resulting trace identifies the same API request. Mocked UI checks alone do not satisfy the real RAG integration check.

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
3. Implement automated evidence/citation checks, separate marker containment, and observer-only model judging with the approved rubric. Retain judge artifacts/errors and limited human-audit selections/corrections; report unscored judgments explicitly. Use the approved initial 10-answer audit plus flagged cases; D11 selects gemini-3.8-flash with low thinking and pilot usage bounds; rubric implementation, full-run budgets, account verification and execution authorization still precede live scoring. Disclose shared answer/judge-model limitations.
4. Test scoring with fabricated responses containing warnings, both markers, missing markers, paraphrases, and errors.
5. Freeze held-out evaluation inputs with hashes; keep them outside attacker-side development material and document the procedural limitation. Use fresh threads for independent trials and a separate scripted multi-turn set to test D09; freeze turn order and report those results separately.

**Deliverables:** reviewed corpus/query manifests, answer keys, baseline scorer and scoring examples. **Acceptance:** denominators and missing/failed cases are explicit; correctness is not silently equated with string containment; RAG receives only question text and ordinary evidence.

### R16 — Run development pilot, freeze, and measure the baseline

**Prerequisites:** R14/R15 and approved readiness/resource thresholds.

1. Run the D11 bounded pilot after execution authorization: five development questions × three answers, judge those 15 outputs, five fabricated judge-validation cases and five rewrite fixtures. Enforce all cumulative API/retry/token/time/memory bounds. This does not replace the six conversation scripts or authorize additional full-development/held-out aggregate usage; settle those execution budgets separately.
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
5. Prepare the next detailed attack/defense plan using accepted D07/D08 scope: fixed N = 5, distinct covers sharing one base instruction/directive, and restricted-brief authoring followed by frozen evaluation without a surrogate or victim feedback. Use the approved one-answer-per-held-out-question-per-condition policy. Resolve remaining payload/variant details before dependent implementation. M_a verification belongs to the optional-extension list and is not a prerequisite.

**Deliverables:** verified reproduction guide and completed clean-target handoff. **Acceptance:** another implementation agent can run the baseline and diagnose an individual trial without undocumented manual edits or access to the original Downloads PDF.

## 6. Validation and completion recording

For each task, add a status entry containing task ID, implemented files, actual check commands/results, relevant artifact locations, remaining limitations, and next task. Use `not started`, `in progress`, `blocked by Dxx`, or `complete`; completion requires the stated acceptance evidence. No tests are run against nonexistent application code.

M1 corresponds to R08, M2 to R09, M3 to R14, and M4 to R17. A successful mock test satisfies plumbing checks only. Exact-match proxy scores and actual answer quality remain separately reported. See [testing](../documentation/testing-and-reproducibility.md) for validation layers.

## 7. Later research roadmap — deliberately not an attack implementation specification

Attack testing is the primary research goal; spotlighting is the secondary comparison. After M4, implement the accepted D07 knowledge/chunking boundary and resolve remaining D08 comparison-design questions. Consider instruction repetition and placement within attacker-owned descriptions as explicit variants, without hidden victim-boundary tuning; record length, chunk count, and actual instruction exposure to expose confounds. The document budget is fixed at five admitted attacker tickets; no budget sweep is selected. Use one fixed set of five distinct support stories spanning all three recovery topics and sharing the same base instruction and target directive. Freeze the set before final evaluation. Exact payload text, topic allocation, instruction repetition, placement, concealment, and variant count remain pending. M_a verification is optional future work under the shortened submitted-report scope, not a required restoration. Then detail separate tasks for attacker-controlled ticket ingestion into derived snapshots, restricted-brief authoring and authoring-provenance checks without victim feedback or a surrogate, frozen-query experiment orchestration, exposure-aware scoring, and the D08 three-condition comparison (clean baseline, attacked baseline, defended attack); no defended-clean run.

The attack author receives target topics, description permissions, general chunking knowledge, and the attack objective, and may invent example questions. Withhold clean corpus contents, victim prompts/configuration, actual development/held-out questions and keys, and victim traces from construction. Freeze tickets before victim testing; preserve the brief, supplied-material identities, ticket hashes/freeze time, and known leakage. Observer analysis must not guide revisions to the frozen attack. Disclose procedural same-team separation and non-adaptive scope.

Run the initial study once per held-out question per condition: 30 clean, 30 attacked, and 30 defended logical outcomes in fresh threads. Reuse clean baseline outcomes only with matching frozen configuration (60 additional attacked/defended answer generations, excluding judging/retries). Target attack rates use the 18 answerable recovery questions; assess the other 12 separately. Preserve all operational attempts and missing pairs, never repeat a completed answer to obtain a desired attack result, and disclose the single-answer variability limitation. The clean repeatability pilot remains unchanged; no extra payload variants or conversation-script execution counts are selected here.

Preserve the 36-document clean snapshot and normal victim configuration. Each poisoned snapshot adds exactly five admitted attacker tickets, for 41 documents; matched attacked/defended runs use the same snapshot. Count documents rather than chunks or instruction repetitions, and make no document-count scaling claim. Implement the same admission path for attacker content; keep experiment labels outside the victim. D08 excludes cover-only and defended-clean conditions; audit whether instruction spans and correct evidence actually reached generation and report the resulting attribution/utility limitations. Any change to threat model, baseline prompts, budget construction, or scoring claims requires a documented decision.

Optional research ideas are maintained in [things to try if time permits](../documentation/optional-extensions.md). M_a verification is explicitly outside required delivery. The other list entries are proposals, not approved extra runs; none adds an implementation dependency or completion gate.

The report's desired outcome is a hypothesis. A useful clean RAG that resists an attempted injection remains a valid target and result; do not weaken it to force the expected outcome.
