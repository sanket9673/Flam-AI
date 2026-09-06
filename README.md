# Multilingual LLM Tokenizer Economics & Capacity Audit

An engineering-grade forensic audit and reproducible benchmark suite evaluating multilingual tokenizer efficiency, GPU serving constraints, and strategic distillation architectures for Indic languages (Hindi, Kannada, Tamil, Telugu, Bengali, Marathi).

---

## Quick Start: Reproduce Evidence

To run the complete verification suite and reproduce all findings from first-principles code:

```bash
pip install -r requirements.txt
python3 scripts/verify_all.py
```

---

## Executive Summary of Findings

1. **The "6x Hindi Penalty" Myth Debunked (Part A)**:
   - The intern's claim that Hindi is 5.89x worse to serve than English was a statistical artifact of `line.split(" ")` whitespace bugs and "Tokens per Word" cross-lingual bias on agglutinative morphology.
   - When measured against **Tokens per UTF-8 Byte** on modern tokenizers (**Meta-Llama-3-8B**), Hindi achieves **0.99x parity with English**.

2. **Serving Capacity & KV-Cache Sizing (Part B)**:
   - For the **FLM-4B** model on an **NVIDIA L4 (24GB VRAM)** GPU, KV-cache memory is exactly **112.00 KiB per token** ($114,688\text{ bytes}$), providing a usable budget of **12.08 GB (105,329 tokens)**.
   - The maximum full-length (4096-token) concurrency limit is **25 concurrent streams**.
   - The intern's claim of 3,200 tok/s at Batch 48 was a hallucination caused by bundling compute-bound prompt prefill tokens (87.5% of the total) into decode throughput. Pushing beyond Batch 24 causes severe **KV-cache saturation (>0.95 util) and preemption thrashing (7 and 23 preemptions)**.

3. **Strategic Synthesis & Reviewer Modeling (Part C)**:
   - Under a realistic human evaluation constraint of 10 hours/week over 3 weeks (90s/sample), our total validation capacity is strictly capped at **1,200 total samples**.
   - **Recommended Architecture**: **Path (A) — Synthetic Distillation (SFT)** using a Llama-3 70B Teacher.
   - **Evaluation Strategy**: 100% human validation focused on **Anchor Languages** (Hindi $N=600$, Kannada $N=600$), with Transfer languages (Tamil, Telugu, Bengali, Marathi) governed by **LLM-as-a-Judge** calibrated by the empirical Human-LLM Trust Discount Factor ($\alpha$).

---

## Repository Structure

```text
├── data/
│   └── corpus_flores/              # 1,012 sentence-aligned parallel lines (eng, hin, kan, tam)
├── partA/
│   ├── fertility_fixed.py          # Corrected multilingual tokenizer benchmark (GPT-2 vs Llama-3)
│   ├── results_matrix.md           # Source of Truth benchmark results matrix
│   └── recommendation.md           # Executive recommendation memo (A4)
├── partB/
│   ├── capacity_math.py            # First-principles KV-cache arithmetic & log audit
│   └── answers_B.md                # Forensic failure audit report & schedulability metrics
├── partC/
│   ├── reviewer_simulator.py       # Reviewer bandwidth & statistical confidence simulator
│   └── memo.md                     # Strategic decision memo & Day-3 Kill Criterion
├── scripts/
│   ├── audit_tooling/
│   │   ├── bug_whitespace.py       # Experiment 1: The Word-Count Bug
│   │   ├── concept_semantic_density.py # Experiment 2: Semantic Density Flaw
│   │   └── red_herring_casing.py   # Experiment 3: Casing in Indic Scripts
│   ├── download_flores.py          # FLORES-200 parallel extraction pipeline
│   ├── capture_baseline.py         # Baseline capture automation
│   └── verify_all.py               # Top-level compliance & verification suite
├── starter_kit/                    # Read-only reference of intern's baseline code & logs
│   ├── fertility.py                # Original v0 script (untouched)
│   ├── REPORT_v0.md                # Intern's original flawed report
│   ├── bench/bench_log.csv         # Raw serving benchmark logs
│   └── corpus_sample/              # Original sample files
├── NOTEBOOK.md                     # Chronological research notebook & Defense Prep
├── AI_USAGE.md                     # AI transparency log & Humble Audit
└── requirements.txt                # Python dependencies
```
