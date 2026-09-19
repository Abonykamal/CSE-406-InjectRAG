# Things to try if time permits

These are optional research ideas outside required delivery. The user explicitly
placed attacker-side model verification, model-generated follow-up rewriting,
and retrieval reranking here to keep the submitted scope compact. Listing an idea does not approve its
implementation or experiment. The required study can be completed without any
of them; no implementation task, model choice, or acceptance
gate depends on this list. Current approvals remain in [D08](decisions.md#d08), [D12](decisions.md#d12) and [D14](decisions.md#d14). The 347-call/375-attempt study budget allocates no extension runs.

Prioritize the working clean target, the frozen five-ticket attack, its evaluation,
the approved secondary spotlighting comparison, and then the R22 sweep. Select an extension separately
only if time and approved free-tier resources permit. No paid usage is authorized.
This list does not reopen the excluded defended-clean or cover-only runs, and it does not extend the D14 sweep beyond its approved attacked-only, 18-question, N ∈ {1, 3, 5} scope.

| Idea | What it could add | Extra work / boundary |
|---|---|---|
| Attacker-side model M_a verification | Test and revise payloads on attacker-invented questions before freezing them, as proposed in the original detailed draft | Explicitly optional by user decision. Requires model selection, bounded attempts, retained requests/results, and a separate frozen attack-set identity. Does not require replicating the whole RAG application. No deployed-victim feedback, hidden configuration, clean corpus, or actual evaluation questions may guide authoring. |
| Model-generated follow-up rewriting | Compare current-question retrieval with a standalone follow-up rewrite on predeclared multi-turn scripts; measure whether this changes retrieval, attacker-content exposure, or later answers | Explicitly optional by user decision. The required pipeline uses no rewrite model. A later comparison needs its own rewrite model calls, validation, result-combination rule, trace fields, frozen settings, and approved run budget. Keep its outcomes separate from the primary fresh-thread single-turn study; do not revise the frozen attack after observing victim results. Rewriting may reveal another attack path but does not guarantee attack success. |
| Retrieval reranking | Measure how adding a relevance reranker changes clean evidence quality, attacker-content exposure, and attack success relative to the simple top-five baseline | Explicitly optional by user decision; reranking is off in required delivery. Select and validate the reranker and candidate count using clean development data, specify an additional resource budget, and freeze settings before evaluation. Retain candidate ranks before and after reranking and actual context inclusion. Preserve the original baseline results and frozen attack; do not tune the reranker or revise payloads to obtain a desired attack outcome. |
| Additional answer repetitions | Show whether the same frozen attack/question produces different outcomes across runs | Proposal only. Predeclare questions and repeat counts; preserve every output and operational failure. Do not select questions or stop repeats based on whether the attack succeeds. This does not change the approved initial one-answer policy. |
| One focused payload comparison | Explore one instruction-placement/repetition change, or concealment on/off | Proposal only. Vary one chosen property, hold covers/base directive fixed where possible, and log changes in length, retrieval, and exposure. No exhaustive sweep or guaranteed chunk integrity. |

Any later extension must preserve the current results and distinguish new attack
sets/runs from the original study. Reused evaluation material must not be described
as unseen if it informed development. The same-team access limitation still applies.
Keep candidate authoring separate from observer findings; no extension here permits
victim-guided tuning. Exact models, API limits, extra run counts, and protocols are
specified only if an extension is selected.

The submitted report is [`design_report.pdf`](../design_report.pdf) (nine pages), committed
in this repository; it contains no attacker-side verification loop. The earlier fourteen-page
draft proposed that loop in its section 4.2 and is not included here. The report creates no
implementation commitments beyond current approvals, except where the
[deviation register](design-review.md#deviation-register--submitted-report-versus-implemented-study)
records one.

Note that the poisoning-budget sweep is **no longer** an optional idea: [D14](decisions.md#d14)
makes it required task R22, because submitted report §5.2 promises it. R22 is droppable under
budget pressure, but it is planned work, not an extension.
