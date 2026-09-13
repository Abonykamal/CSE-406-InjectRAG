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

---

## Overview

RAG systems retrieve external documents and place them in an LLM's context to
ground its responses. If attacker-controlled content reaches the knowledge
corpus, it reaches the model's context too — creating an opening for **indirect
prompt injection**, where malicious instructions embedded in *retrieved* content
steer the model without ever appearing in the user's prompt.

This project studies that attack in a simulated corporate IT helpdesk chatbot.
An attacker with legitimate permission to submit support content embeds
model-directed instructions in a document they control. When that document is
retrieved for a related user query, the instruction attempts to induce an
attacker-chosen misleading response.

The attacker has no access to the system prompt, the models, the retrieval
mechanism, or any other internal component.

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
returns `r = LLM(S, q, E(q; D))`.

The attacker targets a **query class** `Q` — semantically related questions
victims are expected to ask — and fixes one target directive `R` to be induced
across the entire class. Because `q` is unobservable, `R` must be class-invariant
rather than question-specific.

The attacker injects `N` documents `Γ = {P₁, …, P_N}` through the legitimate
ingestion channel, yielding corpus `D ∪ Γ`. Subject to a poisoning budget
`|Γ| = N`, the attacker maximizes:

```
max_Γ  E_{q~Q} [ 1( R ∈ LLM(S, q, E(q; D ∪ Γ)) ) ]
```

i.e. choose the poisoned documents that make the system emit the injected
directive for the largest fraction of questions in the target class.

**Attacker capability.** Controls only `Γ`. Cannot alter or observe `S`, `D`, the
encoders, or the victim's query. Never prompts the LLM directly, never interacts
with the victim, never submits the victim's query.

**Two necessary conditions:**

1. **Retrieval condition** — at least one `P ∈ Γ` must appear in `E(q; D ∪ Γ)`,
   or the injected instruction never reaches the model.
2. **Injection condition** — given `P` is retrieved, the LLM must follow `I` in
   preference to `S` and to the legitimate evidence `E(q; D ∪ Γ) ∩ D`.

## Attack Scenario

A simulated corporate IT helpdesk chatbot used by employees for common
procedures — password resets, account lockouts, VPN access — running a RAG
pipeline over official IT documentation and support content.

Employees can submit IT support tickets, and resolved tickets are ingested into
the corpus alongside official documentation. This is common practice in helpdesk
knowledge bases, since past tickets capture fixes that formal documentation
omits. Ingestion is assumed to screen content for plausibility but perform **no
instruction-level inspection**.

The attacker is a malicious employee with legitimate permission to submit or
modify their own ticket content, placing the payload inside otherwise plausible
IT support text.

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

The `N` injected documents share the same injection instruction and target
directive `R`, but use **distinct cover content** `C`, each written around a
different sub-topic of `Q`. This broadens retrieval coverage of the class rather
than concentrating probability on a single phrasing.

An example document for the password-recovery class appears in Appendix A of the
design report. Its target directive carries the literal string
`it-support-portal.example.com`, which is the token matched during evaluation.

## Evaluation

The metrics separate retrieval effectiveness from instruction-following
effectiveness, so a failed attack can be attributed to a specific stage, and
measure how effectiveness scales with the poisoning budget `N`.

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
- **Utility** — preservation of Clean Accuracy on benign queries

## Implementation Plan

The previous phase checklist is superseded by the
[replacement RAG-first draft](plans/draft-plan.md). It breaks the clean target
system into dependency-ordered implementation tasks with deliverables,
acceptance checks, and explicit user decision gates.

Start with the [documentation index](documentation/README.md),
[proposed architecture](documentation/architecture.md),
[repository layout](documentation/repository-structure.md), and
[pending decisions](documentation/decisions.md).

The detailed report is a proposal subject to revision. Its experimental assumptions
and metric limitations are tracked in the [design review](documentation/design-review.md)
and [evaluation specification](documentation/evaluation.md).

## Scope and Ethics

This is coursework for CSE 406, conducted entirely against a **self-contained,
simulated** IT helpdesk corpus built by the authors. No real system, service, or
organization is targeted, and no live corpus is poisoned. The distinctive string
used as the target directive (`it-support-portal.example.com`) is a reserved
example domain chosen so that attack success can be matched deterministically
without pointing at anything real.

The attack is documented alongside a working defense; the purpose is to measure
whether the trust boundary between system instructions and retrieved content
holds, and whether a formatting-level mitigation improves it while preserving utility.
