# Corpus and clean baseline

Status: proposed; D04 and D06 approve scope and readiness criteria before data authoring and baseline freeze.

## Authoring sequence

1. Select the fictional organization's procedures and one initial target query class. Proposed starting class: password/account recovery, with VPN and other helpdesk topics as distractors.
2. Write a compact canonical policy sheet with correct steps, approved fictional endpoints, identity-check requirements, and cases requiring escalation. All documents and answer keys derive from this sheet.
3. Author official articles and ordinary resolved tickets with varied wording and lengths. Include repeated terminology and some irrelevant but plausible material. Document counts and proportions require D06; do not invent a representative production corpus claim.
4. Validate that tickets agree with policy unless a conflict is deliberately labeled in a development fixture. Define whether admission requires a resolved ticket (the README's assumption) or merely a submission (the report's assumption).
5. Create development questions for answerable, ambiguous, unsupported, paraphrased, and adjacent-topic cases. Give answerable questions relevant document IDs and accepted answer facts.
6. Create a disjoint held-out set before final evaluation. Group near-duplicate/paraphrase families to avoid leakage. Freeze it and its answer key before tuning attack content; repository separation is a procedural research boundary, not an access-control guarantee.
7. Check the clean corpus and clean prompts do not contain the later attack target marker. Record this as a check, not proof that a generator cannot emit that string independently.

## Baseline progression

Use tiny hand-inspectable fixtures to debug plumbing, then a real-model pilot on development data to inspect retrieval relevance, context fit, answer quality, latency, and resource use. Do not tune against the held-out baseline results. Freeze corpus, query split, prompts, chunking, model identities, and retrieval settings after the approved pilot.

Retrieve without consulting expected answers. Score retrieval relevance separately from answer correctness so retrieval failures are not confused with generation failures. Preserve poor results rather than editing evidence to manufacture readiness. Report marker containment separately from semantic correctness and review contradictions, warnings, and refusals.

## M4 readiness gate

D06 must record numeric retrieval and answer-quality targets, the allowed failure/resource budget, pilot repetitions, and the query/corpus counts. The baseline is ready when these agreed checks pass and a fresh checkout can reproduce the documented run within declared nondeterminism. If they do not pass, investigate on development data and record any redesign. No arbitrary threshold is silently adopted by the implementation agent.
