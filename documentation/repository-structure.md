# Repository structure — approved direction, proposed details

Yes, subdirectories are useful: the victim application, research tooling, source data, and generated results have different responsibilities. Separate deployable projects are not inherently necessary. D03 approves one Python project with separate RAG, experiment, and evaluation packages and shared contracts/configuration. The `src/` layout below describes proposed implementation details.

Application files below remain proposed; current repository work consists of documentation/planning and session-orientation guidance. Other paths below are proposed and should be created when the corresponding task needs them, without empty placeholder packages.

```text
README.md
plans/
  draft-plan.md
documentation/
  README.md
  architecture.md
  project-status.md
  ...
  decisions.md
pyproject.toml                 # uv-managed single Python project
uv.lock                       # committed dependency lock
Dockerfile                    # approved delivery; exact image pending
compose.yaml                  # application + local Qdrant services
.env.example                   # variable names/placeholders only
.gitignore
src/injectrag/
  rag/
    contracts.py
    config.py
    ingestion.py
    chunking.py
    embeddings.py
    index.py
    retrieval.py
    context.py
    generation.py
    pipeline.py
    tracing.py
  tickets/                     # D04 lifecycle/admission; exact files pending
  api/                         # required from first working application
    app.py                     # FastAPI served by Uvicorn
    routes.py                  # request validation and pipeline calls
  web/                         # approved plain HTML/CSS/JavaScript UI
    templates/
    static/
  experiments/                 # later; snapshot/run orchestration
  evaluation/                  # observer-only model judge/audit, later attack scoring
  attacks/                     # later; attacker-side construction only
configs/
  baseline.<format>
prompts/
  baseline-system.txt
data/
  corpus/clean/                # authored synthetic articles and tickets
  queries/                    # development and frozen evaluation sets
  manifests/                  # document/query provenance and observer labels
  corpus/attacks/              # later, explicit condition-specific inputs
artifacts/                    # generated indexes/cache/run outputs; ignored
tests/
  fixtures/
  unit/
  integration/
  smoke/
```

## Dependency direction

Entry points and experiment orchestration call the RAG package. Evaluation consumes public trace contracts. RAG must not import attack construction, scoring, or held-out answers. Prefer small internal interfaces over a framework-heavy architecture unless feasibility evidence justifies the dependency.

The required API and simple chat UI belong in thin presentation packages. D10 approves FastAPI-served HTML/CSS/JavaScript assets using fetch and complete responses; streaming is deferred. A separate `apps/` project becomes useful when a frontend needs its own language, dependencies, build, or deployment; it is not required just to name the RAG system. Revisit D03 before creating such a project. Keep one source of truth for shared contracts. Rewriting belongs in the victim pipeline; judging remains observer-only. Model-provider interfaces may be shared without introducing a dependency from victim code on evaluation logic.

D10 selects SQLite via sqlite3 for application state and a separate local Qdrant Compose service for vector storage. One custom application image also runs one-off research commands; Qdrant uses its existing image. Persist application state, Qdrant data, snapshots/results, and model cache in separate host-mounted directories. D11 selects Python 3.12, model IDs, CPU FastEmbed/ONNX, google-genai and the version-pinning policy. Exact stable package/image/artifact pins will be resolved during authorized setup; paths and final schemas remain to specify; D12 settles application/retrieval/retry policies and whole-study limits; none of these application files exists yet.

## Tracking and generated files

Commit authored synthetic inputs, query definitions, prompts, configuration, manifests, and dependency lockfiles. Ignore credentials, downloaded embedding weights, embedding caches, indexes, temporary files, and bulk run output. Git-ignored does not mean disposable: retain trial requests/outputs and audit provenance in persistent storage outside container layers. Selected result artifacts may be exported deliberately with a manifest for coursework review. Do not assume local session metadata belongs in the software distribution.

## Staged creation

1. This change: documentation and plan only.
2. After local preflight under D13 (account checks gate hosted runs only): Python package, API/UI skeleton, dependency configuration, tests, and ignore rules.
3. With ingestion/baseline tasks: data, manifests, prompts, and runtime configurations.
4. At first execution: generated directories created by commands, never assumed to exist.
5. After clean baseline: attack and experiment tasks R18–R21 in the existing implementation plan.

D12 uses signed-cookie authentication without a SQLite sessions table. Keep accounts/tickets/threads/turns in application storage; publication bookkeeping is detailed in the [SQLite proposal](../sqlite-schema-plan.txt). No rewrite or reranker module is required. Persist phase/study usage counters and trial attempts in research artifacts across run restarts.

Implement only packages needed by the current delivery batch. The plan now includes R18–R21 for the fixed attack/defense; no separate general planning phase or second application is required.
