# Architecture decision log

**Pending means not approved.** Recommendations guide discussion; they do not authorize an implementation agent to select a major design. The user approved D01 and D03 and supplied the local-runtime preference for D02. Exact runtime choices remain pending. D04–D08 are follow-up gates at the relevant stage rather than presumed approvals.

| ID | Major decision | Proposal / alternatives | Status | Blocks |
|---|---|---|---|---|
| [D01](#d01) | First application interface | API plus simple chat UI from the start | Accepted | UI architecture remains pending; question-scoped memory accepted in D09 |
| [D02](#d02) | Models, hardware, cost, execution | Local models preferred on Linux ASUS Zenbook with Intel Iris Xe; hardware inventory recorded | Direction accepted; exact stack pending | Model/runtime selection and real-model feasibility |
| [D03](#d03) | Language and project layout | One Python project with separate RAG, experiment, and evaluation packages and shared contracts/configuration | Accepted | Exact framework and package tooling remain pending |
| D04 | Corpus and ingestion realism | Recommend synthetic official articles plus resolved tickets, one password/account class first, adjacent-topic distractors; local ingestion initially | Pending follow-up | Corpus authoring and ingestion semantics |
| D05 | Baseline prompt and context policy | Recommend normal grounded assistant, source IDs and insufficient-evidence response; no defense-specific spotlighting in baseline | Pending follow-up | Prompt implementation and experimental baseline |
| D06 | Clean readiness and scoring | Agree corpus/query counts, answer rubric, retrieval/answer thresholds, pilot repeat count, cost ceiling, and held-out split | Pending follow-up | Baseline freeze and M4 completion |
| D07 | Attacker knowledge versus chunk integrity | Prefer ordinary victim chunking and observer-only integrity measurement; controlled integrity study is a separately labeled alternative | Pending later study | Attack construction and claims |
| D08 | Controlled comparison design | Confirm cover-only control, held-out access, budget-set construction, and defended clean condition | Pending later study | Attack/defense experimental plan |
| [D09](#d09) | Conversation memory | Remember follow-ups within the current question thread; new questions start fresh threads | Accepted scope | Storage, retention, history budget, and follow-up retrieval policy remain to specify |

## Logging convention

Keep all architecture decision records (ADRs) in this file. Add dated entries with a stable ID, status, context, options/rationale, decision, consequences, and verification requirements. Record the user's approval accurately and distinguish accepted scope from unresolved details. The register above also tracks pending decisions; a proposal is not approval.

When an accepted decision changes, append a new entry, mark the earlier entry superseded, and link both entries. Preserve the original rationale and approval history. Feasibility evidence may refine a proposal but does not constitute approval. Do not create separate decision files or a decisions directory.

<a id="d01"></a>

## D01 — API and simple chat UI from the start

- Status: accepted for delivery scope; UI implementation details pending
- Date: 2026-09-13
- Approval: user answered “API plus a simple chat UI from the start.”
- Related tasks: R02, R13, R13a, R13b, R14, R17

The first working RAG application must expose an API and a simple browser chat interface. A CLI-only milestone cannot satisfy the application delivery requirement. Both interfaces must use the same RAG pipeline and trace contracts as future experiments.

Plan explicit API validation, readiness/error behavior, model lifecycle and bounded request handling. Plan a UI with question input, transcript, answer/source display, loading/error states, and browser verification.

At the time of this decision, Python-served UI delivery and independent questions were unapproved proposals. [D09](#d09) subsequently resolves memory in favor of question-scoped conversation history, replacing the independent-question proposal. Framework, UI delivery, and streaming remain unspecified.

This replaces the earlier unapproved CLI-first recommendation. Verification requires a browser-to-API-to-RAG run, in addition to API and UI failure-path checks.

<a id="d02"></a>

## D02 — Local models preferred on the Linux laptop

- Status: direction accepted; exact models/runtime and pilot limits pending
- Date: 2026-09-13
- Approval: user prefers local models on their ASUS Zenbook with Iris graphics, running Linux.
- Related tasks: R01, R07, R11, R13a, R16

Prioritize local generation and local embeddings. The [hardware inventory](local-runtime-feasibility.md) records observed resources. No specific model, acceleration backend, download size, or acceptable response latency has been approved or benchmarked.

Prepare a CPU-compatible pilot proposal; verify any Iris acceleration path independently. Compare measured quality, full-application memory use, and latency before fixing the experimental target. Exact runtime/model/framework selections still require user input as major design choices.

Local preference does not authorize a hosted fallback or paid API use. If a local candidate cannot meet the agreed baseline requirements, report the evidence and alternatives before changing the execution strategy. Do not weaken baseline quality just to accommodate a particular model.

<a id="d03"></a>

## D03 — One Python project with separate packages

- Status: accepted
- Date: 2026-09-13
- Approval: user agreed to one Python project with separate RAG, experiment, and evaluation packages, sharing configuration and data contracts.
- Related tasks: R02, R03, R13, R13a, R13b

Use one Python project for the target application and research tooling. Keep the victim pipeline independent from experiment orchestration and scoring. Share contracts and configuration through declared interfaces; never pass answer keys or attacker labels into victim inference.

The [repository layout](repository-structure.md) proposes `src/injectrag/` with separate RAG, API, web, evaluation, and later experiment/attack packages. API and UI delivery are required by D01. A Python-served page is a pending delivery proposal, not a reason to create a separate frontend project now.

Exact framework, package manager, dependency lock format, and internal file boundaries remain implementation proposals. Verify package dependency direction and that both user-facing and experiment paths call the same core pipeline.

<a id="d09"></a>

## D09 — Remember follow-ups within a question thread

- Status: accepted scope; storage and retrieval details pending
- Date: 2026-09-13
- Approval: user requested “make it remember the previous turns for that particular question.”
- Related tasks: R03, R09, R10, R12, R13, R13a, R13b, R14, R15, R16

### Context and rationale

Follow-up questions should use earlier turns about the current question. Independent requests cannot resolve references such as “what if that does not work?” The implementation interpretation is a conversation thread for one initial question and its follow-ups, with an explicit “New question” action to start fresh. Do not infer a topic boundary automatically.

### Decision

Supply the current thread's prior user and assistant turns to generation, within an explicit context budget. Never reuse another thread's history. Starting a new question resets the active history. This approves conversational context, not permanent memory across application restarts or a user profile.

### Consequences and verification

Add thread/turn identity to API contracts and traces. Preserve roles: prior answers are conversational context, not trusted instructions or verified evidence. Re-retrieve supporting evidence for each turn. Propose how follow-up retrieval uses history before implementing query rewriting or another retrieval-policy change; generation-only history may not retrieve relevant evidence for elliptical follow-ups.

Storage location, expiration, maximum history budget, and truncation policy remain to specify under D05 and runtime planning. Log exactly which turns were included or omitted. Test follow-up context, explicit reset, interleaved threads, duplicate/retried requests, failures, and history overflow.

Evaluation must start each independent trial in a fresh thread. Evaluate scripted multi-turn conversations separately with frozen ordered turns; track the turn at which attacker content is exposed and any influence on later answers. Do not apply single-turn exposure formulas to persistent conversation effects without revising the study definitions.

### Supersession

Replaces the unapproved independent-question recommendation recorded with D01; D01's approved API/UI scope remains unchanged.

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
