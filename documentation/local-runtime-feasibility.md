# Local runtime feasibility

Status: hardware inventory only; no model benchmark or runtime selection completed.

## User constraints and observed environment

The user identifies the machine as an ASUS Zenbook running Linux and prefers local generation and embeddings. Read-only inspection in the current workspace on 2026-09-13 reported:

| Resource | Observed value |
|---|---|
| CPU | Intel Core i7-12700H, 14 cores / 20 logical CPUs, x86-64 |
| Graphics | Intel Alder Lake-P GT2 / Iris Xe Graphics |
| RAM | Approximately 15 GiB total as reported by `free -h` |
| Available RAM | Approximately 6.9 GiB at inspection; varies with other applications |
| Swap | 4 GiB configured; not counted as a model performance budget |
| Workspace filesystem | Approximately 180 GiB available at inspection |

Evidence commands: `lscpu`, `free -h`, `df -h .`, and `lspci` filtered for graphics devices. No dedicated graphics-memory capacity, inference-backend compatibility, throughput, or usable acceleration was established by this inventory.

## Proposed pilot requirements

1. Select a small shortlist of CPU-compatible local generation and embedding candidates, checking current primary documentation before making concrete software recommendations.
2. Present exact model/revision, weight format/quantization where applicable, runtime, download size, resource estimates, and bounded test inputs for approval. Record estimates separately from measurements.
3. Measure peak memory with the API, browser UI, embedding runtime, and generator together. Decide sequential loading or shared residency based on observed memory, not total installed RAM alone.
4. Measure startup, indexing, retrieval, and full answer latency on the same clean development questions. Agree acceptable latency and clean quality under D06.
5. Verify a bounded request policy and responsiveness during generation. Do not assume multiple server workers can each load a model within this laptop's budget.
6. Treat Iris acceleration as an optional separately verified candidate. Record runtime/driver/device details if tested; retain a measured CPU path where feasible.
7. Record feasibility failures and alternatives. Hosted execution requires a subsequent user decision.

No models or dependencies were downloaded for this planning update. Exact model/framework choices and runtime performance remain unresolved.
