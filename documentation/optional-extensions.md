# Things to try if time permits

These are optional research ideas outside required delivery. The user explicitly
placed attacker-side model verification, model-generated follow-up rewriting,
and retrieval reranking here to keep the submitted scope compact. Listing an idea does not approve its
implementation or experiment. The required study can be completed without any
of them; no implementation task, model choice, or acceptance
gate depends on this list. Current approvals remain in [D08](decisions.md#d08) and [D12](decisions.md#d12). The 311-call/336-attempt study budget allocates no extension runs.

Prioritize the working clean target, the frozen five-ticket attack, its evaluation,
and the approved secondary spotlighting comparison. Select an extension separately
only if time and approved free-tier resources permit. No paid usage is authorized.
This list does not reopen excluded budget sweeps, defended-clean, or cover-only runs.

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

The submitted report is **B1_Group_7.pdf** (nine pages); it omits the attacker-side
verification loop. The earlier **InjectRAG_Design_Report-detailed.pdf** proposed that
loop in section 4.2. Neither external PDF is a required repository dependency, and
neither creates additional implementation commitments beyond current approvals.
