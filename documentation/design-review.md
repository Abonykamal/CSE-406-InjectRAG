# Review of the detailed design report

The report defines the study's intent but leaves implementation choices open. The following are analysis and proposed corrections, not approved replacements for major design decisions. No external literature verification was performed in this documentation pass.

| Report location | Issue or ambiguity | Proposed treatment |
|---|---|---|
| §5.1 | Temperature zero is described as ensuring deterministic output without repeated trials | Record all generation settings; run a repeatability pilot and qualify reproducibility claims |
| §9.1 | ASR factorization assumes marker matches cannot happen without retrieval | Use the conditional identity in evaluation documentation; measure non-exposure matches |
| §§4.4, 5.2, 10 | Correct evidence in corpus is treated as correct evidence in the assembled context | Log corpus availability, top-k presence, and actual context inclusion separately |
| §§4.2, 5.1 versus §3.4 | Guaranteed instruction chunk integrity assumes control/knowledge the black-box attacker does not have | Do not customize victim chunking for payloads; decide observer measurement versus a labeled controlled study at D07 |
| §9.2 | Literal target and ground-truth containment overstate compliance/correctness | Retain marker proxies; audit negations, quotations, paraphrases, and contradictions before behavioral claims |
| §9.1 | ISR has no defined value when no poison is retrieved | Emit N/A with denominator zero |
| §9.3 versus §8 | Poisoning count also changes cover diversity and possibly composition | Agree set construction at D08; report confounds and repeat balanced sets if feasible |
| §§4.2, 9.3 | Adding concealment can change chunk boundaries and retrieval, not just generation | Compare document versions, chunk layouts, and exposure; avoid attributing all differences to concealment |
| §3.3 and existing README | Submitted tickets versus resolved tickets as the admission channel | Choose the simulated admission semantics under D04 |
| §§3.4, 4.2, 9.2 | Same team can inadvertently tune attacker content on hidden victim queries/configuration | Separate attacker development material, frozen evaluation queries, and observer traces; document any leakage |
| §§5.1, 13 | Models, storage, sizes, and revision pinning are placeholders | Choose after approved resource feasibility work; disclose provider revision limitations |
| §11 | Spotlighting is phrased as though it guarantees instruction separation | Treat it as an empirical mitigation; compare both security and utility |
| §§5.2, 9.3, 11 | No fully explicit defended-clean run in the main condition list | Include clean/defended to assess utility cost independently |
| §9.3 and §10 | References to §5.3 point to a nonexistent section | Interpret as §5.2; fix when revising the report |

## Change process

When implementation exposes a problem, retain a minimal reproducer or pilot trace, describe which claim or contract is affected, compare fixes, and seek user input for a major change. Update the decision record, plan, architecture, and affected experiment manifests together. Never silently change the threat model or weaken the baseline to obtain a successful attack.

## Deliberately deferred

Exact libraries/model versions, detailed attack authoring, attacker-side model selection, spotlighting syntax, sample sizes, inference costs, and experimental results. These need feasibility evidence or later user decisions; this draft does not present them as settled.
