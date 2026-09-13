# Repository structure — approved direction, proposed details

Yes, subdirectories are useful: the victim application, research tooling, source data, and generated results have different responsibilities. Separate deployable projects are not inherently necessary. D03 approves one Python project with separate RAG, experiment, and evaluation packages and shared contracts/configuration. The `src/` layout below describes proposed implementation details.

Only `plans/` and `documentation/` are created in this documentation change. Other paths below are proposed and should be created when the corresponding task needs them, without empty placeholder packages.

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
pyproject.toml                 # one approved Python project; tooling to select
<selected lockfile>
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
  api/                         # required from first working application
    app.py                     # framework selected after proposal/approval
    routes.py                  # request validation and pipeline calls
  web/                         # proposed Python-served UI; confirmation pending
    templates/
    static/
  experiments/                 # later; snapshot/run orchestration
  evaluation/                  # baseline scoring first, attack scoring later
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

The required API and simple chat UI belong in thin presentation packages. The current recommendation is a Python-served page with HTML/CSS/JavaScript assets; this delivery choice is pending confirmation. A separate `apps/` project becomes useful when a frontend needs its own language, dependencies, build, or deployment; it is not required just to name the RAG system. Revisit D03 before creating such a project. Keep one source of truth for shared contracts.

## Tracking and generated files

Commit authored synthetic inputs, query definitions, prompts, configuration, manifests, and dependency lockfiles. Ignore credentials, downloaded model weights, embedding caches, indexes, temporary files, and bulk run output. Selected result artifacts may be exported deliberately with a manifest for coursework review. Do not assume local session metadata belongs in the software distribution.

## Staged creation

1. This change: documentation and plan only.
2. After exact runtime/framework choices: Python package, API/UI skeleton, dependency configuration, tests, and ignore rules.
3. With ingestion/baseline tasks: data, manifests, prompts, and runtime configurations.
4. At first execution: generated directories created by commands, never assumed to exist.
5. After clean baseline: attack and experiment packages under a separate approved plan.
