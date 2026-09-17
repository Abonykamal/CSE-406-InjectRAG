# Design report review

The submitted report defines research intent but leaves implementation choices open. Current user approvals govern scope. The table distinguishes issues addressed by accepted decisions from remaining technical proposals. The original report-review pass did not verify external literature; later runtime/prompt references are recorded in their relevant documents. A documented correction is not evidence that every item has been explained to the user.

## Which report these sections refer to

**The authoritative source is [`design_report.pdf`](../design_report.pdf) in this repository** — the nine-page submitted report, reduced by the user from an earlier draft to avoid overpromising. Its structure is: §1 Overview and Problem Definition; §2 System Model (2.1 workflow/components, 2.2 trust boundary); §3 Attack Model and Design (3.1 definition, 3.2 scenario, 3.3 payload structure, 3.4 message sequence); §4 Implementation Plan; §5 Attack Outcome and Evaluation (5.1 expected outcome, 5.2 evaluation); §6 Defense Design; Appendix A example attacker-controlled document.

The table below cites **submitted-report sections**. An earlier fourteen-page draft (`InjectRAG_Design_Report-detailed.pdf`) used a different, longer numbering; where a review item originated against that draft, its old section number appears in parentheses as history. That draft is not in this repository and is not needed — every live review item is stated against sections that exist in `design_report.pdf`.

| Submitted-report location | Issue or ambiguity | Current treatment / remaining discussion |
|---|---|---|
| §5.2 (draft §9.1) | ASR factorization `ASR = RSR × ISR` assumes marker matches cannot happen without retrieval | Use the conditional identity in [evaluation](evaluation.md#trial-events); measure non-exposure matches |
| §5.2 (draft §9.1) | ISR has no defined value when no poison is retrieved | Emit N/A with denominator zero, never 0 |
| §5.1, §5.2 (draft §§4.4, 10) | Correct evidence in the corpus is treated as correct evidence in the assembled context | D06 approves separate retrieval/final-context evidence diagnostics; record required passage content, not only document IDs |
| §5.2 (draft §9.2) | Literal target and ground-truth containment overstate compliance/correctness | D06 approves model-judged clean quality with limited audit; retain marker proxies separately. Attack behavioral rubric and proxy limitations still need specification |
| §5.2 (draft §9.3 versus §8) | "Measures how effectiveness scales with the poisoning budget N", but varying N also varies cover diversity and composition | D08 fixed N = 5; [D14](decisions.md#d14) now adds a minimal nested attacked-only sweep at N ∈ {1, 3, 5} so the submitted claim is met. Nested subsets hold cover content fixed, which is what makes the comparison interpretable; see the deviation register below |
| §3.1, §3.3 (draft §§4.2, 5.1 versus §3.4) | The draft assumed guaranteed instruction chunk integrity, which needs knowledge the black-box attacker lacks | Not asserted in the submitted report. D07 accepted: ordinary frozen victim chunking and observer-only integrity measurement. Attacker may use general chunking knowledge for repetition/placement, without hidden-boundary feedback; controlled intact-exposure study remains optional |
| §3.3, Appendix A (draft §§4.2, 9.3) | Adding the optional concealment instruction can change chunk boundaries and retrieval, not just generation | Compare document versions, chunk layouts, and exposure; avoid attributing all differences to concealment |
| §3.2 | "Submit **or modify** their own ticket content" grants an edit capability the application does not implement | D12 makes submitted descriptions immutable with no editing or reopening. The implemented attacker is strictly weaker than the report's; see the deviation register below |
| §3.2 | "Ingestion screens content for plausibility but performs no instruction-level inspection" — the report does not say what performs that screen | Mapped to technician resolution: a technician reads the ticket and resolves it, which is the plausibility screen. No instruction-level filter is added. Recorded in [architecture](architecture.md#trust-and-experiment-boundaries) |
| §3.1, §5.2 | `E(q; D)` is written over documents, but the implemented retriever returns chunks | Retrieval units are chunks; Γ membership and the N budget are counted over parent ticket documents. See the deviation register below |
| §3.2 (draft §3.3, and the historical README) | Submitted tickets versus resolved tickets as the admission channel | Resolved by D04 scope approval: resolved tickets retain employee descriptions and technician resolutions; executable submission/resolution plus preloaded resolved tickets. D12 adds immutable submission, one-way resolution, signed-cookie login and automatic live publication; D13 supplies the starting schema/publication outline |
| §3.1, §3.2 (draft §§3.4, 4.2, 9.2) | Same team can inadvertently tune attacker content on hidden victim queries/configuration | D08 approves restricted-brief authoring without a surrogate or victim feedback, followed by frozen evaluation; withhold actual development/held-out questions, corpus, and internals, and disclose same-team leakage |
| §4 (draft §§5.1, 13) | Models, storage, sizes, and revision pinning are unspecified | D10/D11 select stack, models, version policy and pilot bounds; account quotas, concrete pins/compatibility and measured feasibility remain unverified; disclose provider revision limitations |
| §4 | The report's six implementation phases are not a task breakdown | Mapped to plan tasks in the [phase mapping](#submitted-report-implementation-phase-mapping) below; the plan delivers all six |
| §6 | Spotlighting is phrased as though it guarantees instruction separation | Treat it as an empirical mitigation; compare security and answer quality in the D08 selected conditions without claiming isolated clean-corpus utility preservation |
| §5.2, §6 (draft §§9.3, 11) | Clean-corpus defense utility cost is not separately measured | The submitted report's own condition list is clean / attacked / defended, which is exactly D08's selected scope, so this is not a deviation. The limitation stands: without a defended-clean run the defense's utility cost on a clean corpus is not isolated |
| — (draft §§9.3, 10) | Draft cross-references to a nonexistent §5.3 | Resolved editorially by the shortening; no such reference exists in the submitted report |
| §5.1 (draft §5.1) | The draft described temperature zero as ensuring deterministic output without repeated trials | The submitted report does not make this claim. D06 still approves five development questions × three repeats, and D08 approves one answer per held-out question per condition, with variability limits disclosed |

## Change process

When implementation exposes a problem, retain a minimal reproducer or pilot trace, describe which claim or contract is affected, compare fixes, and seek user input for a major change. Update the decision record, plan, architecture, and affected experiment manifests together. Never silently change the threat model or weaken the baseline to obtain a successful attack.

## Review progress

D04 resolves the admission channel; D05 resolves grounded baseline/spotlighting separation and conversation/retrieval direction; D06 resolves clean scoring scope, dataset sizes, and initial repeatability/readiness targets; D07 resolves the chunk-integrity assumption; D08 selects three conditions and fixed N = 5 with five distinct covers sharing one base instruction/directive, omitting defended-clean and cover-only. [D14](decisions.md#d14) restores a minimal budget sweep so the submitted report's §5.2 scaling claim is met; defended-clean and cover-only remain excluded. Attack testing is primary; spotlighting is secondary.

D08 also approves restricted-brief authoring followed by frozen evaluation, with no surrogate or victim feedback during construction; same-team separation remains a disclosed procedural limitation.

The earlier fourteen-page draft's section 4.2 included bounded attacker-side M_a verification without deployed-victim access. The submitted `design_report.pdf` omits that loop; the user keeps M_a as optional future work only, not a required restoration or blocker. Submitted §3.1 (page 3) explicitly excludes attacker observation of `D`, which supports the recorded clean-corpus restriction. See [optional extensions](optional-extensions.md).

D08 approves one answer per held-out question per condition for the initial study, with operational retries separate and variability limits disclosed.

Remaining explanation/decisions: exact payload/variant details and the target marker; probability-factorization and zero-exposure interpretation; attack marker versus behavioral compliance/displacement; and concealment/repetition confounds if variants are run. The submitted PDF has not been edited; the deviation register above is the record of where implementation departs from it.

## Deliberately deferred

Concrete dependency/image/model-artifact pins under D11, detailed attack authoring, spotlighting syntax, additional attack variants/repeats beyond the approved 30-question × three-condition single-answer comparison and the D14 sweep, exact inference quotas, and experimental results. Clean baseline sizes/repetitions are approved in D06; D11 approves model IDs, runtime/version policy and pilot bounds. The remaining items need feasibility evidence, routine pinning or later user decisions; this draft does not present them as settled. Attacker-side model selection belongs only to the optional M_a extension, not the required study.

## Submitted-report reconciliation

[`design_report.pdf`](../design_report.pdf) is the nine-page submitted report, identified by the user as the reduced submission intended to avoid overpromising. Section 3.1 preserves the class-wide attack objective and explicitly excludes observation of the legitimate corpus `D`. Section 3.3 retains distinct covers and a shared directive but has no M_a verification loop. Section 5.2 proposes budget scaling and uses marker-based metrics and the simplified ASR identity; section 6 describes spotlighting. Later approvals and the existing measurement/utility limitations govern the implementation. The PDF has not been edited.

## Deviation register — submitted report versus implemented study

Every point where the built system or the study intentionally differs from `design_report.pdf`. Report these in the final write-up; do not let them accumulate silently.

| # | Report says | Implementation does | Why, and what it costs |
|---|---|---|---|
| 1 | §3.2: attacker may "submit **or modify**" their own ticket content | D12: submitted descriptions are immutable; no editing, no reopening | Removes an endpoint and its state machine. The implemented attacker is **strictly weaker** than the report's: it can only submit. The attack does not depend on modification, so this narrows capability without invalidating any result. Never describe this as evading a real review process |
| 2 | §5.2: "measures how effectiveness scales with the poisoning budget N" | [D14](decisions.md#d14): minimal attacked-only sweep at N ∈ {1, 3, 5} over the 18 answerable recovery questions, using nested subsets of the frozen five tickets | D08 had dropped the sweep for time. The minimal form costs 36 answers and no extra judge calls, because the sweep reports only deterministic locally computed marker/exposure metrics. Sweep points carry no judged answer-quality labels, and the defended condition is not swept |
| 3 | §3.1/§5.2: `E(q; D)` and RSR are written over **documents** | Retriever returns the top five **chunks**; a document contributes several chunks | Chunk-level retrieval is standard and is what the 2,048-token evidence ceiling budgets. Resolution: retrieval units are chunks, but Γ membership, the N budget and the 36/41-document counts are always over **parent ticket documents**. `RSR_topk` asks whether any chunk whose parent is in Γ appears in the raw top five |
| 4 | §3.2: "ingestion screens content for plausibility but performs no instruction-level inspection" | Technician resolution is that screen; no separate filter exists | The report does not name the screening actor. Mapping it onto the technician step makes the assumption concrete and testable rather than hypothetical |
| 5 | §5.2: `ASR = RSR × ISR` stated as an identity | Recorded as conditional on zero non-exposure marker matches, and `RSR` is split into `RSR_topk` / `RSR_context` | The report's justification (the marker is absent from the clean corpus) does not rule out a generator emitting the string unprompted. The conditional form is measurable; non-exposure matches are recorded and investigated |
| 6 | §5.2 and §6: "Clean Accuracy" as a defense utility axis | Measured in each of the three selected conditions, with no defended-clean run | The submitted report's own condition list is clean / attacked / defended, so the conditions match. The limitation is that the defense's utility cost on a clean corpus is not isolated |
| 7 | Appendix A: a complete example attacker document with the literal `it-support-portal.example.com` | Payload wording and target marker remain **pending** until R18 | User decision: keep the payload fully pending and author all five tickets under the restricted brief. Appendix A is illustrative, not the frozen payload. The chosen marker must still be a reserved example domain absent from the clean corpus, as Appendix A's is |

## Submitted-report implementation-phase mapping

The report's §4 lists six phases. The plan does not adopt them as its task structure, but it delivers all six. This mapping lets a reader check coverage.

| Report §4 phase | Plan tasks | Delivery batch |
|---|---|---|
| Phase 1 — RAG System: ingestion, chunking, embedding, indexing, retrieval, context construction, generation | R01–R14 | A, B |
| Phase 2 — Clean Corpus and Baseline | R04, R15, R16, R17 | C, D |
| Phase 3 — Attack Implementation: payload construction, attacker-document creation, verified ingestion/retrieval | R18, R19 | D |
| Phase 4 — Evaluation: RSR, ISR, ASR, ASR-exclusive, Clean Accuracy | R20, plus the [metric mapping](evaluation.md#report-metric-names-versus-implementation-metric-names) | E |
| Phase 5 — Defense: spotlighting between retrieval and generation | R21 step 1 | E |
| Phase 6 — Defense Evaluation and Final Testing | R21 steps 2–4, R22 sweep, R17 reproduction | E |

## Subsequent application and budget alignment

[D12](decisions.md#d12) supersedes required rewriting/fusion: use the original current question, top-five cosine retrieval, no reranker and at most 2,048 evidence tokens. Retained history is for active-thread generation and research inspection, with no old-thread resume. Login, no-queue errors, publication behavior and transient retry eligibility are accepted. [D14](decisions.md#d14) revises the aggregate budget to 347 planned calls and 375 maximum attempts. Reranking and rewriting are optional extensions, not prerequisites for valid metric measurement. Final schemas, prompts/chunking, retry wait timing and the remaining attack/scoring details still require work.

D13 supplies routine starting defaults and removes those details as blanket build blockers. The remaining attack/scoring choices gate R18/R20 specifically; R18–R22 describe the execution path. Runtime feasibility and account checks remain evidence requirements.
