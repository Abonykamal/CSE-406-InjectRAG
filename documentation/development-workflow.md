# Development and implementation-agent workflow

## Session orientation

The root [AGENTS.md](../AGENTS.md) instructs Codex to use the repository's [$orient skill](../.agents/skills/orient/SKILL.md) on the first user message of a new session. It reads the core project context and then the additional documentation relevant to the request. The skill is read-only and does not start implementation by itself.

You can also request `$orient` explicitly to refresh context. Startup behavior relies on Codex loading this repository's `AGENTS.md`; it is an instruction-based workflow, not a background process. If the new skill does not appear in the selector, restart Codex. The root instruction also provides its direct file path.

## Starting a task

1. Read project status, the relevant accepted decisions, and the task in `plans/draft-plan.md`.
2. Inspect existing code and working-tree changes. Preserve unrelated user edits.
3. Check prerequisites and decision gates. A recommendation or PDF statement is not approval for a major design choice.
4. Implement the bounded deliverable, validate its acceptance criteria, and update the affected documentation.
5. Record completed work, evidence, limitations, and the next unblocked task. Leave unverified criteria open.

## Decision boundaries

Ask before changing language/framework, runtime/provider or resource budget, application delivery scope, repository packaging, corpus admission policy, baseline trust/prompt policy, attacker knowledge, experiment definitions, or accepted performance targets. Prepare the options and available evidence first. Continue independent authorized work while awaiting answers, but do not implement dependent choices.

Routine implementation details within accepted contracts—internal helper names, error wording, and fixture organization—can be resolved by the implementation agent. Discovery of a report fault is expected; record it rather than treating the report as immutable.

## Decision-review handoff

Read the current decision register and later amendments rather than interpreting historical pending notes as current blockers. D04–D08 now have accepted directions; do not reopen those choices. Keep both READMEs, architecture/contracts, evaluation, status, and dependent plan tasks aligned whenever a decision changes. Preserve historical approval rationale while refreshing current summaries. Use the remaining agenda in project status to distinguish unreviewed research issues from routine implementation details. The user prioritizes attack testing and a compact build, with spotlighting as a secondary comparison; excluded defended-clean and cover-only runs must not reappear as requirements. D08 fixes N = 5 admitted attacker tickets with distinct covers spanning the three recovery topics and one shared base instruction/directive for the three main conditions. [D14](decisions.md#d14) adds exactly one budget sweep — attacked-only, N ∈ {1, 3, 5}, 18 target questions, nested subsets of the frozen five, as task R22 — because submitted report §5.2 promises scaling. Do not widen that sweep, add a defended point, author new payloads for it, or treat nested sets as approved anywhere else.

For later attack construction, follow D08 restricted-brief authoring and freeze tickets before victim testing. Do not pass actual development/held-out questions or keys, clean corpus contents, victim prompts/configuration, or victim feedback into the authoring context. No surrogate is selected. Keep observer analysis separate from authoring, retain the brief/freeze provenance, and disclose any known same-team leakage; do not describe an already-informed author as blind.

D08 initial evaluation uses one answer for each of the 30 held-out questions in each selected condition, with operational retries separate. Preserve unfavorable completed answers, report variability limits, and do not add repeated runs or payload variants without an approved scope change. The user has resolved M_a verification as optional future work only. Keep [things to try if time permits](optional-extensions.md) outside required tasks and acceptance gates; do not treat available time or list membership as authorization to run an extension.

D10 approves the application stack and two-service Qdrant layout. Do not reopen FastAPI/plain UI, uv, SQLite, or Qdrant as pending defaults. D11 now closes exact model/runtime selections, version policy and pilot design. D12 settles application/retrieval/retry policies and the aggregate study budget. Account quotas, compatibility/pins and actual feasibility remain verification work. Follow D12 without reopening its accepted choices; resolve only the remaining schema/publication, prompt/chunking, retry-wait and visit details. Stable package patch versions and image digests can be resolved during authorized setup within D11 without reopening model selection; substitutions remain design changes. D13 records the latest direction to begin implementation and supersedes the earlier documentation-only restriction. Begin local build work using the plan; actual credentials, account quotas, budget accounting and frozen inputs gate hosted runs. Paid usage remains excluded.

## Documentation responsibilities

- `architecture.md`: component and flow changes.
- `data-contracts.md`: schema and artifact changes, with migrations if needed.
- `decisions.md`: one ADR-style log of approved major choices and superseded decisions; append entries here rather than creating separate files.
- `project-status.md`: implemented state, validation evidence, next task, blockers.
- `testing-and-reproducibility.md`: supported validation/reproduction procedure.
- Add `local-development.md` when install/run commands exist, and `baseline-results.md` only when measurements exist. Add experiment-specific documentation when that work starts.

Do not populate setup commands or result tables with invented outputs. Keep the root README as a concise entry point linking authoritative details. No deployment, external communication, or published release is part of the present planning request.

## Rapid implementation handoff

Use the five batches and starting defaults in the [implementation plan](../plans/draft-plan.md#2-implementation-gates-and-rapid-delivery-order). Complete related R-tasks together as a working slice. Finalize routine details in code/config and update their contracts without repeatedly asking for approval. Preserve actual approval boundaries for models, budget, threat model and study claims. Reuse the first budgeted pilot request as hosted integration evidence; routine tests and reproduction must not add hidden inference calls.
