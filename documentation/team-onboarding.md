# Teammate onboarding

The project is in design review. No application, dataset, models, or experiment
results exist yet. The agreed study scope is ready to explain; the implementation
choices below still gate dependent work. This page summarizes current decisions
and does not approve new technology, experiments, or task ownership.

## Read first

1. [Project overview](../README.md): research question, target, and threat model.
2. [Current status](project-status.md): what exists and the remaining agenda.
3. [Decision register](decisions.md): current approvals; dated older entries retain history.
4. [Implementation plan](../plans/draft-plan.md): dependencies, deliverables, and acceptance checks.

Then read the documents relevant to your task through the [documentation index](README.md).
The shortened submitted report is B1_Group_7.pdf; the detailed report is an earlier
draft. Current approvals govern where the reports differ. Neither external PDF is
needed to understand or implement the maintained plan.

## Agreed delivery and study

- One Python project, API and simple chat UI, executable ticket submission/resolution,
  seeded employee/technician roles, Docker delivery, and persistent trial artifacts.
- Gemini generation through a replaceable adapter; local embeddings/retrieval;
  independently configurable rewriting. Free tier initially; no paid usage approved.
- Grounded answers with citations, missing-evidence handling, clarification,
  question-scoped full history, and original-plus-rewritten follow-up retrieval with
  logged original-only fallback.
- Clean corpus: 12 articles and 24 resolved tickets. Development and held-out sets:
  30 questions each, plus six separate conversation scripts. D06 defines readiness.
- Attack testing is primary; spotlighting is a secondary comparison. Add five
  attacker tickets with distinct recovery-topic stories sharing one base instruction
  and directive. Only employee descriptions are attacker-controlled.
- Three conditions: clean baseline, attacked baseline, defended attack. Initial
  held-out evaluation uses one answer per question per condition. No budget sweep,
  defended-clean, or cover-only run. M_a verification is optional future work.
- Attack construction uses a restricted brief without victim feedback, internal
  configuration, clean corpus contents, or actual evaluation questions/keys. Freeze
  tickets before victim testing. Observer inspection explains results without
  feeding revisions back into the frozen attack; disclose same-team limitations.

D10 approves FastAPI/Uvicorn with one initial worker, a FastAPI-served HTML/CSS/JavaScript UI using fetch and complete responses, uv with pyproject.toml and a committed uv.lock, SQLite through Python sqlite3 for accounts/tickets/threads/turns, and local Qdrant for vectors and chunk metadata. Docker Compose runs two services: one custom application image and the existing Qdrant image, with separate persistent host mounts for application state, Qdrant data, snapshots/results, and model cache. Research commands use the application image as one-off jobs. These are design approvals only; no application files or services exist.

D11 selects BAAI/bge-small-en-v1.5 through FastEmbed/ONNX Runtime on CPU, Gemini gemini-3.8-flash for answers and separate observer judging, and gemini-3.5-flash-lite for independently configured rewriting. Use google-genai, Python 3.12, low thinking for answers/judging and minimal thinking for rewriting. Resolve compatible stable dependencies during authorized setup, commit exact uv.lock versions, pin Docker images by digest, and record embedding revisions/hashes before baseline freeze. See [D11](decisions.md#d11) for the approved pilot design and its limits. Stack/model selection is closed; account quotas and measured feasibility have not been verified.

## Decisions still needed

| Review batch | Remaining choices | Needed before |
|---|---|---|
| Attack and measurement | Exact target behavior/marker; initial payload wording, repetition/placement and concealment choice; behavioral scoring rubric and attack-run audit scope | Payload freeze and security scoring, not ordinary clean ingestion |
| Application policies and limits | Ticket edits/reopening, sessions/SQLite schemas/index publication; history retention/resume/overflow; retrieval fusion/rewrite validation; full-run aggregate budgets, queue/overflow/retry details beyond the approved pilot bounds | Dependent workflow, context, API, and integration tasks |

**Stack and models: design closed (D10/D11).** Before live work, verify account model access/free-tier quotas and dependency compatibility, record exact package/image/model-artifact pins under the approved policy, then obtain measured feasibility evidence within the approved pilot design after execution is authorized. These are verification tasks, not pending model selections.

Also settle the six conversation scripts' split and execution details before their
evaluation. Metric interpretation needs a short review: marker presence versus
actual compliance, top-k versus context exposure, the conditional ASR identity,
zero-exposure ISR, and concealment/repetition confounds. These explanations do not
require extra experimental conditions.

Exact clean chunk size/overlap, retrieval counts, evidence limits, and prompt wording
need concrete proposals and clean development evidence. Record initial settings and
freeze final choices before evaluation; do not invent measured optimal values during
onboarding or tune them against attack success. Existing approval gates still apply.

## Suggested task split, not assigned ownership

| Work area | Plan tasks and interfaces |
|---|---|
| Target application | R01–R14: runtime, ingestion/retrieval/generation, ticket workflow, API/UI, and trace persistence. See [architecture](architecture.md) and [contracts](data-contracts.md). |
| Corpus and evaluation | R04, R15–R17: canonical policy, clean documents, split questions/keys, scorer/audit, baseline and reproduction. See [corpus](corpus-and-baseline.md) and [evaluation](evaluation.md). |
| Attack and secondary defense | Later research phase after the clean baseline: restricted-brief payload authoring, frozen poisoned snapshots, exposure/behavior scoring, and spotlighting comparison. See [design review](design-review.md). |

Agree named owners and immediate tasks as a team. Account for the attacker knowledge
boundary when sharing material: someone who has already inspected withheld data
cannot later be described as a blind attacker. A shared repository alone does not
enforce this separation.

Before coding, read the task prerequisites and [development workflow](development-workflow.md).
Do not infer implementation approval from a proposed setting. Preserve existing
working-tree changes and record actual checks, not planned success. Optional ideas
remain in [things to try if time permits](optional-extensions.md), outside completion gates.
