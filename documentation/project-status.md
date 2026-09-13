# Project status

Last updated: 2026-09-13.

## Implemented and verified

- Repository initially contained a project README and local session metadata; no application, dependencies, corpus, or tests were present.
- Detailed report reviewed; replacement implementation draft and project documentation created.
- The old README implementation checklist is superseded by `plans/draft-plan.md`.

## Not implemented

No ingestion, chunking, embeddings, index, retrieval, generation, CLI/API/UI, attack tooling, scoring harness, or defense exists. No baseline or security measurements have been performed. Documentation checks do not establish application correctness.

## Current milestone

**M0 — design clarification and approval.** The draft is reviewable; major choices are pending in the [decision register](decisions.md). Proposed file paths and command names are not existing functionality.

D01 (API + simple chat UI) and D03 (one Python project) are accepted. D02 records local models preferred on the user’s Linux laptop. D09 approves question-scoped conversation memory. Next: resolve UI delivery and corpus questions, then propose exact runtime choices using the recorded hardware inventory; resolve prompt and baseline gates D05–D06 before dependent tasks. Do not install a stack, select a paid provider, or create an application skeleton on the strength of a recommendation alone.

| Milestone | State | Exit evidence |
|---|---|---|
| M0: approve target-system design | Pending user decisions | Accepted decision records and concrete feasibility scope |
| M1: reproducible ingestion/index | Not started | Validated clean snapshot and rebuild checks |
| M2: inspectable retrieval | Not started | Retrieval traces on development questions |
| M3: complete clean RAG | Not started | One documented ingestion-to-answer run |
| M4: clean baseline and handoff | Not started | Frozen manifest, scored run, approved readiness thresholds |
| Later: attack/defense study | Deferred | Separate detailed plan after M4 |

## Blockers and risks

API + simple chat UI and one Python project are approved. Exact UI architecture, history storage/budget and follow-up retrieval policy, runtime/model choices, corpus scope, baseline prompt, and acceptance thresholds remain pending. These block dependent implementation, not documentation work. The report's black-box restrictions and chunk-integrity assumption need reconciliation before attack planning. See [design review](design-review.md).

## Change log

- 2026-09-13: recorded D09, remembering follow-ups within a question thread with a fresh thread for a new question; updated history, API/UI, testing, and evaluation requirements.

- 2026-09-13: consolidated decision records and pending choices into `documentation/decisions.md` at the user’s request; preserved IDs, approval state, and rationale.

- 2026-09-13: recorded user approval of API + simple chat UI and one Python project; recorded local-model preference and read-only hardware inventory. Expanded plan with API and browser UI tasks. No models downloaded or application code created.

- 2026-09-13: replaced the high-level implementation checklist with a RAG-first draft; added architecture, contracts, repository, evaluation, testing, workflow, and decision documentation. No software results claimed.
