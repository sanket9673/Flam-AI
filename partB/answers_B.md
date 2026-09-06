# Capacity & KV-Cache Forensic Audit Report (Part B)

**Target Model**: FLM-4B (4.2B dense parameters, 28 layers, GQA with 8 KV heads, head dimension 128, fp16 precision)  
**Target Hardware**: 1x NVIDIA L4 (24 GB VRAM, `gpu_memory_utilization = 0.92`, Usable VRAM = 22.08 GB, Non-KV Overhead = 1.60 GB)  
**Audit Artifact**: `starter_kit/bench/bench_log.csv` & `starter_kit/REPORT_v0.md`  

---

## 1. KV-Cache Signature

Using first-principles transformer memory arithmetic:

$$\text{KV Cache Bytes per Token} = 2 \times \text{layers} \times \text{num\_kv\_heads} \times \text{head\_dim} \times \text{bytes\_per\_element}$$

$$\text{KV Cache Bytes per Token} = 2 \times 28 \times 8 \times 128 \times 2 = 114,688 \text{ bytes/token}$$

- **Exact Value**: **114,688 bytes/token**
- **In Binary Kilobytes**: **112.00 KiB / token** ($114,688 / 1024$)
- **In Decimal Kilobytes**: **114.69 KB / token** ($114,688 / 1000$)

### Memory Allocation Breakdown:
- **Total Usable VRAM (0.92 limit)**: $24.00 \times 0.92 = 22.08 \text{ GB}$ ($22,080,000,000\text{ bytes}$)
- **Static Model Weights (fp16)**: $4.2 \times 10^9 \times 2 = 8.40 \text{ GB}$ ($8,400,000,000\text{ bytes}$)
- **Non-KV Runtime Overhead** (activations, CUDA graphs, workspaces): $1.60 \text{ GB}$ ($1,600,000,000\text{ bytes}$)
- **Remaining KV-Cache Budget**: $22.08 - 8.40 - 1.60 = \mathbf{12.08 \text{ GB}}$ ($12,080,000,000\text{ bytes}$)
- **Total KV-Cache Capacity**: $12,080,000,000 / 114,688 = \mathbf{105,329 \text{ tokens}}$
- **Max Full-Length (4096-token) Concurrency Ceiling**: $105,329 / 4096 = \mathbf{25.71 \rightarrow 25 \text{ concurrent streams}}$

---

## 2. The Hallucination: Why Linear Scaling to 3200 tok/s is Impossible

### The Intern's Flawed Projection in `REPORT_v0.md`:
> *"For capacity planning, assume ~1600 tok/s per L4 (best observed) and scale linearly with batch size, so batch 48 should give us ~3200 tok/s."*

### Forensic Breakdown of the Failure:
1. **Saturation at Batch 24**:
   - At Batch 24 with Prompt 3584 + Gen 512 ($4,096\text{ tokens/seq}$), total memory consumed by KV cache is $24 \times 4096 = 98,304\text{ tokens}$, corresponding to **93.3% of the 105,329 token budget** (`kv_cache_util = 0.93`).
   - Batch 24 is the **absolute physical capacity limit** of a single 24GB L4 GPU for full-length sequences.
2. **The Collapse at Batch 32 and Batch 48**:
   - At **Batch 32**: Memory demand is $32 \times 4096 = 131,072\text{ tokens}$ (**124.4% of capacity**).
   - At **Batch 48**: Memory demand is $48 \times 4096 = 196,608\text{ tokens}$ (**186.7% of capacity**).
3. **The Empirical Reversal in `bench_log.csv`**:
   - Instead of doubling to ~3200 tok/s, reported throughput **declines** from **1607.4 tok/s (Batch 24)** down to **1384.0 tok/s (Batch 32)** and **1298.5 tok/s (Batch 48)**.
   - Wall-clock execution time surges from **61.16s** (Batch 24) to **94.71s** (Batch 32) and **151.41s** (Batch 48).

### The "Honest Goodput" Calculation (Prefill Inflation Exposed):

The **one misread column** in `bench_log.csv` that led to the flawed projection was **`reported_tok_s`**, which bundled parallel prompt prefill tokens together with sequential token generation:

$$\text{Reported Throughput} (\text{reported\_tok\_s}) = \frac{\text{Total Tokens (Prefill + Generation)}}{\text{Wall Clock Seconds}} = \frac{24 \times (3584 + 512)}{61.16} = \frac{98,304}{61.16} = \mathbf{1607.40 \text{ tok/s}}$$

The actual **Generation Goodput** (newly generated tokens delivered to clients):
$$\text{Honest Goodput} = \frac{\text{Generated Tokens}}{\text{Wall Clock Seconds}} = \frac{24 \times 512}{61.16} = \frac{12,288}{61.16} = \mathbf{200.92 \text{ tok/s}}$$

**Prefill accounted for 87.5% of the total tokens processed.** Because prompt prefill is compute-bound matrix multiplication executed in massive parallel bursts, bundling prefill tokens into `reported_tok_s` artificially inflated throughput by **8.00x** ($1607.4 / 200.92$). The sustainable token generation rate of the server was only ~200 tok/s.

---

## 3. The Preemption Trigger: KV-Cache Saturation (>0.95 Utilization)

In PagedAttention / vLLM-style serving engines, memory is allocated in discrete block pages. When `kv_cache_util` approaches saturation ($\ge 0.95$):
1. **Free Block Exhaustion**: The memory manager runs out of free physical KV blocks to append new decode tokens for running requests.
2. **Forced Preemption**: To avoid Out-Of-Memory (OOM) crashes, the engine must abort/suspend active decode sequences (`preempted_seqs = 7` at Batch 32, `preempted_seqs = 23` at Batch 48) and evict their KV cache.
3. **Recompute Thrashing**: When preempted sequences are resumed, the engine must **re-run prefill from scratch** on their prompts. This generates huge compute thrashing, degrades inter-token latency (`itl_ms_p50` surges from 48ms to 101ms), and degrades end-to-end tail latency (`e2e_ms_p95` degrades from 15.5s to 105.4s).

| Batch Size | Prompt / Gen Len | KV Cache Util | Preempted Seqs | Reported Throughput | Honest Goodput | p95 Latency | Health Status |
|---|---|---|---|---|---|---|---|
| **24** | 3584 / 512 | **0.93** | **0** | 1607.4 tok/s | 200.92 tok/s | 69.2s | **Optimal Peak (Safe)** |
| **32** | 3584 / 512 | **0.97** | **7** | 1384.0 tok/s | 172.99 tok/s | 97.5s | **Preemption Thrashing** |
| **48** | 3584 / 512 | **0.97** | **23** | 1298.5 tok/s | 162.31 tok/s | 105.4s | **Severe Thrashing** |

---

## 4. The Golden Metric for Serving Infrastructure

To prevent deceptive capacity planning and SLA breaches, the Infrastructure and Serving teams must enforce two distinct, unbundled metrics:

### 1. Primary Decode Sizing Metric: **`effective_decode_goodput`**
$$\text{effective\_decode\_goodput} = \frac{\sum \text{Generated Output Tokens}}{\text{Active Decode Wall Time (s)}}$$
- **Purpose**: Tracks actual revenue-generating token generation independently of prompt prefill size.

### 2. Capacity & Schedulability Guardrail: **`kv_reservation_concurrency_headroom`**
$$\text{kv\_reservation\_concurrency\_headroom} = 1.0 - \frac{\sum_{i=1}^{B} \text{max\_sequence\_len}_i}{\text{Total KV Token Capacity}}$$
- **Enforcement Rule**: Admission control must reject or queue incoming requests whenever reserved concurrency exceeds **$0.85$** to provide a safety margin against preemption thrashing.
