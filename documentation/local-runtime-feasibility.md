# Runtime feasibility — local retrieval and hosted generation

Status: Gemini API generation, Docker delivery, and local embeddings/retrieval approved. Hardware inventory and reference-code inspection only; D10 selects the application stack and two-service Qdrant layout; D11 closes model/runtime selection, version policy and pilot design. Actual account quotas, concrete pins, compatibility and measured feasibility remain unverified; execution is not authorized.

## User constraints and observed environment

The user identifies the machine as an ASUS Zenbook running Linux and has selected hosted Gemini generation with local embeddings/retrieval, replacing the earlier preference for local generation. Read-only inspection in the current workspace on 2026-09-13 reported:

| Resource | Observed value |
|---|---|
| CPU | Intel Core i7-12700H, 14 cores / 20 logical CPUs, x86-64 |
| Graphics | Intel Alder Lake-P GT2 / Iris Xe Graphics |
| RAM | Approximately 15 GiB total as reported by `free -h` |
| Available RAM | Approximately 6.9 GiB at inspection; varies with other applications |
| Swap | 4 GiB configured; not counted as a model performance budget |
| Workspace filesystem | Approximately 180 GiB available at inspection |

Evidence commands: `lscpu`, `free -h`, `df -h .`, and `lspci` filtered for graphics devices. No dedicated graphics-memory capacity, inference-backend compatibility, throughput, or usable acceleration was established by this inventory.

## Verification work after execution authorization

1. Verify access and active free-tier quotas for the D11 selected Gemini models in the intended account; public pricing is not an account allowance. No paid usage is approved.
2. Verify D11 BGE-small/FastEmbed/ONNX CPU compatibility with Python 3.12 and the approved local Qdrant stack. Record model revision, download size, pinned application/Qdrant image versions, and resource estimates separately from observations.
3. Measure local memory with the application, browser, embeddings, and index present. No local generator benchmark is required.
4. Measure startup, indexing, retrieval, and end-to-end Gemini answer latency. Use D06 quality targets/repetitions and D11 pilot ceilings/latency target. Include separately configured rewrite and observer-judge API usage in the resource estimate.
5. Verify bounded request concurrency, timeout/retry handling, rate-limit reporting, and API/UI responsiveness. Do not silently switch providers or use paid fallback.
6. Implement Gemini behind a provider-independent interface; record supported and unsupported options explicitly. A later provider change requires a separately identified baseline.
7. Retain sanitized requests, returned outputs/metadata, attempts/errors, timings, and configuration/input identities in persistent artifacts. Validate real generation and local retrieval together in Docker.

No models or dependencies were downloaded for this planning update. D10 selects the framework/storage/tooling; D11 selects models and a version-pinning policy; concrete dependency/image/artifact pins and runtime performance remain unverified.

## Docker expectation and reference chatbot inspection — 2026-09-16

The user expects Docker-based delivery. Container packaging and inference location are separate decisions: a containerized application may call either a local model service or a hosted API. Containers still consume host resources; the approved application, embeddings, and Qdrant need the planned memory/latency pilot. D10 subsequently selects the two-service layout; exact image digests will be pinned during authorized setup under D11. Background: [Docker container concepts](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/).

Read-only inspection of `/home/abony-kamal/Documents/BUET-Job-Portal` found:

- `plugins/chatbot/Dockerfile`: Python 3.11 slim application image running FastAPI through Uvicorn.
- `deploy/compose.chatbot.yml`: chatbot application and a separate Qdrant service, with persistent model-cache and vector-storage volumes.
- `plugins/chatbot/app/services/embedding_service.py` and `app/config.py`: local FastEmbed embeddings, default `BAAI/bge-small-en-v1.5`.
- `plugins/chatbot/app/services/llm.py`: generation through the hosted Groq SDK; source default model `openai/gpt-oss-20b`. Active environment overrides were not inspected.
- `plugins/chatbot/app/graph/nodes/faq_node.py`: retrieves three FAQ passages, supplies the last four history messages, and requests a grounded answer. Retrieved text is interpolated into the system message; InjectRAG must preserve its own approved trust boundaries instead of copying that placement.

This is source/configuration evidence, not a running-system benchmark. No reference services were started or changed, and no secrets were read. The reference provides useful packaging, embedding/retrieval, and provider-interface patterns. Its hosted generation does not establish local-generation feasibility for InjectRAG. The subsequent D02 revision selects Gemini generation with local embeddings; do not adopt the reference's provider, model, dependencies, or versions automatically. The sibling checkout is not a required project dependency.

## Application stack approval — 2026-09-17

D10 approves FastAPI/Uvicorn with one initial worker, a FastAPI-served HTML/CSS/JavaScript UI using fetch and complete responses, uv with pyproject.toml and a committed uv.lock, SQLite through Python sqlite3 for accounts/tickets/threads/turns, and local Qdrant for vectors and chunk metadata. Docker Compose runs two services: one custom application image and the existing Qdrant image, with separate persistent host mounts for application state, Qdrant data, snapshots/results, and model cache. Research commands use the application image as one-off jobs.

This is design approval, not runtime evidence or permission to provision. Include both containers in memory measurements; one Uvicorn worker does not set an inference-concurrency limit. D11 selects Python 3.12 and CPU FastEmbed/ONNX; compatible stable packages and image digests will be pinned during authorized setup. Keep current model availability and published free-tier limits distinct from authenticated account quotas; no account quota or performance has been verified. See [D10](decisions.md#d10) for rationale and official stack references.

## Model and pilot approval — 2026-09-17

D11 selects BAAI/bge-small-en-v1.5 through FastEmbed/ONNX Runtime on CPU, Gemini gemini-3.8-flash for answers and separate observer judging, and gemini-3.5-flash-lite for independently configured rewriting. Use google-genai, Python 3.12, low thinking for answers/judging and minimal thinking for rewriting. Resolve compatible stable dependencies during authorized setup, commit exact uv.lock versions, pin Docker images by digest, and record embedding revisions/hashes before baseline freeze.

The embedding model uses 384 dimensions and a 512-token input limit; include prefixes/special tokens in that limit and detect overlength input. Sibling chatbot reinspection confirms the same default and lazy cached loading via qdrant-client[fastembed]; it is source evidence only, not performance evidence. No PyTorch/CUDA or local generator is required.

| Pilot item | Approved design bound |
|---|---|
| Clean answers | Five development questions × three answers = 15 planned answers (existing D06 repeatability scope) |
| Judge requests | Judge the 15 answers plus five fabricated validation cases = 20 planned requests |
| Rewrite requests | Five fixed follow-up validation cases, separate from the six conversation scripts |
| Inference total | 40 planned requests plus at most five retry attempts = 45 maximum |
| All API requests | 100 maximum including inference, token counting, and metadata checks |
| Input | At most 8,192 tokens per request, including instructions, evidence, history and formatting |
| Output | At most 4,096 tokens for answers/judging; 512 for rewriting; account for provider thinking-token behavior |
| Model concurrency | One model request at a time |
| Retries | At most one retry per failed request, within the shared five-attempt retry allowance |
| Attempt timeout | 90 seconds for answers/judging; 30 seconds for rewriting |
| Container memory ceiling | Application 4 GiB, Qdrant 1 GiB; recheck available host resources before execution |
| Operational target | Median answer latency at most 30 seconds excluding deliberate quota waits, complete traces and responsive readiness checks |

These are pilot ceilings/targets, not measured consumption or blanket full-study authorization. The 4 GiB application ceiling covers the whole container, not expected embedding memory. Preserve cumulative request/attempt counts across resumes, stop on exhaustion, and record explicit oversized/truncated/failed outcomes without silent history trimming. Retain the D05 rewrite fallback. Full-study aggregate budgets and remaining application policies are separate. The five rewrite fixtures do not replace the six conversation scripts; the pilot does not replace held-out readiness. See [D11](decisions.md#d11) for approval and official sources.

Public official pages reviewed on 2026-09-17 list free-tier text input/output for both selected Gemini endpoints, with active numerical quotas directed to AI Studio. Account access, RPM/TPM/RPD and available capacity remain unverified. Answer and judge traffic share gemini-3.8-flash quota. Ninety answers plus one judgment each means 180 planned inference requests; compatible reuse of 30 clean answers and judgments leaves 120 additional requests. Other development/scripts/retries/auxiliary calls add usage; these counts do not authorize execution.

## Hosted generation — accepted direction

Hosted generation can preserve the corpus-poisoning/spotlighting research objective: keep ingestion, embeddings, retrieval, context construction, and observer traces under application control, and send the assembled request to a fixed API model. Use the same model and settings in paired clean/poisoned and defended/undefended conditions. Provider safeguards are part of the measured target; results do not isolate a bare model. Model retirement, backend changes, quotas, network availability, and request costs constrain repeatability and experiment scheduling. Local execution also needs repeatability checks.

The user approved Gemini generation through a replaceable provider adapter, Docker delivery, local embeddings/retrieval, and retained trial artifacts. D11 selects the exact models and pilot design; paid usage is not approved. Free-tier sufficiency must be verified for the selected account/model. Provider selection should test clean quality and resource/cost limits rather than select a model because an attack succeeds.

Current primary references: [Groq reproducibility guidance](https://console.groq.com/docs/prompting), [model deprecations](https://console.groq.com/docs/deprecations), and [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).
