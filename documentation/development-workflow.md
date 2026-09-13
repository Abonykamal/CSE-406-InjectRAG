# Development and implementation-agent workflow

## Starting a task

1. Read project status, the relevant accepted decisions, and the task in `plans/draft-plan.md`.
2. Inspect existing code and working-tree changes. Preserve unrelated user edits.
3. Check prerequisites and decision gates. A recommendation or PDF statement is not approval for a major design choice.
4. Implement the bounded deliverable, validate its acceptance criteria, and update the affected documentation.
5. Record completed work, evidence, limitations, and the next unblocked task. Leave unverified criteria open.

## Decision boundaries

Ask before changing language/framework, runtime/provider or resource budget, application delivery scope, repository packaging, corpus admission policy, baseline trust/prompt policy, attacker knowledge, experiment definitions, or accepted performance targets. Prepare the options and available evidence first. Continue independent authorized work while awaiting answers, but do not implement dependent choices.

Routine implementation details within accepted contracts—internal helper names, error wording, and fixture organization—can be resolved by the implementation agent. Discovery of a report fault is expected; record it rather than treating the report as immutable.

## Documentation responsibilities

- `architecture.md`: component and flow changes.
- `data-contracts.md`: schema and artifact changes, with migrations if needed.
- `decisions.md`: one ADR-style log of approved major choices and superseded decisions; append entries here rather than creating separate files.
- `project-status.md`: implemented state, validation evidence, next task, blockers.
- `testing-and-reproducibility.md`: supported validation/reproduction procedure.
- Add `local-development.md` when install/run commands exist, and `baseline-results.md` only when measurements exist. Add experiment-specific documentation when that work starts.

Do not populate setup commands or result tables with invented outputs. Keep the root README as a concise entry point linking authoritative details. No deployment, external communication, or published release is part of the present planning request.
