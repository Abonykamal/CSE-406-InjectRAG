# Project status

Last updated: 2026-09-17.

## Implemented and verified

- Repository initially contained a project README and local session metadata; no application, dependencies, corpus, or tests were present.
- Detailed report reviewed; replacement implementation draft and project documentation created.
- The old README implementation checklist is superseded by `plans/draft-plan.md`.

## Not implemented

No ingestion, chunking, embeddings, index, retrieval, generation, CLI/API/UI, attack tooling, scoring harness, or defense exists. No baseline or security measurements have been performed. Documentation checks do not establish application correctness.

## Current milestone

**Ready to start the clean-system build.** D01–D12 settle the core design; D13 and the plan provide rapid sequencing and routine starting defaults; D14 reconciles everything against the submitted report and adds the droppable R22 sweep. Attack/scoring choices gate their later tasks. Proposed file paths and command names are not existing functionality.

D01–D11 establish delivery, stack/models, corpus/readiness and the fixed five-ticket, three-condition study. [D12](decisions.md#d12) now records the accepted application policies, simple top-five retrieval without rewriting/reranking, retry policy and whole-study budget; [D14](decisions.md#d14) reconciles the documentation against the committed `design_report.pdf` and revises that budget to 347 planned calls, 28 extra retries and 375 attempts, within the unchanged 800 total API requests. Signed-cookie login, no editing/reopening, automatic publication, retained history without resume, explicit overflow and no waiting chat queue are settled. Implementation has not started. Account access/quotas, compatible pins and measured feasibility remain unverified; the user now directs rapid implementation, with this turn preparing the executable plan. Start Batch A local preflight/scaffolding; verify account access and counters before hosted calls.

D10 approves FastAPI/Uvicorn with one initial worker, a FastAPI-served HTML/CSS/JavaScript UI using fetch and complete responses, uv with pyproject.toml and a committed uv.lock, SQLite through Python sqlite3 for accounts/tickets/threads/turns, and local Qdrant for vectors and chunk metadata. Docker Compose runs two services: one custom application image and the existing Qdrant image, with separate persistent host mounts for application state, Qdrant data, snapshots/results, and model cache. Research commands use the application image as one-off jobs. No implementation or feasibility measurements are implied.

| Milestone | State | Exit evidence |
|---|---|---|
| M0: approve target-system design | Core direction ready | D01–D13; routine defaults and phased gates in the plan |
| M1: reproducible ingestion/index | Not started | Validated clean snapshot and rebuild checks |
| M2: inspectable retrieval | Not started | Retrieval traces on development questions |
| M3: complete clean RAG | Not started | One documented ingestion-to-answer run |
| M4: clean baseline and handoff | Not started | Frozen manifest, scored run, approved readiness thresholds |
| Attack/defense study | Planned as R18–R21 | Clean readiness, restricted attack freeze, shared snapshot and three-condition report |
| Budget sweep | Planned as R22, droppable | Nested Γ₁/Γ₃ snapshots verified by parent hash, 36 attacked-only answers, sweep reported separately |

## Blockers and risks

Routine starting defaults for SQLite/publication, visits, retry waits, chunking and size caps are in the plan under D13. Implement and verify them during their tasks; they are not blanket blockers. Exact API fields and prompt text are authored during implementation. D12 approved the six clean scripts at three turns each, once with per-turn judging; the plan assigns three development and three held-out scripts; contents remain to author before execution. Research details still open: exact attack target/marker, payload wording/topic allocation/repetition/placement/concealment, behavioral rubric and later audit scope. Account quotas, concrete pins/compatibility and measured feasibility still need evidence. The accepted budget does not allocate optional extensions or separate early smoke calls.

## Remaining review agenda

Application policy review is recorded in D12; do not reopen accepted login, no-resume/no-queue, retrieval or budget choices. Begin Batch A, then the clean vertical slice. R18–R22 already specify attack/defense implementation; settle their research gates without holding up the clean build. Explain metric interpretation where needed: actual context exposure versus raw retrieval, marker versus behavior, conditional ASR identity, zero-exposure ISR and concealment/repetition confounds. No extra experimental condition is required. M_a verification, rewriting and reranking are optional future work only.

## Change log

- 2026-09-18: added a browser helpdesk application over the demonstration pipeline (`src/injectrag/service.py`, `src/injectrag/api.py`, `web/`, `run_app.py`, `tools/test_app.py`), with live ticket-resolution poisoning and a defense toggle. `ChunkIndex` gained `add()`/`truncate()` and `Pipeline` gained `add_document()` so a ticket resolved at runtime becomes searchable without a rebuild; retrieval, chunking, the evidence budget and the baseline prompt are unchanged. The app starts on the 36 clean documents only -- attacker content enters exactly through submit-then-resolve. Verified in a real browser on the offline fake provider: clean answer with no exposure, resolving the frozen P01 payload published `W01` and grew the corpus to 37 documents / 38 chunks, re-asking put `W01` at rank 5 (score 0.6849) and the answer carried the marker, `spotlighting: boundary` left retrieval identical but removed the marker, and reset restored 36 documents. 65 offline checks in `tools/test_app.py` pass. Also corrected one pre-existing unsatisfiable assertion in `tools/smoke_test.py` (it tested for `" ^"`, but the data-marking token never follows whitespace); the data-marking behavior itself was already correct and is unchanged. In-memory only; no decision affected and no ADR entry added; demonstration track, not the R01-R22 clean system.

- 2026-09-17: verified the maintained documentation and plan against the submitted report, now committed as `design_report.pdf`. Corrected the report identity throughout: earlier text named an external `B1_Group_7.pdf` in a `Downloads` directory and cited section numbers from the longer unsubmitted draft, so no review item could be checked against a source a reader has. The design-review table is restated against the submitted report's real sections (§1–§6, Appendix A), with draft numbers kept in parentheses as history. Added a deviation register and a §4 implementation-phase mapping to the design review, a report-metric-to-implementation-metric mapping to the evaluation spec, and reconciliations for the report's unattributed plausibility screen (mapped to technician resolution) and its document-level `E(q; D)` notation (retrieval is chunk-level; budgets are document-level). Recorded [D14](decisions.md#d14): restore the §5.2 budget-scaling claim as droppable task R22 — attacked-only, N ∈ {1, 3, 5}, 18 target questions, nested subsets of the frozen five, 36 answers and zero judgments — raising the study budget to 347 planned calls, 28 retries, 375 attempts, 3,072,000 input and 849,920 output tokens within the unchanged 800-request ceiling; keep payload wording and the target marker pending rather than adopting Appendix A; keep tickets immutable and disclose that the implemented attacker is narrower than report §3.2's. Documentation only; no application code, corpus, model call or experiment exists.

- 2026-09-17: audited implementation readiness; removed the R01/scaffolding dependency cycle and duplicate unbudgeted smoke checks, added five delivery batches and R18–R21 attack/defense tasks, and recorded routine implementation defaults under D13. Application code remains unimplemented. Verified 120 local links/anchors across 16 maintained Markdown files, R00–R21 task coverage, unchanged budget arithmetic and scoped documentation whitespace checks.

Entries record decisions as they occurred; pending statements in older entries may have been resolved by later entries. The current summary and decision register govern current status.

- 2026-09-17: incorporated D12 application/retrieval/retry decisions and user approval of the whole-study budget across maintained docs and temporary plans. No application or experiment execution performed. Validated 112 local links/anchors across 16 maintained Markdown files, budget arithmetic, and scoped `git diff --check -- README.md documentation plans`. Repository-wide whitespace checks still flag pre-existing CRLF changes in untouched AGENTS/skill guidance files.

- 2026-09-17: approved D11 models (CPU BGE-small/FastEmbed/ONNX; Gemini 3.8 Flash answers/judging and 3.5 Flash-Lite rewriting), Python 3.12/google-genai, stable dependency/image/artifact pinning policy, and bounded pilot design. Stack/model selection is closed. Actual account access/quotas, compatibility/pins and measured feasibility remain unverified; application policies remain open. Updated both READMEs, onboarding, contracts, runtime, evaluation/testing guidance and the plan. No installs, downloads, scaffolding or live calls. Checked 92 local links/anchors across 16 maintained documents; link checks and git diff --check passed.

- 2026-09-17: approved D10 compact stack: FastAPI/Uvicorn (one initial worker), plain API-served UI with complete answers, uv/uv.lock, SQLite via sqlite3, and local Qdrant. Compose has two services, one custom application image and the Qdrant image, with persistent host mounts; research jobs reuse the application image. Updated affected documentation, both READMEs, and the plan. Exact models/versions, quotas, bounded pilot and application policies remain pending. Documentation-only approval; no provisioning or implementation. Validated 83 local links/anchors across 16 documents and passed git diff --check.

- 2026-09-16: reviewed the shortened submitted B1_Group_7.pdf (nine pages), which omits M_a verification and explicitly excludes attacker observation of the clean corpus in section 3.1. User selected M_a as optional future work only, resolving the restoration proposal without adding a blocker. Added an optional-extension list, distinguished submitted versus historical detailed-report references, and synchronized both READMEs and the plan. Checked 15 maintained documents and 65 local links/anchors; link checks and `git diff --check` passed. No implementation, models, or experiments started.

- 2026-09-16: approved one answer per held-out question per condition for the initial study: 30 clean, 30 attacked, and 30 defended outcomes; reuse clean results only with matching frozen configuration. Keep operational retries separate, retain unfavorable answers, and disclose variability limits. Updated 11 affected documents including both READMEs and the plan; 54 local links/anchors across 14 maintained documents and `git diff --check` passed. Recorded the report's bounded attacker-side M_a verification as a separate restoration proposal still awaiting approval. No implementation or experiments performed.

- 2026-09-16: approved restricted-brief attack authoring followed by frozen evaluation, without a surrogate or victim feedback during construction. Withhold corpus, victim internals, actual development/held-out questions and keys; retain authoring/freeze provenance and disclose same-team leakage. Updated 12 affected documents including both READMEs and the plan; checks across 14 maintained documents and 54 local links/anchors plus `git diff --check` passed. Exact payload/variant details and experiment repetitions remain pending. No implementation or experiments performed.

- 2026-09-16: approved one fixed five-ticket set with distinct support stories spanning all three recovery topics and a shared base instruction and target directive. Attack testing is primary; spotlighting is secondary. Exact payload text, topic allocation, repetition/placement/concealment, access, and experiment repetitions remain pending. Updated 12 affected documents including both READMEs and the plan; no payload authoring or implementation.

- 2026-09-16: approved fixed N = 5 admitted attacker tickets, with no budget sweep due to limited time. Clean/poisoned snapshots contain 36/41 documents. Exact attack-set composition, access procedure, variants, and repetitions remain pending; no scaling-with-budget claim is supported. Updated 12 affected documents, including both READMEs and the plan; checked 14 maintained documents and 54 local links/anchors, and passed `git diff --check`. Documentation only; no application or experiments started.

- 2026-09-16: reconciled both READMEs, decision summaries, architecture diagram, plan dependencies, and review status against session approvals. Preserved historical rationale and explicit open issues. Checked 14 maintained documents and 54 local links/anchors; link/anchor validation and `git diff --check` passed. Documentation-only checks do not establish application readiness.

- 2026-09-16: approved D08 three-condition scope: clean baseline, attacked baseline, defended attack. Defended-clean and cover-only runs are excluded for time; independent clean-defense utility and cover/instruction attribution claims are correspondingly limited.

- 2026-09-16: accepted D07 ordinary frozen chunking and observer-only instruction-integrity/exposure measurement. Repetition and placement are permitted attack-design dimensions using general chunking knowledge, without hidden victim-boundary feedback. Exact variants remain pending.

- 2026-09-16: approved D06 held-out readiness targets and five-question × three-repeat development pilot; initial full baseline runs use one answer/question. Exact judge, request/token/latency limits and retry settings remain pending. No readiness measurements performed.

- 2026-09-16: approved D06 initial scope: 12 articles + 24 resolved tickets; 30 development + 30 held-out questions with agreed category counts; six separate conversation scripts; initial 10-answer human audit plus flagged cases. Data remains unauthored; readiness thresholds and pilot limits remain pending.

- 2026-09-16: approved automated-first baseline scoring with model judging and a limited human audit to prioritize attack/defense work. Exact judge, audit size, numeric readiness gates, and dataset sizes remain pending. No live scoring performed.

- 2026-09-16: approved full-thread user/assistant history by default without routine trimming/summarization; fresh evidence precedes the current question at the end. Old retrieval bundles remain in artifacts. Overflow handling and storage/retention remain pending.

- 2026-09-16: approved explicitly logged original-question retrieval after rewrite failure. Retain stage errors and report fallback outcomes separately; exact retry/validation settings remain pending.

- 2026-09-16: accepted original-plus-rewritten retrieval for follow-ups and independently configurable rewrite provider/model. Exact second model/provider, fusion/history/failure policy, and quotas remain pending. Require rewrite-stage artifacts and conversational quality checks.

- 2026-09-16: accepted D05 separate labeled baseline evidence outside system instructions and later spotlighting as a combined untrusted-content formatting/handling-rule intervention. Exact syntax, history/retrieval policy, and budgets remain pending.

- 2026-09-16: revised D02 to Gemini hosted generation with local embeddings/retrieval and Docker delivery. Require replaceable generation adapters and retained sanitized trial requests/outputs/metadata. Free-tier capacity is unverified; paid usage is not approved. No implementation or API calls performed.

- 2026-09-16: accepted D05 grounded-answer behavior with supporting citations, explicit missing evidence, and clarification for ambiguity. Exact context/history policy remains pending. Hosted generation is under discussion; no provider or paid usage was selected.

- 2026-09-16: accepted seeded local accounts with API-enforced employee/technician roles; recorded Docker delivery expectation and inspected BUET-Job-Portal chatbot source. That reference uses local embeddings/Qdrant with hosted Groq generation; no runtime benchmark or provider change was made.

- 2026-09-16: recorded D04 scope approval and planned executable ticket submission/resolution plus preloaded resolved tickets. Workflow details remain pending; no application code created.

- 2026-09-14: added the repository-local `$orient` skill and root `AGENTS.md` startup instruction. Skill validation and local reference checks passed; automatic behavior in a separate new Codex session has not yet been exercised. Application implementation remains unchanged.

- 2026-09-13: recorded D09, remembering follow-ups within a question thread with a fresh thread for a new question; updated history, API/UI, testing, and evaluation requirements.

- 2026-09-13: consolidated decision records and pending choices into `documentation/decisions.md` at the user’s request; preserved IDs, approval state, and rationale.

- 2026-09-13: recorded user approval of API + simple chat UI and one Python project; recorded local-model preference and read-only hardware inventory. Expanded plan with API and browser UI tasks. No models downloaded or application code created.

- 2026-09-13: replaced the high-level implementation checklist with a RAG-first draft; added architecture, contracts, repository, evaluation, testing, workflow, and decision documentation. No software results claimed.
