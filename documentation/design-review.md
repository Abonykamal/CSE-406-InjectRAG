# Design report review

The original detailed draft and the shortened submitted report define research intent but leave implementation choices open. The table below retains section references to the original detailed draft; submitted-report references are explicitly labeled. Current user approvals govern scope. The table distinguishes issues addressed by accepted decisions from remaining technical proposals. The original report-review pass did not verify external literature; later runtime/prompt references are recorded in their relevant documents. A documented correction is not evidence that every item has been explained to the user.

| Report location | Issue or ambiguity | Current treatment / remaining discussion |
|---|---|---|
| §5.1 | Temperature zero is described as ensuring deterministic output without repeated trials | D06 approves five development questions × three repeats; D08 approves one answer per held-out question per condition for the initial attack study, with variability limits disclosed |
| §9.1 | ASR factorization assumes marker matches cannot happen without retrieval | Use the conditional identity in evaluation documentation; measure non-exposure matches |
| §§4.4, 5.2, 10 | Correct evidence in corpus is treated as correct evidence in the assembled context | D06 approves separate retrieval/final-context evidence diagnostics; record required passage content, not only document IDs |
| §§4.2, 5.1 versus §3.4 | Guaranteed instruction chunk integrity assumes control/knowledge the black-box attacker does not have | D07 accepted: ordinary frozen victim chunking and observer-only integrity measurement. Attacker may use general chunking knowledge for repetition/placement, without hidden-boundary feedback; controlled intact-exposure study remains optional |
| §9.2 | Literal target and ground-truth containment overstate compliance/correctness | D06 approves model-judged clean quality with limited audit; retain marker proxies separately. Attack behavioral rubric and proxy limitations still need discussion |
| §9.1 | ISR has no defined value when no poison is retrieved | Emit N/A with denominator zero |
| §9.3 versus §8 | Poisoning count also changes cover diversity and possibly composition | D08 selects fixed N = 5 with no budget sweep or scaling claim; five distinct covers spanning the three recovery topics share one base instruction/directive; exact payload details remain pending, and results depend on the selected content |
| §§4.2, 9.3 | Adding concealment can change chunk boundaries and retrieval, not just generation | Compare document versions, chunk layouts, and exposure; avoid attributing all differences to concealment |
| §3.3 and existing README | Submitted tickets versus resolved tickets as the admission channel | Resolved by D04 scope approval: resolved tickets retain employee descriptions and technician resolutions; executable submission/resolution plus preloaded resolved tickets. Detailed workflow policy remains pending |
| §§3.4, 4.2, 9.2 | Same team can inadvertently tune attacker content on hidden victim queries/configuration | D08 approves restricted-brief authoring without a surrogate or victim feedback, followed by frozen evaluation; withhold actual development/held-out questions, corpus, and internals, and disclose same-team leakage |
| §§5.1, 13 | Models, storage, sizes, and revision pinning are placeholders | D10/D11 select stack, models, version policy and pilot bounds; account quotas, concrete pins/compatibility and measured feasibility remain unverified; disclose provider revision limitations |
| §11 | Spotlighting is phrased as though it guarantees instruction separation | Treat it as an empirical mitigation; compare security and answer quality in D08 selected conditions without claiming isolated clean-corpus utility preservation |
| §§5.2, 9.3, 11 | No fully explicit defended-clean run in the main condition list | D08 explicitly omits defended-clean due to time constraints; disclose that clean-corpus defense utility cost is not independently measured |
| §9.3 and §10 | References to §5.3 point to a nonexistent section | Interpret as §5.2; fix when revising the report |

## Change process

When implementation exposes a problem, retain a minimal reproducer or pilot trace, describe which claim or contract is affected, compare fixes, and seek user input for a major change. Update the decision record, plan, architecture, and affected experiment manifests together. Never silently change the threat model or weaken the baseline to obtain a successful attack.

## Review progress

D04 resolves the admission channel; D05 resolves grounded baseline/spotlighting separation and conversation/retrieval direction; D06 resolves clean scoring scope, dataset sizes, and initial repeatability/readiness targets; D07 resolves the chunk-integrity assumption; D08 selects three conditions and fixed N = 5 with five distinct covers sharing one base instruction/directive, explicitly omitting budget sweeps, defended-clean, and cover-only. Attack testing is primary; spotlighting is secondary.

D08 also approves restricted-brief authoring followed by frozen evaluation, with no surrogate or victim feedback during construction; same-team separation remains a disclosed procedural limitation.

The original detailed draft section 4.2 includes bounded attacker-side M_a verification without deployed-victim access. The submitted B1_Group_7.pdf omits that loop; the user now keeps M_a as optional future work only, not a required restoration or blocker. Although detailed-draft section 3.4 does not explicitly prohibit all clean-corpus reading, submitted section 3.1 (page 3) does exclude observation of D. This supports the recorded restriction. See [optional extensions](optional-extensions.md).

D08 now approves one answer per held-out question per condition for the initial study, with operational retries separate and variability limits disclosed.

Remaining explanation/decisions: exact payload/variant details; probability-factorization and zero-exposure interpretation; attack marker versus behavioral compliance/displacement; and concealment/repetition confounds if variants are run. Editorial section-reference repair applies when the original report is revised; the external PDF has not been edited.

## Deliberately deferred

Concrete dependency/image/model-artifact pins under D11, detailed attack authoring, spotlighting syntax, additional attack variants/repeats beyond the approved initial 30-question × three-condition single-answer comparison, exact inference quotas, and experimental results. Clean baseline sizes/repetitions are approved in D06; D11 now approves model IDs, runtime/version policy and pilot bounds. The remaining items need feasibility evidence, routine pinning or later user decisions; this draft does not present them as settled. Attacker-side model selection belongs only to the optional M_a extension, not the required study.

## Submitted-report reconciliation

B1_Group_7.pdf is the shortened nine-page submitted report, identified by the user as the reduced submission intended to avoid overpromising. Section 3.1 preserves the class-wide attack objective and explicitly excludes observation of the legitimate corpus. Section 3.3 retains distinct covers and a shared directive but has no M_a verification loop. Section 5.2 still proposes budget scaling and uses marker-based metrics and the simplified ASR identity; section 6 describes spotlighting. Later fixed-budget approvals and the existing measurement/utility limitations govern the implementation. Treat those remaining measurement issues as review items, not reasons to expand the experiment matrix. Neither source PDF was edited.
