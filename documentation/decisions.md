# Architecture decision log

**Pending means not approved.** D01–D11 establish the accepted base design. [D12](#d12) records the subsequent application/retrieval/retry choices and the user-approved whole-study budget. D12 supersedes earlier required rewriting/fusion, unresolved application-policy statements and the original 40-call/45-attempt pilot. [D13](#d13) records the subsequent implementation direction and routine starting defaults. [D14](#d14) reconciles the maintained documentation against the committed [`design_report.pdf`](../design_report.pdf) and revises the aggregate budget for a minimal budget sweep. Historical entries below retain their original rationale; the current table and D12–D14 govern implementation. Account verification, measured feasibility and remaining research details are still outstanding.

| ID | Major decision | Proposal / alternatives | Status | Blocks |
|---|---|---|---|---|
| [D01](#d01) | First application interface | API plus simple chat UI from the start | Accepted | UI delivery selected in D10; question-scoped memory accepted in D09 |
| [D02](#d02) | Models, hardware, cost, execution | Gemini API generation through a replaceable provider adapter; Docker delivery; local embeddings/retrieval; retained trial artifacts | D10 stack and D11 models/pilot design accepted | Account quota, compatibility and measured feasibility verification |
| [D03](#d03) | Language and project layout | One Python project with separate RAG, experiment, and evaluation packages and shared contracts/configuration | Accepted | FastAPI/uv in D10; Python 3.12 and version-pinning policy in D11 |
| [D04](#d04) | Corpus and ticket admission | Synthetic articles and resolved tickets; executable workflow | Accepted; lifecycle/login/publication resolved by D12 | Implement/verify D13 schema and publication defaults |
| [D05](#d05) | Grounded answers and context | Full history, citations, missing-evidence handling; D12 current-question top-five retrieval | Accepted; original rewrite/fusion superseded by D12 | Prompt syntax and clean validation |
| [D06](#d06) | Clean readiness and scoring | 36 documents, 30+30 questions, six scripts, limited audit and readiness gates | Accepted; full budget/script execution bounds in D12 | Rubric/script authoring and actual M4 evidence |
| [D07](#d07) | Attacker knowledge versus chunk integrity | Ordinary frozen victim chunking; observer-only integrity measurement; repetition/placement allowed using general chunking knowledge | Main-study approach accepted; exact variants pending | Later attack construction and exposure annotations |
| [D08](#d08) | Controlled comparison design | Clean baseline, attacked baseline, defended attack; fixed N = 5 attacker tickets; no defended-clean or cover-only condition; sweep exclusion partly superseded by [D14](#d14) | Conditions, document budget, composition, authoring/access procedure, and initial repetitions accepted; exact payload details pending; attacker-side verification optional, not a blocker | Attack/defense experimental plan |
| [D09](#d09) | Conversation memory | Full active-thread history; fresh New question | Accepted; retention/no-resume/overflow in D12 | Implement/verify D13 visit default and API checks |
| [D10](#d10) | Stack and storage | FastAPI/plain UI, uv, SQLite, local Qdrant; two services | Accepted; policies in D12 | Setup and compatibility evidence |
| [D11](#d11) | Models and version policy | CPU BGE-small, Gemini 3.8 Flash answer/judge, Python 3.12 | Accepted; rewrite removed and pilot revised by D12 | Account access, pins and feasibility evidence |
| [D12](#d12) | Application policies, retrieval and study budget | No edits/reopen/resume/queue; signed cookie; top five; bounded retries; 311 calls/336 attempts | Accepted | D13 starting settings; implementation not started |
| [D13](#d13) | Rapid implementation sequence | Begin clean build; budgeted integration checks; R18–R21 attack/defense tasks | Direction accepted; defaults recorded as implementer choices | Live account checks and remaining attack/scoring gates |
| [D14](#d14) | Submitted-report reconciliation and minimal budget sweep | Restore §5.2 scaling with an attacked-only nested sweep at N ∈ {1, 3, 5}; keep payload pending; disclose the ticket-immutability narrowing | Accepted | R22 runs only after R20/R21 complete |

## Logging convention

Keep all architecture decision records (ADRs) in this file. Add dated entries with a stable ID, status, context, options/rationale, decision, consequences, and verification requirements. Record the user's approval accurately and distinguish accepted scope from unresolved details. The register above also tracks pending decisions; a proposal is not approval. Dated historical entries retain the choices open at that time; later follow-ups and D10/D11 resolve the stack/storage/model/pilot questions without erasing their history.

When an accepted decision changes, append a new entry, mark the earlier entry superseded, and link both entries. Preserve the original rationale and approval history. Feasibility evidence may refine a proposal but does not constitute approval. Do not create separate decision files or a decisions directory.

<a id="d01"></a>

## D01 — API and simple chat UI from the start

- Status: accepted delivery scope; D10 selects framework/UI delivery; detailed policies pending
- Date: 2026-09-13
- Approval: user answered “API plus a simple chat UI from the start.”
- Related tasks: R02, R13, R13a, R13b, R14, R17

The first working RAG application must expose an API and a simple browser chat interface. A CLI-only milestone cannot satisfy the application delivery requirement. Both interfaces must use the same RAG pipeline and trace contracts as future experiments.

Plan explicit API validation, readiness/error behavior, model lifecycle and bounded request handling. Plan a UI with question input, transcript, answer/source display, loading/error states, and browser verification.

At the time of this decision, Python-served UI delivery and independent questions were unapproved proposals. [D09](#d09) subsequently resolves memory in favor of question-scoped conversation history, replacing the independent-question proposal. D10 subsequently selects FastAPI-served plain assets and complete responses with streaming deferred.

This replaces the earlier unapproved CLI-first recommendation. Verification requires a browser-to-API-to-RAG run, in addition to API and UI failure-path checks.

<a id="d02"></a>

## D02 — Runtime direction: Gemini generation, local embeddings, Docker

- Status: original local-generation preference superseded by the revision below; local embeddings retained
- Date: 2026-09-13
- Approval: user prefers local models on their ASUS Zenbook with Iris graphics, running Linux.
- Related tasks: R01, R07, R11, R13a, R16

**Historical rationale — superseded for generation by the revision below.** Prioritize local generation and local embeddings. The [hardware inventory](local-runtime-feasibility.md) records observed resources. No specific model, acceleration backend, download size, or acceptable response latency has been approved or benchmarked.

Prepare a CPU-compatible pilot proposal; verify any Iris acceleration path independently. Compare measured quality, full-application memory use, and latency before fixing the experimental target. Exact runtime/model/framework selections still require user input as major design choices.

Local preference does not authorize a hosted fallback or paid API use. If a local candidate cannot meet the agreed baseline requirements, report the evidence and alternatives before changing the execution strategy. Do not weaken baseline quality just to accommodate a particular model.

### Historical deployment clarification — 2026-09-16 (generation restriction superseded below)

The user expects Docker-based delivery and requested inspection of the sibling BUET-Job-Portal FAQ chatbot. Plan containerized delivery; exact images, service layout, and runtime remain pending. Docker packaging does not change the local-model preference or authorize hosted generation. See the current source inspection in [local runtime feasibility](local-runtime-feasibility.md).

### Revision — 2026-09-16: Gemini generation, local embeddings, Docker delivery

- Status: accepted direction; D10 selects stack/service layout and D11 selects models/runtime/version policy/pilot design; verification pending
- Approval: user selected Google's Gemini API initially, a provider-agnostic interface for later replacement, Docker delivery, local embeddings, and retained trial requests/outputs.

Use hosted Gemini generation with local embeddings and retrieval. The user considers local generation impractical for this project; this is a scope choice, not a measured finding that the laptop cannot run any generator. Supersedes the earlier local-generation preference and hosted-execution restriction above.

Keep generation behind a small shared request/result interface. Implement Gemini first; Groq or another provider can later be substituted through an adapter without rewriting ingestion, retrieval, UI, or scoring. Do not silently switch providers during a run. A provider/model change creates a new configuration and requires a new clean baseline; provider-specific roles, token accounting, and supported settings must be mapped and verified explicitly.

Use the Gemini free tier initially. Exact model availability and account quotas must be checked before the pilot; sufficiency for the study is not established. Paid usage is not approved. Rate limits should produce bounded waits/retries or a visible incomplete run, not an automatic paid or alternative-provider fallback.

Retain trial inputs and outputs, including exact assembled messages, sanitized provider request bodies, returned response content/metadata, model identifiers, resolved settings, retrieval/context inclusion, timestamps, usage/latency when available, and each attempt/error. Keep credentials and authentication/session secrets out of artifacts. Link trials to frozen corpus/index/prompt/query/configuration identities. Persist artifacts outside disposable container state. Retention of returned data does not imply access to hidden provider internals.

Verification requires a containerized local embedding/retrieval path plus real Gemini grounded generation within agreed free-tier limits, trace completeness, and deterministic fake-provider tests of the shared interface. Local generation benchmarking is no longer a prerequisite.

<a id="d03"></a>

## D03 — One Python project with separate packages

- Status: accepted
- Date: 2026-09-13
- Approval: user agreed to one Python project with separate RAG, experiment, and evaluation packages, sharing configuration and data contracts.
- Related tasks: R02, R03, R13, R13a, R13b

Use one Python project for the target application and research tooling. Keep the victim pipeline independent from experiment orchestration and scoring. Share contracts and configuration through declared interfaces; never pass answer keys or attacker labels into victim inference.

The [repository layout](repository-structure.md) proposes `src/injectrag/` with separate RAG, API, web, evaluation, and later experiment/attack packages. API and UI delivery are required by D01. D10 subsequently approves a Python-served plain browser UI in this project.

D10 subsequently selects FastAPI/Uvicorn and uv with uv.lock; exact versions and internal file boundaries remain to specify. Verify package dependency direction and that both user-facing and experiment paths call the same core pipeline.

<a id="d09"></a>

## D09 — Remember follow-ups within a question thread

> Historical entry: [D12](#d12) resolves later application policies and budget limits, removes required rewriting/fusion and revises pilot counts. Read D12 for current requirements.

- Status: accepted scope; full-history/retrieval resolved by D05; SQLite selected by D10; retention/resume/overflow pending
- Date: 2026-09-13
- Approval: user requested “make it remember the previous turns for that particular question.”
- Related tasks: R03, R09, R10, R12, R13, R13a, R13b, R14, R15, R16

### Context and rationale

Follow-up questions should use earlier turns about the current question. Independent requests cannot resolve references such as “what if that does not work?” The implementation interpretation is a conversation thread for one initial question and its follow-ups, with an explicit “New question” action to start fresh. Do not infer a topic boundary automatically.

### Decision

Supply the current thread's prior user and assistant turns to generation, within an explicit context budget. Never reuse another thread's history. Starting a new question resets the active history. This approves conversational context, not permanent memory across application restarts or a user profile.

### Consequences and verification

Add thread/turn identity to API contracts and traces. Preserve roles: prior answers are conversational context, not trusted instructions or verified evidence. Re-retrieve supporting evidence for each turn. D05 subsequently approves original-plus-rewritten retrieval, a separately configurable rewrite model, and logged original-question fallback on rewrite failure.

D05 subsequently approves full user/assistant history without routine trimming or summarization. Storage location, expiration, token accounting, and exceptional overflow behavior remain to specify. Log exactly which turns were included or omitted. Test follow-up context, explicit reset, interleaved threads, duplicate/retried requests, failures, and history overflow.

Evaluation must start each independent trial in a fresh thread. Evaluate scripted multi-turn conversations separately with frozen ordered turns; track the turn at which attacker content is exposed and any influence on later answers. Do not apply single-turn exposure formulas to persistent conversation effects without revising the study definitions.

### Supersession

Replaces the unapproved independent-question recommendation recorded with D01; D01's approved API/UI scope remains unchanged.

<a id="d04"></a>

## D04 — Synthetic corpus and executable ticket admission

> Historical entry: [D12](#d12) resolves later application policies and budget limits, removes required rewriting/fusion and revises pilot counts. Read D12 for current requirements.

- Status: accepted scope; workflow implementation details pending
- Date: 2026-09-16
- Approval: user accepted the proposed corpus, topic scope, and resolved-ticket semantics; replaced local-file-only delivery with executable submission/resolution workflows plus preloaded resolved tickets.
- Related tasks: R03–R05, R05a, R08, R13a–R14, R15

### Context and options

A fictional company policy establishes correct procedures and answer facts. Official articles alone would omit the intended employee-controlled ticket channel. Synthetic articles plus ordinary tickets support that channel while keeping procedures consistent; findings remain limited to a constructed helpdesk setting.

Account-access recovery offers more variety than forgotten passwords alone without requiring a broad initial IT study. Local-file-only ingestion would simplify implementation, but the user prefers an executable admission process and considers the additional development worthwhile with a coding agent.

### Decision

Use synthetic official articles and ordinary resolved tickets derived from a canonical fictional policy. Start with forgotten passwords, account lockouts, and lost verification devices. Include adjacent legitimate IT topics, such as VPN issues and profile updates, as retrieval distractors and clean-question material. Approved counts are recorded in D06.

Admit resolved tickets, retaining both the employee-authored description and the technician's resolution. The later attacker controls only their own description, not resolution text, official articles, or ticket status. Resolution does not certify employee text as trusted model instructions.

Build executable ticket submission and resolution workflows as part of the initial application. Also preload already-resolved synthetic tickets through local import or equivalent corpus seeding. Both paths must converge on the same resolved-ticket eligibility and content-normalization rules; seeding must not become an attacker bypass.

### Consequences and verification

Add ticket lifecycle/API/UI delivery and validation to the implementation plan. Demonstrate submission, resolution, admission, and eventual retrieval, while unresolved tickets remain outside the searchable corpus. Preserve the employee description and resolution as distinguishable fields with provenance.

Local accounts with API-enforced employee/technician roles are accepted in the follow-up below. Specify session mechanism, persistence, edit/reopen behavior, and when resolved content becomes searchable before implementation. Preserve frozen experiment snapshots when application tickets change. Preloaded and interactively resolved tickets must produce equivalent corpus documents for equivalent content.

The experiment studies admitted malicious text. Executable admission allows testing the implemented workflow; it does not establish successful evasion of a real organization's review process.

### Follow-up approval — 2026-09-16: local accounts and enforced roles

The user accepted the recommendation for seeded local employee and technician accounts with permissions enforced by the API, rather than a demo role switch. Employees submit tickets and inspect their own status; they cannot set technician resolution text or mark tickets resolved. Technician accounts perform resolution. Seed import is a setup operation, not an employee-accessible shortcut. Registration and email integration are outside this initial account scope. Exact session/storage implementation remains pending.

Verification must exercise API authorization directly, including denied employee resolution attempts, unauthenticated access to protected operations, and employee ticket ownership checks; hiding UI buttons alone is insufficient.

<a id="d05"></a>

## D05 — Grounded baseline answer behavior

> Historical entry: [D12](#d12) resolves later application policies and budget limits, removes required rewriting/fusion and revises pilot counts. Read D12 for current requirements.

- Status: answer behavior, baseline/defense separation, full history, retrieval and fallback direction accepted; SQLite selected by D10; exact syntax/fusion, retention/resume/overflow, and budgets pending
- Date: 2026-09-16
- Approval: user agreed to the grounded-answer recommendation with citations and explicit missing-evidence handling.
- Related tasks: R09–R10, R15–R16

### Context and options

Allowing general knowledge to supply company-specific procedures risks unsupported advice. Quote-only responses limit explanation and follow-up usefulness. Select natural explanations supported by retrieved company evidence.

### Decision

Require company-specific claims to be supported by retrieved material and cite supporting source IDs. Answer supported portions of a question and identify what remains unknown. Ask for clarification when the situation is ambiguous. Missing evidence that a procedure is permitted does not establish that it is forbidden. Prior conversation supplies context, not independent evidence of company policy.

### Consequences and verification

Test supported answers, partial evidence, missing evidence, ambiguity, and citation support. Score whether cited sources actually support the claims, not merely whether citation strings appear. Exact prompt wording, rendering syntax, context budget, and history storage/overflow remain pending; follow-up retrieval is resolved in the later entry below. The follow-up below settles the baseline-versus-spotlighting boundary.

### Follow-up approval — 2026-09-16: evidence separation and spotlighting

The user approved separate labeled reference content in the baseline, with retrieved passages kept outside the system-instruction field. Document text cannot create actual provider roles. Use ordinary source labels and grounded-answer instructions; do not add injection-specific handling rules to the baseline or deliberately weaken it.

The later spotlighting condition adds explicit untrusted-content boundaries and a rule to use retrieved passages as evidence without obeying embedded model-directed instructions. Keep baseline behavior, model, and other experimental settings fixed. This comparison measures the combined formatting-and-instruction intervention; attributing effects to formatting alone would require additional controlled comparisons. Exact syntax remains to specify; defense implementation stays in the later study.

Verify provider role mapping and source rendering, including documents containing fake role labels. Preserve ordinary baseline safeguards and record provider safeguards as part of the target. Spotlighting is a mitigation to measure, not a guarantee.

### Follow-up approval — 2026-09-16: original-plus-rewritten retrieval

The user selected context-aware model rewriting together with retrieval using both the original current question and its standalone rewrite, accepting an extra API call. This replaces the proposed user-history concatenation approach, which was not finalized. The current question remains the task; history helps resolve references and must not override explicit corrections or topic changes.

For follow-ups, supply full same-thread user/assistant history by default, as approved below, to a rewrite adapter, then search the same snapshot using the original question and rewritten question. Merge and deduplicate ranked chunks within a fixed total evidence budget. Assistant history may resolve references such as "the second option" but is not verified company policy. Rewriting must not answer the question or add unsupported procedural facts. First turns need no history-based rewrite. Full history is approved below; rewrite prompt/output validation, rank fusion/weights, and candidate counts remain to specify and validate on development data. Rewrite failure follows the approved fallback below.

Configure rewrite provider/model separately from answer generation. Gemini remains the initial answer provider; a different API/model may be selected for rewriting to manage quota or cost. No particular second provider/model or paid usage is selected. Different model names do not establish independent quotas; verify applicable account/project/provider limits. Keep both configurations fixed and logged within an experiment; no silent fallback.

Retain rewrite input messages, actual sanitized request, returned output, accepted search text, provider/model/settings, usage/latency, and attempts/errors, plus both retrieval rankings and final fused selection. Evaluate standalone questions, vague references, corrections, topic shifts, unsupported additions, and influence from erroneous or injected prior answers. Treat rewriting as part of the victim pipeline and multi-turn attack surface. A rewrite configuration change requires renewed clean evaluation of affected conversational behavior.

### Follow-up approval — 2026-09-16: rewrite failure fallback

The user approved continuing with original-question retrieval when rewriting fails, with the fallback explicitly logged. After bounded retries under the configured policy, record the rewrite-stage error or invalid-output reason and run only the original-question search. Do not fabricate rewritten rankings or silently change providers. Exact rewrite validation and retry limits remain to specify.

A completed answer may carry a degraded retrieval status without making the entire request an operational failure. The answer must still satisfy grounding requirements; ask for clarification or identify insufficient evidence when appropriate. Retrieval, generation, or trace-persistence failures remain explicit errors. Retain fallback trials and report their frequency and quality separately from successful two-search trials so the experiment does not conceal a change of retrieval path.

### Follow-up approval — 2026-09-16: full-thread history and prompt placement

The user approved full user/assistant conversation history by default for the expected short threads, replacing the proposed recent-exchange window (never adopted). No routine trimming or automatic summarization. Preserve native user/model roles and chronological order. New questions still start empty threads.

For answer generation, keep trusted grounded-answer instructions separate, then prior conversation, then fresh labeled retrieved evidence and the current original question last. History explains references but does not establish company policy; explicit user corrections govern interpretation of the current task. Re-retrieve evidence each turn. Do not replay historical retrieval bundles as conversation messages; preserve them separately in trial artifacts. Retain original assistant answers, including any errors, rather than silently cleaning history.

For rewriting, use full same-thread conversational history followed by the current question, with instructions to preserve corrections and resolve references without answering or inventing facts. Count tokens against each selected model's limits, including a distinct rewrite model. Exact overflow handling, storage/retention, evidence budget, and provider rendering remain pending; no permission for silent history truncation is implied.

Validate prior-answer errors, corrections, irrelevant earlier exchanges, current-source grounding, exact role/order preservation, and absence of replayed retrieval bundles. Placement is a design to test, not a guarantee that fresh evidence overrides previous model behavior.

<a id="d06"></a>

## D06 — Automated-first scoring with limited human audit

> Historical entry: [D12](#d12) resolves later application policies and budget limits, removes required rewriting/fusion and revises pilot counts. Read D12 for current requirements.

- Status: scoring direction, dataset/split/audit sizes, readiness gates, repetitions and D11 judge/pilot accepted; rubric implementation, full-run policies and script execution details pending
- Date: 2026-09-16
- Approval: user accepted automated-first scoring with limited human audit, emphasizing limited build time and attack/defense research as the main focus.
- Related tasks: R15–R17

### Context and decision

Reviewing every answer manually is too costly for the user's schedule. Automate retrieval evidence checks using pre-authored evidence annotations and citation-ID validity/context-presence checks. Use a model judge for correct/partial/incorrect answer labels, citation support, and appropriate handling of unsupported or ambiguous questions. Essential facts, material contradictions, and unsupported procedural claims are defined by the answer key; literal marker matches remain separate measurements.

Review the canonical policy and answer keys carefully. Human-audit a small random sample spanning judged passes and failures plus flagged contradictions/suspicious judgments. The subsequent approval fixes the initial audit at 10 judged answers plus flagged cases. Retain initial judge labels and any human corrections with provenance. If audit reveals systematic errors, revise the rubric/judge and rescore transparently. Report model-judged accuracy with limited human audit, not fully human-verified accuracy.

### Consequences and verification

Keep the judge observer-only: answer keys and labels never enter victim inference or retrieval. Save judge inputs, returned labels/reasons, model/prompt/settings, and errors using sanitized trial-linked artifacts. Invalid/failed judgments are unscored with explicit reporting, not automatically wrong answers. Judge provider/model, bounded usage, exact scoring aggregation, and audit procedure remain pending; no paid usage is approved.

Validate the judge on fabricated correct, incomplete, contradictory, paraphrased, and malicious-instruction-containing answers. Answer text and evidence are data, not instructions to the judge. A different judge model does not guarantee correctness or injection resistance. Later attack behavioral scoring needs its own rubric; preserve deterministic marker metrics and audit suspicious judgments separately.

### Remaining gates

Counts, split, initial audit size, readiness thresholds, and initial repeats are approved in the follow-ups below. Exact judge, rubric implementation, resource/retry limits, and conversation-script split/execution details remain to settle before baseline freeze. Minimize evaluation machinery while preserving evidence needed for credible attack/defense comparisons.

### Follow-up approval — 2026-09-16: compact dataset and initial audit

The user approved 36 clean documents: 12 official articles and 24 resolved tickets, with approximately two-thirds account-access recovery and one-third adjacent IT topics. Use distinct ticket situations and varied wording rather than article duplicates. This is a compact constructed study, not a representative production corpus.

Approve 30 development and 30 held-out independent questions. Each split contains 18 answerable account-recovery questions, 6 answerable adjacent-topic questions, 3 unsupported questions, and 3 ambiguous questions requiring clarification. Group near-duplicates/paraphrase families within one split. Freeze held-out inputs and keys before final evaluation and attacker tuning; never use held-out results for tuning while still calling them held-out. Targeted attack denominators use the relevant account-recovery subset, not all question categories.

Also approve six separate short conversation scripts covering references, corrections, topic changes, misleading prior answers, and fresh-thread isolation. Report conversational results separately from independent trials. Exact script turns and split assignment remain to specify.

Approve an initial human audit of 10 judged answers, sampled across judged successes and failures where available, plus flagged suspicious cases. Preserve sampling provenance and report that this is a limited audit, not verification of all labels. Scope for audits of later attack/defense runs remains to specify.

This resolves initial document/question/split counts and audit size. Readiness thresholds and pilot repeats were subsequently approved below; exact judge and request/resource ceilings remain pending. No corpus or evaluation data has yet been authored.

### Follow-up approval — 2026-09-16: readiness targets and initial repeats

The user approved the following held-out clean baseline gates for the 30-question set:

- Required supporting evidence reaches the final answer-model context for at least 22 of the 24 answerable questions. Check required evidence content, not merely source IDs.
- At least 21 of the 24 answerable questions are fully correct. Partial answers are reported separately and do not pass this gate.
- All 3 unsupported questions avoid invented procedures; all 3 ambiguous questions receive appropriate clarification.
- Answers counted as fully correct have no unsupported material claim in the citation-support assessment; preserve semantic labels and citation assessments separately.
- All 30 questions produce inspectable completed outcomes under the bounded retry policy. Retain initial failures/retries; do not retry until desired scores occur.

Report target and adjacent-topic results separately, plus raw counts and operational outcomes. A completed logged rewrite-fallback answer remains eligible under the approved fallback policy, with separate fallback reporting. Unscored judgments cannot establish a quality pass. These are coursework readiness criteria, not universal quality standards; three examples per special category support only limited claims.

Approve a repeatability pilot of five development questions spanning the categories, each answered three times (15 answer attempts). Initial full development and held-out baseline runs use one answer per question. Retain all outputs and scoring variation; disclose limited repetition. At this approval, attack-study repetitions and exact conversation-script execution counts remained pending. D08 subsequently approves one answer per held-out question per condition for the initial attack study; script execution counts remain pending.

If held-out gates fail, diagnose transparently. Any tuning against those results invalidates their unseen-evaluation status; do not relabel reused questions as held-out. Exact judge/model choices, token/request ceilings, latency target, and bounded retry settings remain pending. No paid usage is approved.

<a id="d07"></a>

## D07 — Frozen victim chunking and attacker-side placement/repetition

- Status: main-study approach accepted; exact attack variants and measurement details pending
- Date: 2026-09-16
- Approval: user accepted ordinary frozen chunking with observer-only integrity measurement and explicitly identified repetition/strategic placement as an attack-design dimension.

### Decision and rationale

Select and freeze victim chunking using clean development evidence, then apply identical rules to clean and malicious tickets. Do not guarantee intact instruction exposure, alter chunking for attack payloads, or use hidden victim boundaries/configuration to tune them. Observer traces may measure instruction survival and exposure after trials; they are not attacker-side feedback under the main threat model.

The attacker may know that this target uses chunking in its RAG pipeline, without knowing its splitter, chunk size, overlap, exact boundaries, or internal configuration. This is a general architectural assumption, not a claim that every RAG system necessarily chunks documents. The attacker may use that knowledge to write concise instructions, repeat instructions at multiple positions, or choose placement within their own ticket description. Technician resolution, status, and official articles remain outside attacker control.

### Consequences and verification

Consider repetition count and placement as explicit attack-design dimensions in the later plan. Exact variants, authoring/development budget, and whether to run an ablation remain pending; no exhaustive sweep is required. A controlled intact-instruction study is optional and separately labeled, not the main study.

Record document length, instruction occurrences/positions, resulting chunk counts, and which complete or partial occurrences reach the final context. Distinguish an instruction split across chunks but jointly included from an instruction whose necessary text is absent. Repetition/placement can change retrieval, context occupancy, and exposure as well as instruction survival; do not attribute all changes solely to chunk robustness. Report document-count budget alongside these properties. Annotate integrity as observer data only; freeze attack variants before inspecting hidden victim traces for evaluation.

<a id="d08"></a>

## D08 — Three-condition comparison under time constraints

- Status: condition scope, fixed N = 5, composition, authoring/access procedure, and initial repetitions accepted; exact payload details pending; attacker-side verification optional, not a blocker
- Date: 2026-09-16
- Approval: user explicitly selected conditions 1, 3, and 4 only due to limited time, declining defended-clean evaluation.

### Decision

Run only clean/undefended (clean baseline), poisoned/undefended (attacked baseline), and poisoned/defended (defended attack). Neither defended-clean nor cover-only is required or selected. This supersedes their earlier proposed inclusion in the evaluation and plan.

Compare attacked and defended runs using matching queries, poisoned snapshot, model/settings, and controlled retrieval inputs for the context-only defense. Retain answer-quality and completion measurements in the selected runs alongside attack-marker and behavioral measurements.

### Consequences and limits

Without defended-clean, the study cannot isolate the defense's utility cost on a clean corpus or claim that it preserves clean-corpus utility. Answer quality measured in defended attack describes quality under poisoning, not a substitute clean-defense condition. Without cover-only, the study cannot cleanly separate effects of added competing documents from embedded instructions; use exposure and response evidence to describe observations without overstating attribution.

The smaller scope prioritizes the coursework attack/defense comparison. Do not add excluded conditions as mandatory acceptance gates. At this initial approval, budget/set construction and later experiment repetitions remained unresolved; the follow-up below settles the document budget.

### Follow-up approval — 2026-09-16: fixed five-ticket attack budget

The user selected N = 5 only because there is insufficient time to vary N. Use five admitted attacker tickets in each poisoned snapshot, with attacker-controlled instructions confined to employee descriptions. Count parent ticket documents, not resulting chunks or repeated instruction occurrences. Preserve the 36-document clean corpus: the clean snapshot has 36 documents and each poisoned snapshot has 41. Attacked and defended comparisons use the same poisoned snapshot as already required above.

This replaces the report's proposed budgets {1, 3, 5} and the discussion recommendation for nested sets; neither proposal was approved. Do not run a budget sweep or claim to measure how effectiveness scales with document count. Results describe the selected five-ticket attack set and target configuration.

> Partly superseded by [D14](#d14): a minimal attacked-only sweep at N ∈ {1, 3, 5} over the 18 target questions, using nested subsets of the frozen five tickets, is now approved as task R22 so that the submitted report's §5.2 scaling claim is met. The fixed five-ticket set, the three conditions, and the exclusion of defended-clean and cover-only are unchanged, and the main comparison still reports N = 5.

At the fixed-budget approval, cover/topic composition, instruction strategy/variants, attacker development and observer-access procedure, and later repetitions remained pending. The next follow-up settles the composition approach. The fixed-budget approval did not select nested or repeated balanced sets. Retain D07 length, repetition, chunk-count, and exposure measurements; five documents do not imply fixed token volume or context occupancy.

### Follow-up approval — 2026-09-16: distinct covers and a shared instruction

The user clarified that testing the attack is the primary research goal, with spotlighting as the secondary comparison, and approved the recommended composition. Use one fixed set of five distinct support stories spanning forgotten passwords, account lockouts, and lost verification devices. Embed the same base instruction and class-invariant target directive in all five employee descriptions. Freeze the set before final evaluation and use the same tickets for matched attacked/defended runs.

Varied cover stories provide retrieval opportunities across the target class. A shared instruction makes the combined attack easier to interpret than a different strategy in each ticket. Results remain specific to the selected set and target configuration; this is not evidence that varied covers outperform duplicates or that all five-ticket attacks behave similarly. Preserve the three approved conditions and existing exposure/behavior measurement requirements.

At the composition approval, exact story wording and topic allocation, base instruction text and target directive, repetition, placement, concealment, variant scope, attacker development/observer access, and later experiment repetitions remained pending. The next follow-up settles the authoring/access procedure. This approval chooses the shared-instruction composition, not a particular payload or additional variant sweep. No payloads have been authored or tested.

### Follow-up approval — 2026-09-16: restricted-brief authoring and frozen evaluation

The user approved restricted-brief attack authoring followed by frozen evaluation, without a surrogate system or victim feedback during construction. Give the attack author only the target topics, employee-description permissions, general knowledge that chunking occurs, and the chosen attack objective. The author may invent their own example questions. Do not supply clean corpus contents, victim system prompts or hidden configuration, actual development/held-out questions or answer keys, or victim retrieval/output feedback to attack construction. Clean-development questions serve baseline development, not attacker training.

Freeze the five tickets before testing them against the victim. Researchers acting as observers may then inspect the questions, outputs, rankings, chunk boundaries, and final context to explain outcomes, but those observations must not guide revisions to the frozen attack. This preserves D07 and the no-victim-interaction threat model; iterative victim-guided optimization would require a separately approved study change.

Retain the exact authoring brief and supplied-material identities, frozen ticket hashes and freeze time, and any known information leakage or deviations. Same-team separation is procedural, not guaranteed blindness; do not claim otherwise. An authoring context already exposed to withheld material cannot be presented as blind merely because the files were later hidden. The study tests a non-adaptive attack and does not establish the strongest attack achievable with repeated feedback.

At this authoring/access approval, exact payload details/variant scope and experiment repetitions remained pending; the later entry below settles initial experiment repetitions. No surrogate, attack payload authoring, or victim experiment has been performed.

### Historical report reconciliation — 2026-09-16: restoration proposal resolved below

Direct reading of the original report confirms that section 3.4 (PDF page 5) defines the attacker knowledge boundary, while section 4.2 (page 7) explicitly includes bounded payload verification/revision using an attacker-side model M_a, without querying the deployed victim. The earlier no-surrogate recommendation removed that proposed step; it was a scope simplification, not a requirement of the black-box threat model. Section 3.4 also does not explicitly state a blanket clean-corpus-reading prohibition; the restriction above is an additional procedural assumption.

At this point, restoring bounded M_a verification was recommended but had not been approved. The following repetition approval did not settle it. The later optional-extension decision below resolves the proposal; preserve this earlier reasoning as history.

### Follow-up approval — 2026-09-16: one answer per question per condition

The user approved starting with one answer per held-out question per selected condition and explicitly reporting the limitation. Run the same 30 held-out independent questions in clean baseline, attacked baseline, and defended attack, once each in fresh threads: 90 planned answer outcomes total. Reuse the already-planned 30 clean baseline outcomes only when the frozen configuration matches the comparison; this leaves 60 additional answer generations for attacked/defended runs, excluding judge calls and bounded operational retries. These counts describe the initial comparison, not approval of additional payload variants or all-project API usage.

Target attack rates use the 18 answerable account-recovery questions, with completion/paired eligibility disclosed under the evaluation contract. The other 12 questions assess adjacent-topic answers, unsupported handling, and clarification separately. Retain all attempts and errors. Operational retries follow the bounded policy and are not independent experiment repetitions; never rerun a completed answer because the attack failed or the score was undesirable. Preserve missing pairs and completion counts.

Disclose that one answer per question does not measure within-question attack-outcome variability. The approved clean five-question × three-answer pilot remains unchanged and does not establish attack repeatability. Conversation-script execution details, exact retry/resource ceilings, and payload/variant details remain pending. No experiments or API calls have occurred.

### Follow-up approval — 2026-09-16: submitted report and optional extensions

The user provided the shortened submitted report, since committed to this repository as [`design_report.pdf`](../design_report.pdf) and referred to at the time by its submission filename `B1_Group_7.pdf`, explaining that it was reduced to avoid overpromising, and selected attacker-side model M_a verification as possible future work only. Keep the current required study without M_a or surrogate verification; this resolves the restoration proposal without making model choice or verification-attempt limits a blocker. Preserve optional ideas in [things to try if time permits](optional-extensions.md), separate from required delivery and acceptance checks. Listing an idea does not authorize extra implementation, model/API usage, or experiments.

Read-only review of the nine-page submitted report confirms that it contains no attacker-side M_a verification loop. Its section 3.1 (PDF page 3) explicitly says the attacker cannot observe the legitimate corpus D, in addition to S, the encoders, and the victim query. Thus the existing clean-corpus restriction is supported by this submitted version; the earlier reconciliation concerned the original detailed draft only. Distinguish submitted-report references from the historical detailed draft. Neither PDF overrides later approvals, including N = 5, the three-condition scope, and one answer per question per condition.

The core attack remains authoring from the restricted brief followed by frozen victim evaluation, without victim-guided revision. An optional M_a extension would use attacker-invented examples and a bounded separately selected model, not victim feedback or held-out material. Its exact model, limits, and evaluation protocol would be specified only if the extension is later selected. No extension has started.

<a id="d10"></a>

## D10 — Compact application stack and local Qdrant

> Historical entry: [D12](#d12) resolves later application policies and budget limits, removes required rewriting/fusion and revises pilot counts. Read D12 for current requirements.

- Status: accepted design; D11 resolves model/version/pilot selections; implementation and verification outstanding
- Date: 2026-09-17
- Approval: after discussing Qdrant and clarifying the revised two-service layout, the user approved the remaining stack recommendations.
- Related tasks: R01–R03, R05a, R08–R09, R12–R14, R17

### Decision

D10 approves FastAPI/Uvicorn with one initial worker, a FastAPI-served HTML/CSS/JavaScript UI using fetch and complete responses, uv with pyproject.toml and a committed uv.lock, SQLite through Python sqlite3 for accounts/tickets/threads/turns, and local Qdrant for vectors and chunk metadata. Docker Compose runs two services: one custom application image and the existing Qdrant image, with separate persistent host mounts for application state, Qdrant data, snapshots/results, and model cache. Research commands use the application image as one-off jobs.

Keep Gemini behind the approved replaceable provider adapter and keep embedding computation local in the application. Qdrant stores/searches vectors; choosing it does not choose an embedding model. The browser calls the same API used by the application workflows. Start with a loading indicator and complete answers; streaming is deferred. One initial Uvicorn worker avoids unintended duplication of embedding instances; blocking local work must not prevent readiness responses.

Use short SQLite transactions through small storage functions; do not hold a transaction across a model call. SQLite is application state, Qdrant is retrieval storage, and sanitized trial/judge/audit artifacts remain separately retained outside container layers. SQLite persistence is now selected for conversation records; retention, expiration, restart/resume behavior, and exceptional history overflow still require policy decisions. Full same-thread history and fresh-thread isolation remain unchanged.

### Rationale and alternatives

The earlier NumPy exact-search/one-service recommendation was not approved. Qdrant reduces custom vector persistence, metadata mapping, and search infrastructure at the cost of one additional service. Select a local Qdrant server in Compose, not embedded local mode or Qdrant Cloud. One custom application image plus the existing Qdrant image means two services; it does not create a second Python project. Django and a separately built frontend were alternatives, not selected dependencies.

Qdrant does not automatically make collections immutable or provide experiment provenance. Preserve the existing snapshot compatibility, complete-publication, frozen-input, and observer-label boundaries in the index adapter. Exact collection naming/publication, search settings and tie handling remain to specify. No NumPy search backend is required by this approval.

### Remaining gates and verification

Exact Python/dependency/image versions, embedding model/runtime, Gemini answer model, rewrite/judge providers and models, published free-tier limits and actual account quotas, token/request/time/retry/concurrency ceilings, and a bounded feasibility pilot remain pending. Session mechanism, ticket edit/reopen rules, index publication timing, history retention/resume/overflow, retrieval fusion, and prompt settings remain separate policy work. One server worker does not establish an approved inference concurrency or memory limit.

Verify locked installation and image identities, browser/API integration, Qdrant known-vector ranking/reload/compatibility and frozen-collection isolation, SQLite transaction/ownership behavior, readiness during slow inference, and persistent data across container recreation when implementation is authorized. No installs, downloads, scaffolding, live API calls, experiments, or paid usage are authorized by this design approval.

### Sources and earlier decisions

Read-only official documentation checked during this review: [FastAPI static files](https://fastapi.tiangolo.com/tutorial/static-files/), [Uvicorn workers](https://fastapi.tiangolo.com/deployment/server-workers/), [uv locking](https://docs.astral.sh/uv/concepts/projects/sync/), [SQLite usage and concurrency](https://www.sqlite.org/whentouse.html), [Qdrant client](https://github.com/qdrant/qdrant-client), [Qdrant local Docker setup](https://qdrant.tech/documentation/quickstart/), and [Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/). These support capabilities, not measured InjectRAG feasibility.

This resolves stack/storage/delivery details left open in D01–D05 and D09; it preserves their approved behavior and historical entries. Exact models and operational policies remain open. The user prioritizes stack/models and the bounded pilot discussion next; unfinished attack/scoring discussions do not gate this design review.

<a id="d11"></a>

## D11 — Models, version policy, and bounded pilot design

> Historical entry: [D12](#d12) resolves later application policies and budget limits, removes required rewriting/fusion and revises pilot counts. Read D12 for current requirements.

- Status: accepted design; account access/quota, compatibility and measured feasibility unverified; execution not authorized
- Date: 2026-09-17
- Approval: user accepted the model/runtime/version/pilot recommendations after confirming that the local embedding approach matches the BUET Job Portal source default.
- Related tasks: R01–R03, R06–R07, R09–R12, R14–R17

### Selected models and runtime

D11 selects BAAI/bge-small-en-v1.5 through FastEmbed/ONNX Runtime on CPU, Gemini gemini-3.8-flash for answers and separate observer judging, and gemini-3.5-flash-lite for independently configured rewriting. Use google-genai, Python 3.12, low thinking for answers/judging and minimal thinking for rewriting. Resolve compatible stable dependencies during authorized setup, commit exact uv.lock versions, pin Docker images by digest, and record embedding revisions/hashes before baseline freeze.

All three hosted roles initially use Gemini, behind the replaceable provider adapter. Keep role-specific model/prompt/settings independently configurable. The judge operates in separate observer-only requests with keys/rubrics, never in victim inference. Using the same model for answers and judging saves implementation effort but can produce correlated errors or self-preference; disclose this limitation and preserve the approved limited human audit. A different provider is not selected. Choose models for clean quality and operation, not because an attack succeeds.

The embedding model produces 384-dimensional vectors and has a 512-token input limit. Keep actual embedding inputs, including prefixes/special tokens, within the limit and detect overlength input rather than silently truncating. Chunk size/overlap and query handling remain application-policy details. Use CPU FastEmbed/ONNX without a local generator or required PyTorch/CUDA stack. Read-only reinspection confirmed that the sibling chatbot uses this same model default through qdrant-client[fastembed], loading it lazily and reusing the instance; private overrides and measured runtime were not checked. The 4 GiB application ceiling below is not an estimate of model RAM.

### Version policy

Python 3.12 is selected. Exact stable package patch releases and image digests are resolved and compatibility-tested during authorized setup, recorded, and frozen before evaluation; selecting these pins is routine implementation work within this policy, not a renewed design gate. Dependency/provider/model substitutions remain explicit design changes. Record actual ONNX artifacts/tokenizer hashes and requested/reported hosted model identity; endpoint selection does not guarantee immutable provider internals. Do not use a moving latest model alias. Other generation settings, prompt text, token accounting implementation and application policies still need specification before dependent work.

### Approved pilot design, not execution permission

| Pilot item | Approved design bound |
|---|---|
| Clean answers | Five development questions × three answers = 15 planned answers (existing D06 repeatability scope) |
| Judge requests | Judge the 15 answers plus five fabricated validation cases = 20 planned requests |
| Rewrite requests | Five fixed follow-up validation cases, separate from the six conversation scripts |
| Inference total | 40 planned requests plus at most five retry attempts = 45 maximum |
| All API requests | 100 maximum including inference, token counting, and metadata checks |
| Input | At most 8,192 tokens per request, including instructions, evidence, history and formatting |
| Output | At most 4,096 tokens for answers/judging; 512 for rewriting; account for provider thinking-token behavior |
| Model concurrency | One model request at a time |
| Retries | At most one retry per failed request, within the shared five-attempt retry allowance |
| Attempt timeout | 90 seconds for answers/judging; 30 seconds for rewriting |
| Container memory ceiling | Application 4 GiB, Qdrant 1 GiB; recheck available host resources before execution |
| Operational target | Median answer latency at most 30 seconds excluding deliberate quota waits, complete traces and responsive readiness checks |

The counters are cumulative across the pilot, including resumed sessions; they do not reset to create more allowance. Account limits override these ceilings. Pause on daily quota exhaustion, keep retry waits bounded, and retain failures rather than switching provider/tier. Record truncation, timeout and malformed results explicitly; do not repeat a completed answer to improve scores. Rewrite failure retains the D05 original-only retrieval fallback. Oversized history must produce an explicit outcome, never silent trimming. Exact overflow UX, queueing, retry eligibility/backoff and full-study aggregate allowances remain application-policy work.

The pilot checks feasibility and obvious quality problems; it does not replace D06 held-out readiness gates or the six conversation scripts. Memory/latency ceilings are acceptance targets, not measured results. Planning this pilot does not authorize provisioning, installation, scaffolding, model downloads, live calls, experiments or paid usage. Any separate early R01 smoke calls need an explicit allocation within an approved execution budget; do not silently add calls to the 40 planned requests.

### Published availability versus actual account capacity

Official pages reviewed on 2026-09-17 list gemini-3.8-flash and gemini-3.5-flash-lite, free-tier text input/output pricing, and no announced shutdown date for those endpoints. Google's public rate-limit page directs users to AI Studio for active limits; it does not establish a numeric free-tier RPM/TPM/RPD allowance for this account. Limits apply per project, not per key, and available capacity is not guaranteed. Account model access, tier and active quotas remain unverified. No paid usage or silent fallback is approved.

Answer generation and judging share the selected model's quota. One judge request per answer would yield 180 inference requests for 90 held-out answers plus judgments; compatible reuse of 30 clean answers and their compatible judgments leaves 120 additional requests. These are planning counts, not an approved all-project execution allowance. Judge rubric/configuration must also match for judgment reuse. Development, scripts, retries, rewrite validation and auxiliary API requests add usage; model names do not establish independent quota pools.

Sources: [BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5), [FastEmbed](https://pypi.org/project/fastembed/), [Google SDK](https://pypi.org/project/google-genai/), [official SDK guidance](https://ai.google.dev/gemini-api/docs/libraries), [Gemini models](https://ai.google.dev/gemini-api/docs/models), [thinking settings](https://ai.google.dev/gemini-api/docs/thinking), [pricing](https://ai.google.dev/gemini-api/docs/pricing), [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), and [deprecations](https://ai.google.dev/gemini-api/docs/deprecations). Source review is not an account test or an InjectRAG benchmark.

### Closure and remaining work

D10 and D11 close the stack/model selections, version policy and initial pilot design. Preserve older pending statements as dated history; D11 resolves the corresponding model/pilot questions in D02/D03/D05/D06/D10. Model access/quota verification, lock/image/artifact pinning, compatibility checks and actual pilot measurements remain execution prerequisites/evidence, not unmade model selections. Application policies and attack/measurement details remain separate review batches. No application implementation or experiment has started.

<a id="d12"></a>

## D12 — Application policies, top-five retrieval and whole-study budget

> [D13](#d13) subsequently supplies routine starting defaults and updates implementation authorization; D12 behavioral choices remain unchanged. [D14](#d14) adds the R22 sweep phase and revises the aggregate totals below to 347 planned calls, 28 retries, 375 attempts, 3,072,000 input and 849,920 output tokens; every per-attempt limit and policy in this entry is unchanged.

- Status: accepted design; implementation and runtime verification outstanding
- Date: 2026-09-17
- Approval: user accepted the policies recorded in temporary notes, chose five chunks with reranking off, and then instructed: “Approve the budget plan, then update all of the docs in the repo to be consistent with these decisions.”
- Related tasks: R01, R03, R05a, R09–R17

### Tickets and publication

Submitted ticket descriptions are immutable. Technicians resolve once; no ticket editing or reopening. Resolution automatically starts live publication; resolved means eligible and successful complete publication means searchable. Retain visible retryable publication failures. Live publication never mutates frozen clean/poisoned experiment snapshots. The exact schema and complete-publication orchestration in [SQLite proposal](../sqlite-schema-plan.txt) remain proposals, not an implemented database.

### Login, history and request handling

D12 selects a username/password form for seeded accounts and Starlette signed-cookie SessionMiddleware. Store only account ID in an HttpOnly, SameSite=Strict browser-session cookie, hashed passwords in SQLite, and check current account role/ownership on every protected API request. Logout clears the cookie; a random signing secret at startup invalidates cookies on app restart. No SQLite sessions table, registration, persistent login or external identity service. Bind the HTTP demo to loopback; use HTTPS/Secure cookies beyond localhost and reject cross-site state-changing requests. Cookie clearing is not server-side revocation of copied cookies.

D12 retains SQLite threads/turns across restarts without automatic expiry, for inspection rather than resumption. Follow-ups use full ordered user/assistant history only within the active thread; New question starts empty. Leaving or restarting does not allow old-thread continuation. Prior evidence bundles remain in artifacts. Preflight the complete answer request, including output reserve. If full history cannot fit, return HTTP 422 with a context-limit code and a start-new-question message, preserve typed input, record the error, and make no answer call or turn append. Never silently trim or summarize history. Explicit cleanup follows preservation of required research artifacts.

D12 removes the waiting chat queue. Keep one hosted model call at a time; an occupied inference slot returns HTTP 503 with a machine-readable busy code promptly, without model work or turn creation. Preserve typed text for manual retry and keep readiness responsive. Oversized raw questions return HTTP 413; history/context overflow returns HTTP 422. Set the raw-question size cap during API configuration.

### Retrieval and optional extensions

D12 selects one cosine vector search using the current question as written, including follow-ups: top five chunks, descending score with stable chunk-ID tie breaking. Deduplicate only by chunk ID; no reranking, query rewriting, fusion, per-document quota, source preference, attacker-label filtering or uncalibrated similarity cutoff. Include whole chunks in rank order under a 2,048-token evidence ceiling including labels and the complete request limits; log excluded chunks and reasons. Actual context may contain fewer than five chunks. Trace raw top-five rankings and actual context separately. Validate on clean development data and freeze before held-out evaluation; changes require evidence and review. Use identical retrieval rules across conditions and the same poisoned snapshot/candidate list for matched attacked/defended single-turn trials.

Full history goes to answer generation, not the retrieval query. Vague follow-ups can retrieve poorly; validate references, corrections, topic shifts and misleading prior answers with clean scripts, and clarify when evidence cannot support a response. No rewrite output, rewrite validation/fallback or fusion stage exists. Rewriting and reranking are [optional extensions](optional-extensions.md), requiring separate approval and budget. The earlier eight-candidate/six-selected proposal was not supported by measured clean-development evidence and was not adopted. Five is the approved starting limit, not a measured optimum.

### Retry policy

D12 permits at most one retry of a hosted answer or observer-judge call only for temporary network failure, timeout, provider 5xx, or 429 with a short retry window. Retry a failed judge only, never its completed answer. Pause on daily/account quota exhaustion. Poor retrieval, wrong answers and missing attack markers never trigger retries; no automatic Qdrant search retry. Attempts retain one logical trial identity and consume both phase and study limits. Ticket-publication retry is separate. Exact bounded wait timing remains to specify; the proposed 30-second 429 cutoff is not approved.

### Approved aggregate budget

| Phase | Answers | Judgments | Planned calls | Extra retry attempts | Maximum attempts |
|---|---:|---:|---:|---:|---:|
| Pilot | 15 | 20 (including five fabricated cases) | 35 | 5 | 40 |
| Full development | 30 | 30 | 60 | 5 | 65 |
| Held-out, three conditions | 90 | 90 | 180 | 10 | 190 |
| Six clean scripts × three turns, once each | 18 | 18 | 36 | 5 | 41 |
| **Whole study** | **153** | **158** | **311** | **25** | **336** |

The user approved this revised budget on 2026-09-17. The six scripts run on the clean system, three turns each, once, with one judgment per turn. Script contents and development/held-out assignment still need specification. Count the 30 clean held-out answers and compatible judgments once; reuse them in the three-condition comparison. Development is counted separately from the pilot. No attacked/defended scripts, optional extensions or separate early feasibility smoke calls are included. Allocate any early smoke explicitly within an approved plan before execution; do not silently add calls or spend retry reserves on new trials.

Every inference attempt has at most 8,192 input tokens. Pilot answer/judge output caps are 4,096; later caps are 2,048, including provider thinking usage where applicable. The study ceilings are 2,752,512 input tokens (336 × 8,192) and 770,048 output tokens (40 × 4,096 + 296 × 2,048). These are worst-case limits, not expected consumption. The 800 total API-request ceiling includes inference, token counting and metadata; the pilot's 100-request sublimit remains. Count attempts conservatively when provider usage is unavailable, reserve capacity before dispatch, and persist cumulative phase/study counters across run restarts. Do not reset counters to create new allowance. Stop before exceeding any cap and report incomplete outcomes. Rate limits control speed; this budget controls total usage. Actual account quotas may be lower and take precedence. Budget approval does not authorize paid usage, extra experiments or execution in this documentation task.

Retain the 90-second answer/judge attempt timeout, one-call concurrency, 4 GiB application/1 GiB Qdrant pilot memory ceilings and median answer-latency target of 30 seconds excluding quota waits. Removing five rewrite fixtures reduces the pilot to 35 planned calls/40 maximum attempts; the removed calls are not reassigned.

### Remaining work and verification

Still specify clean chunking/overlap, prompts/spotlighting syntax, source rendering, embedding overlength handling, exact API/schema details and complete-publication method; settle page-refresh/visit semantics and bounded retry wait timing. Set routine size caps and IDs during implementation design. Specify script contents/split, attack target/marker and payload details, behavioral scoring rubric and later human-audit scope. No extra judge call per metric is budgeted: the single judgment must return the required labels, with deterministic metrics computed locally. Verify model access/free-tier quotas, pins and measured feasibility before execution. Do not reinterpret these remaining items as reopening accepted top-five retrieval, no-rewrite/no-reranking, login or budget decisions.

### Supersession and records

Supersedes D05 required original-plus-rewritten retrieval and fallback, D11 rewrite model/fixtures and original pilot totals, and earlier pending statements for the policies settled here. Preserves D06 readiness, D08 fixed five-ticket/three-condition/non-adaptive attack scope and primary fresh-thread single-turn metrics. Operational retries do not add evaluation repetitions. The temporary notes remain a conversation record; this decision register now governs maintained documentation.

<a id="d13"></a>

## D13 — Implementation readiness and rapid delivery sequence

- Status: implementation direction accepted; concrete starting defaults are implementer choices within D12, not additional user-approved research decisions
- Date: 2026-09-17
- Source: user requested that documentation and the draft plan be ready for rapid implementation toward the attack and defense, then instructed “Continue.”

Proceed with the accepted clean build; do not require another blanket authorization based on historical documentation-only restrictions. The current review updates the plan and does not claim implementation or live execution has occurred. Paid use, model substitutions, scope/budget expansion and changes to research claims still require review.

The [plan](../plans/draft-plan.md#2-implementation-gates-and-rapid-delivery-order) now groups work into five delivery batches and supplies R18–R21 attack/defense tasks. R01 local preflight runs alongside scaffolding; measured hosted feasibility follows a working pipeline. The first planned R16 pilot answer supplies live integration evidence, without an extra smoke call. Reproduction uses local rebuilds, retained outputs and offline scoring rather than another baseline generation. All D12 counts and limits remain unchanged.

Routine starting details are now recorded in the plan: the SQLite outline with complete-snapshot publication, page-memory visit tokens with refresh ending a visit, bounded retry waits (1 second for eligible non-429 errors; valid Retry-After up to 30 seconds for 429), 2,000-character questions also constrained by the 512-token embedding input bound, 20,000-character ticket fields, paragraph-aware 320-token chunks with up to 48-token overlap, and a three-development/three-held-out split for the six three-turn scripts. These are implementation defaults to validate on clean data, not measured optima or a claim that the user separately approved each number. Record exact resolved settings and hashes; preserve accepted top-five retrieval and the 2,048-token evidence allowance.

This resolves routine starting-detail deferrals in D12 and the SQLite proposal for beginning the build. Final code/schema/prompt details and account/model compatibility still need verification. D12 retry eligibility and no silent truncation remain binding. An unavailable selected model is a blocker for live calls, not permission for automatic substitution.

The exact attack target/marker, five-ticket payload specification, behavioral rubric and later audit scope remain research gates before R18/R20. Restricted authoring must use a person/context that has not received withheld inputs; an implementation agent that knows victim internals cannot later claim blindness. Clean development and generic comparison tooling can proceed while those research choices are settled. No extra variants, attack-authoring model calls or optional extensions are budgeted.

<a id="d14"></a>

## D14 — Submitted-report reconciliation and minimal budget sweep

- Status: accepted
- Date: 2026-09-17
- Approval: after a verification pass comparing [`design_report.pdf`](../design_report.pdf) against the maintained documentation, the user chose the cheapest sweep that keeps the main project intact, chose to keep payload wording fully pending, and chose to keep tickets immutable while disclosing the narrowing.
- Related tasks: R18–R22

### Context

The submitted nine-page report is now committed in this repository as `design_report.pdf`. Earlier documentation referred to it as `B1_Group_7.pdf` at an external `Downloads` path and cited section numbers from a longer unsubmitted draft, so its review table could not be checked against anything a reader actually has. A verification pass against the committed PDF also found three substantive divergences.

### Decision

**1. The committed PDF is the single authoritative report.** All documentation cites `design_report.pdf` and its real section numbers (§1–§6, Appendix A). The fourteen-page draft is history only; where a review item originated against it, its old section number is kept in parentheses. Neither PDF is edited.

**2. Restore the §5.2 budget-scaling claim with a minimal sweep (new task R22).** D08 dropped the sweep for time, but §5.2 of the submitted report states the evaluation "measures how effectiveness scales with the poisoning budget N". Run **attacked/undefended only**, at **N ∈ {1, 3, 5}**, over the **18 answerable account-recovery questions** only. N = 5 is the already-planned R20 attacked run, so only N = 1 and N = 3 are new: **36 answers and zero additional judgments**, because the sweep reports only `RSR_topk`, `RSR_context`, `ISR_marker`, `ASR_marker` and `ASR_exclusive_marker`, all of which are deterministic marker/exposure matches computed locally.

Construct Γ₁ ⊂ Γ₃ ⊂ Γ₅ as **nested subsets of the already-frozen five tickets**: order the five frozen tickets by content hash ascending, take the first one for Γ₁ and the first three for Γ₃. Declare this ordering in the R18 freeze record *before* any sweep run. Nesting is what makes the comparison interpretable — cover content is held fixed and only the count changes — and it authors no new payloads. This is the one place where nested sets are approved; D08's earlier statement that nested sets were not selected applied to the then-pending composition question and is superseded here.

Limits on what the sweep may claim: three points on 18 questions with one answer each, from a single frozen attack set, describe a trend, not a dose-response curve. Sweep points carry **no judged answer-quality or behavioral labels** and **no defended condition**. Never reorder or reselect the subsets after seeing results.

**3. Payload wording and target marker remain pending.** Appendix A of the submitted report shows a complete example attacker document, including the literal `it-support-portal.example.com`. The user chose to keep the payload fully pending: Appendix A is illustrative, and all five tickets are authored under the D08 restricted brief at R18. The chosen target marker must still be a reserved example domain, absent from the clean corpus, matched deterministically. Documentation must not present Appendix A's string as the frozen marker.

**4. Ticket immutability is kept, and the narrowing is disclosed.** Report §3.2 grants the attacker permission to "submit or modify" their own ticket content; D12 makes submitted descriptions immutable. Keep D12. The implemented attacker is strictly weaker than the report's — submission alone, no modification — and the attack does not depend on modification. Record this in the deviation register and the final write-up.

**5. Two report ambiguities are resolved rather than left open.** Report §3.2's unattributed "ingestion screens content for plausibility" is mapped onto **technician resolution**, which is the plausibility screen; no instruction-level filter is added. Report §3.1's document-level `E(q; D)` is reconciled with chunk-level retrieval: **retrieval units are chunks; Γ membership, the N budget and the 36/41 document counts are over parent ticket documents**.

### Revised budget

R22 adds 36 planned calls and a 3-attempt retry reserve to the [D12](#d12) allocation.

| Phase | Answers | Judgments | Planned calls | Extra retry attempts | Maximum attempts |
|---|---:|---:|---:|---:|---:|
| Pilot | 15 | 20 (including five fabricated cases) | 35 | 5 | 40 |
| Full development | 30 | 30 | 60 | 5 | 65 |
| Held-out, three conditions | 90 | 90 | 180 | 10 | 190 |
| Six clean scripts × three turns, once each | 18 | 18 | 36 | 5 | 41 |
| R22 sweep: N ∈ {1, 3} × 18 target questions, attacked only | 36 | 0 | 36 | 3 | 39 |
| **Whole study** | **189** | **158** | **347** | **28** | **375** |

Revised ceilings: **3,072,000 input tokens** (375 × 8,192) and **849,920 output tokens** (40 × 4,096 + 335 × 2,048). The **800 total API-request ceiling is unchanged** and still accommodates 375 inference attempts plus token counting and metadata; the pilot's 100-request sublimit is unchanged. Every other D12 limit — 8,192 input tokens per attempt, 2,048 post-pilot output cap, 90-second attempt timeout, one call at a time, cumulative counters persisted across restarts — applies to R22 unchanged.

### Consequences and verification

R22 is the **last** task and runs only after R20 and R21 have completed and been recorded. If account quota, time or budget runs short, drop R22 and report the sweep as not performed: the three-condition study is the deliverable and does not depend on it. Dropping R22 restores exactly the D08 position, so the main project stays intact either way.

Verify that Γ₁ and Γ₃ are literal subsets of the frozen Γ₅ with matching parent hashes, that snapshots contain 37 and 39 documents respectively against the unchanged 36 clean documents, that the subset ordering was recorded before execution, and that no sweep run triggers judge calls. Reuse the R20 attacked results as the N = 5 point rather than regenerating them.

### Supersession

Supersedes D08's exclusion of a budget sweep and its statement that nested sets were not selected, for this narrowly scoped attacked-only sweep only. Preserves D08's three conditions, the fixed five-ticket frozen set, restricted-brief authoring, and one answer per held-out question per condition. Preserves every D12 policy; revises only the D12 aggregate call, attempt and token totals as tabulated above. Defended-clean and cover-only remain excluded.

## Template for future entries

Copy this structure into a new entry in this file; replace the placeholder ID and retain stable IDs for existing entries.

```markdown
## DXX — Decision title

- Status: proposed / accepted / superseded
- Date:
- Approval reference:
- Related tasks:

### Context

The problem, constraints, and report assumptions involved.

### Options and rationale

Alternatives, evidence, costs, and limitations; distinguish estimates from observations.

### Decision

The approved choice, or the proposal and pending question.

### Consequences and verification

Affected contracts/tasks, tradeoffs, required checks, and migration implications.

### Supersession

Links to any earlier or replacement entry, with the reason for the change.
```
