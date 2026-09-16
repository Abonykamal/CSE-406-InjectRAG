# InjectRAG — Indirect Prompt Injection via RAG

A corpus-poisoning content-manipulation attack against a Retrieval-Augmented
Generation (RAG) pipeline, and a lightweight spotlighting defense.

**CSE 406 — Computer Security Sessional · Group B1_7**

| Student ID | Name |
|---|---|
| 2105069 | Sheikh Iftikharun Nisa |
| 2105072 | Abony Kamal |
| 2105089 | Farhana Adri |

> **Status:** planning draft; implementation has not started. Major design choices
> remain open. See the [replacement implementation plan](plans/draft-plan.md),
> [project documentation](documentation/README.md), and
> [actual project status](documentation/project-status.md). The design report is
> revisable; the overview below describes research intent, not verified behavior.

**Joining the team?** Start with [teammate onboarding](documentation/team-onboarding.md) for the reading order, agreed scope, and remaining implementation decisions.

---

## Overview

RAG systems retrieve external documents and place them in an LLM's context to
ground its responses. If attacker-controlled content reaches the knowledge
corpus, it reaches the model's context too — creating an opening for **indirect
prompt injection**, where malicious instructions embedded in *retrieved* content
steer the model without ever appearing in the user's prompt.

The primary research goal is to test that attack in a simulated corporate IT helpdesk chatbot; spotlighting is a secondary comparison.
An attacker with legitimate permission to submit support content embeds
model-directed instructions in a document they control. When that document is
retrieved for a related user query, the instruction attempts to induce an
attacker-chosen misleading response.

The attacker has no access to the system prompt, the models, the retrieval
mechanism, or any other internal component.

The approved delivery direction is Docker with local embeddings/retrieval and
hosted generation through Google's Gemini API. Generation uses a replaceable
provider interface; trial requests, outputs, and provenance will be retained.
The approved stack is FastAPI/Uvicorn, a plain HTML/CSS/JavaScript UI served by the API,
uv with a committed lockfile, SQLite application/history storage, and local Qdrant.
Docker Compose runs the application and Qdrant as two services with persistent host storage.
Selected models: CPU BAAI/bge-small-en-v1.5 via FastEmbed/ONNX; Gemini
`gemini-3.8-flash` for answers and separate observer judging;
`gemini-3.5-flash-lite` for rewriting. Python 3.12, a reproducible version-pinning
policy, and bounded pilot design are approved. Account quotas, compatibility and
measured feasibility remain unverified; no execution has started. See
[runtime feasibility](documentation/local-runtime-feasibility.md) and [D11](documentation/decisions.md#d11).

The initial clean dataset is 12 articles and 24 resolved tickets, with 30 development
and 30 held-out questions plus six separate conversation scripts. Model-judged
quality is checked with a limited human audit; approved readiness thresholds and
repetitions are in [D06](documentation/decisions.md#d06). These are planned inputs,
not existing data or results.

Follow-ups use full same-thread user/assistant history without routine trimming.
Retrieval searches both the current question and a model-generated standalone
rewrite; rewrite failure triggers logged original-question retrieval. Fresh evidence
precedes the current question in the answer request. Prior retrieval bundles are
retained in artifacts rather than replayed as history. Exact settings remain pending.

## System Model

A user query drives retrieval from an internal knowledge corpus; the retrieved
content is combined with the query and the trusted system instructions to form
the LLM input. Separately, submitted support content enters the corpus through an
ingestion pipeline.

| Component | Function |
|---|---|
| Ingestion pipeline | Adds support content to the knowledge corpus |
| Knowledge corpus | Stores IT documentation and support-related content |
| Retriever | Selects content relevant to the user's query |
| Application | Handles retrieval and constructs the LLM input |
| System instructions | Define the chatbot's intended role and behavior |
| LLM | Generates the response |
| User | Submits queries and receives responses |

### Trust boundary

System instructions constructed by the application are **trusted**. Documents
retrieved from the corpus are **untrusted**. Both converge in the LLM context.
The attacker reaches the corpus through a legitimate document channel; the attack
tests whether untrusted content can cross this boundary and be read as
*instruction* rather than *data*.

## Threat Model

Let `D` be the legitimate corpus and `S` the application's trusted system
instruction. For a query `q`, the system retrieves top-k documents `E(q; D)` and
returns `r = LLM(S, q, E(q; D))`. This notation describes fresh-thread trials;
conversation history and original-plus-rewritten retrieval are explicit extensions
for multi-turn tests, whose results are reported separately.

The attacker targets a **query class** `Q` — semantically related questions
victims are expected to ask — and fixes one target directive `R` to be induced
across the entire class. Because `q` is unobservable, `R` must be class-invariant
rather than question-specific.

The attacker injects `N` documents `Γ = {P₁, …, P_N}` through the legitimate
ingestion channel, yielding corpus `D ∪ Γ`. D08 fixes the poisoning budget at
`|Γ| = N = 5` admitted attacker tickets; no budget sweep is selected. The attacker maximizes:

```
max_Γ  E_{q~Q} [ 1( R ∈ LLM(S, q, E(q; D ∪ Γ)) ) ]
```

i.e. choose the poisoned documents that make the system emit the injected
directive for the largest fraction of questions in the target class.

**Attacker capability.** Controls only `Γ`. Cannot alter or observe `S`, `D`, the
encoders, or the victim's query. May know that this target uses chunking and vary
instruction repetition/placement without access to hidden boundaries or configuration.
Never prompts the victim LLM directly, never interacts
with the victim, never submits the victim's query. D08 approves authoring from a
restricted brief (target topics, description permissions, general chunking knowledge,
and attack objective), without a surrogate or victim feedback. Keep clean corpus
contents, victim prompts/configuration, actual development/held-out questions and
keys, and victim traces outside attack construction. Freeze the five tickets before
evaluation; observer analysis does not feed back into the frozen attack. Same-team
separation is procedural, not guaranteed blindness. The submitted report
(`B1_Group_7.pdf`, section 3.1) explicitly excludes observing the clean corpus.
Attacker-side model verification M_a is an [optional extension](documentation/optional-extensions.md),
not a requirement or an implementation blocker.

**Two necessary conditions:**

1. **Retrieval condition** — at least one `P ∈ Γ` must appear in `E(q; D ∪ Γ)`,
   or the injected instruction never reaches the model.
2. **Injection condition** — given `P` is retrieved, the LLM must follow `I` in
   preference to `S` and to the legitimate evidence `E(q; D ∪ Γ) ∩ D`.

## Attack Scenario

A simulated corporate IT helpdesk chatbot used by employees for common
procedures — password resets, account lockouts, VPN access — running a RAG
pipeline over official IT documentation and support content.

The initial application will support executable ticket submission and resolution,
alongside preloaded synthetic resolved tickets. Employee descriptions and technician
resolutions remain distinguishable; only resolved tickets are eligible for ingestion.
Seeded local employee/technician accounts and API-enforced role/ownership checks
are approved. SQLite persistence is selected; exact sessions, edit/reopen rules, and index publication
policy remain pending under D04.

Employees can submit IT support tickets, and resolved tickets are ingested into
the corpus alongside official documentation in this simulated setting. Resolved
tickets retain employee descriptions and technician resolutions. Admission and
normalization apply consistently; no instruction-level filter is selected for
the baseline. This does not simulate evasion of a real ticket-review process.

The attacker is a malicious employee controlling their own ticket description,
not technician resolution text, resolved status, or official articles. The study
assumes this description survives resolution and admission; exact edit rules
remain pending.

```
attacker-controlled document → ingestion into corpus → retrieval for a victim query
    → inclusion in the LLM context → model-directed behaviour
```

Two temporally separate phases:

| Phase | Actor | Activity |
|---|---|---|
| Preparation | Attacker | Submits malicious documents through the legitimate ticket channel |
| Execution | Victim / RAG system | Victim independently asks `q ∈ Q`; the retriever returns legitimate documentation and, under successful attack conditions, at least one `P ∈ Γ` |

## Payload Structure

Each malicious document is `P = C ⊕ I` — cover content plus model-directed
instruction — embedded in plausible support text rather than a separate control
field, so the instruction reaches the LLM through content the system retrieves as
data.

| Part | Symbol | Purpose |
|---|---|---|
| Cover content | `C` | IT support text using terminology from `Q`, so the document has a reason to be retrieved |
| Injection instruction | part of `I` | Addresses the assistant, directs it to attacker-specified behaviour for queries in `Q` |
| Target directive | part of `I` | The class-invariant directive `R`, carrying a distinctive literal string for deterministic matching |
| Concealment instruction | part of `I` *(optional)* | Attempts to stop the model revealing that retrieved content influenced the response |

D08 approves one fixed set of **five distinct support stories** spanning forgotten
passwords, account lockouts, and lost verification devices. All five share the same
base injection instruction and target directive `R`, with varied cover content `C`
to broaden retrieval opportunities. Freeze the set before final evaluation and use
the same tickets in attacked and defended runs. Exact wording, topic allocation,
repetition, placement, and concealment remain pending. D07 permits repetition/placement
without hidden-boundary feedback, with chunking frozen independently of the attack.

An example document for the password-recovery class appears in Appendix A of the
design report. Its target directive carries the literal string
`it-support-portal.example.com`, which is the token matched during evaluation.

## Evaluation

The metrics separate retrieval effectiveness from instruction-following
effectiveness, so a failed attack can be investigated at each stage. The selected
study evaluates a fixed five-ticket attack budget; it does not measure scaling with `N`.
D08 approves one answer per held-out question per condition: 30 clean, 30 attacked,
and 30 defended answers for the initial comparison. Reuse clean results only with
matching frozen configuration. Target attack rates use the 18 answerable recovery
questions; the other 12 assess broader answer behavior. Report single-answer
variability limits and operational retries separately; never rerun a completed answer
just because the attack failed.

| Metric | Definition |
|---|---|
| **RSR** (Retrieval Success Rate) | Fraction of victim queries for which at least one attacker document appears in the top-k context |
| **ISR** (Injection Success Rate) | Fraction of *retrieved* trials in which the response contains `R` |
| **ASR** (Attack Success Rate) | Fraction of *all* trials whose response contains `R` |
| **ASR-exclusive** | Fraction of all trials whose response contains `R` **and not** the ground-truth answer |
| **Clean Accuracy** | Fraction of benign queries answered correctly, measured separately in each condition (clean / attacked / defended) |

ASR is the primary end-to-end marker metric. **ASR = RSR × ISR** holds only
when target-marker matches do not occur without attacker content reaching the
model. Record actual context exposure separately from top-k retrieval. Literal
marker containment is a proxy: quotation, warnings, and paraphrases require
care when interpreting compliance or displacement. See the
[evaluation specification](documentation/evaluation.md) for precise definitions.

## Defense: Spotlighting

A lightweight defense acting at context-construction time, between retrieval and
generation, without modifying the corpus or the model:

```
r = LLM( Def(S, q, E(q; D ∪ Γ)) )
```

The application marks retrieved documents as untrusted data and instructs the
model to treat them as reference material rather than instructions. The intended effect is to reduce instruction-following from retrieved content
while preserving its use as evidence; effectiveness must be measured.

Spotlighting adds no extra model, classifier, or external dependency — it changes
only how retrieved context is formatted and labelled, plus one handling rule in
the system instruction.

Evaluated on two axes by comparing defended and undefended runs under identical
attack conditions:

- **Security** — reduction in ASR and ASR-exclusive
- **Answer quality under attack** — correctness on benign user questions against the poisoned corpus

D08 selects clean baseline, attacked baseline, and defended attack only, with
36 clean documents and 41 documents in each poisoned snapshot (five added attacker tickets). No budget sweep,
defended-clean or cover-only run is included. Consequently, the study does not
isolate defense utility cost on a clean corpus or fully separate added-document
competition from embedded-instruction effects.

## Implementation Plan

The previous phase checklist is superseded by the
[replacement RAG-first draft](plans/draft-plan.md). It breaks the clean target
system into dependency-ordered implementation tasks with deliverables,
acceptance checks, and explicit user decision gates.

Start with the [documentation index](documentation/README.md),
[proposed architecture](documentation/architecture.md),
[repository layout](documentation/repository-structure.md), and
[pending decisions](documentation/decisions.md).

The shortened submitted report is `B1_Group_7.pdf`; the earlier detailed report
is a historical proposal. Current approvals govern implementation. Neither report
is a portable repository dependency. The detailed report is a proposal subject to revision. Its experimental assumptions
and metric limitations are tracked in the [design review](documentation/design-review.md)
and [evaluation specification](documentation/evaluation.md).

## Scope and Ethics

This is coursework for CSE 406, conducted entirely against a **self-contained,
simulated** IT helpdesk corpus built by the authors. No real system, service, or
organization is targeted, and no live corpus is poisoned. The distinctive string
used as the target directive (`it-support-portal.example.com`) is a reserved
example domain chosen so that attack success can be matched deterministically
without pointing at anything real.

The planned study pairs the attack with a spotlighting defense; neither is
implemented yet. The purpose is to measure
whether the trust boundary between system instructions and retrieved content
holds, and how a formatting-level mitigation changes attack success and answer
quality under poisoning. Clean-corpus defense utility is outside the selected comparison.
