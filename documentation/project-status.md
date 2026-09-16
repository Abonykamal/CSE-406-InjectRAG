# Project status

Last updated: 2026-09-17.

## Implemented and verified

- Repository initially contained a project README and local session metadata; no application, dependencies, corpus, or tests were present.
- Detailed report reviewed; replacement implementation draft and project documentation created.
- The old README implementation checklist is superseded by `plans/draft-plan.md`.

## Not implemented

No ingestion, chunking, embeddings, index, retrieval, generation, CLI/API/UI, attack tooling, scoring harness, or defense exists. No baseline or security measurements have been performed. Documentation checks do not establish application correctness.

## Current milestone

**M0 — design clarification and approval.** Main directions have been approved in the [decision register](decisions.md); implementation settings and remaining research-design details are still pending. Proposed file paths and command names are not existing functionality.

D01 (API + simple chat UI) and D03 (one Python project) are accepted. D02 now approves Gemini API generation, local embeddings/retrieval, Docker delivery, provider replaceability, and persistent trial artifacts; D11 now selects models and pilot limits, with actual account quotas and feasibility unverified. D09 approves question-scoped conversation memory. D04 approves synthetic articles/resolved tickets, account-access recovery, and executable ticket submission/resolution with preloaded tickets. D05 approves full history, grounded answers and original-plus-rewritten retrieval with fallback; D06 approves dataset/audit sizes and readiness targets. D08 fixes the attack budget at five admitted tickets, without a budget sweep. Its approved composition is five distinct stories spanning the three recovery topics with one shared base instruction and target directive. Attack testing is primary; spotlighting is secondary. Restricted-brief authoring followed by frozen evaluation is approved, without a surrogate or victim feedback during construction. Initial study repetitions are approved at one answer per held-out question per condition. M_a verification is optional future work under the shortened submitted-report scope, not a blocker. D10 now approves the application stack (below). D11 closes stack/model selections, version policy and pilot design. Next: application policies (ticket lifecycle/sessions/publication, history retention/resume/overflow, retrieval fusion and validation). Account model access/free-tier quotas, compatible pins, and measured feasibility remain verification tasks before live work; no implementation is authorized yet. Do not install a stack, select a paid provider, or create an application skeleton on the strength of a recommendation alone.

D10 approves FastAPI/Uvicorn with one initial worker, a FastAPI-served HTML/CSS/JavaScript UI using fetch and complete responses, uv with pyproject.toml and a committed uv.lock, SQLite through Python sqlite3 for accounts/tickets/threads/turns, and local Qdrant for vectors and chunk metadata. Docker Compose runs two services: one custom application image and the existing Qdrant image, with separate persistent host mounts for application state, Qdrant data, snapshots/results, and model cache. Research commands use the application image as one-off jobs. No implementation or feasibility measurements are implied.

| Milestone | State | Exit evidence |
|---|---|---|
| M0: approve target-system design | Pending user decisions | Accepted decision records and concrete feasibility scope |
| M1: reproducible ingestion/index | Not started | Validated clean snapshot and rebuild checks |
| M2: inspectable retrieval | Not started | Retrieval traces on development questions |
| M3: complete clean RAG | Not started | One documented ingestion-to-answer run |
| M4: clean baseline and handoff | Not started | Frozen manifest, scored run, approved readiness thresholds |
| Later: attack/defense study | Deferred | Separate detailed plan after M4 |

## Blockers and risks

API + simple chat UI and one Python project are approved. D10 selects API/UI architecture, uv, SQLite and Qdrant storage, and Docker layout. D11 selects models/runtime/version policy and pilot ceilings. Account access/quotas, concrete pins/compatibility and measured feasibility remain unverified. History retention/resume/overflow, rewrite validation/fusion, ticket lifecycle/session/schema/publication, prompt rendering and evidence limits, and full-run aggregate budgets/queue/retry-policy details beyond the pilot bounds remain pending. D06 quality thresholds and initial sample sizes/repeats are approved; D11 selects the judge, while rubric implementation and conversation-script execution details remain open. These block dependent implementation, not documentation work. D07 resolves chunk integrity through ordinary frozen chunking and observer-only measurement; attacker repetition/placement using general chunking knowledge is allowed. D08 approves only clean baseline, attacked baseline, and defended attack; N = 5 is fixed with no budget sweep; the distinct-cover/shared-instruction composition is approved; restricted-brief authoring and frozen evaluation are approved; initial repetitions are one answer per held-out question per condition; exact payload details and variants remain pending, and M_a verification is optional future work, not a blocker. See [design review](design-review.md).

## Remaining review agenda

The first decision-review pass is substantially complete, but the full agenda is not closed. D08 fixes N = 5 and approves five distinct covers spanning the three recovery topics with a shared base instruction and directive. Restricted-brief authoring followed by frozen evaluation resolves the attacker access procedure, without a surrogate or victim feedback during construction. Initial repetitions are approved: one answer for each of the 30 held-out questions in each of the three conditions. Exact payload/variant details remain pending; the M_a restoration proposal is resolved as optional future work only, listed in [things to try if time permits](optional-extensions.md); nested budget sets and scaling comparisons are no longer needed. The design-review probability identity, zero-exposure case, marker-versus-behavior interpretation, and concealment confounds still need a focused explanation; recorded technical proposals are not evidence that the user reviewed each one. D10/D11 close stack/model selection, version policy and pilot design. Continue application policies and remaining research explanations in manageable batches; do not reopen accepted selections. Verification of account quotas, exact pins/compatibility and actual feasibility remains outstanding. No additional experimental condition is required by this remaining work.

## Change log

Entries record decisions as they occurred; pending statements in older entries may have been resolved by later entries. The current summary and decision register govern current status.

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
