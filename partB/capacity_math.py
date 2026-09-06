#!/usr/bin/env python3
"""
partB/capacity_math.py -- Forensic Capacity & KV-Cache Audit for FLM-4B on NVIDIA L4 (24GB).

Performs first-principles arithmetic on GPU memory constraints, KV-cache budgets,
and audits the bench_log.csv to expose the linear scaling fallacy, preemption triggers,
and the prefill-inflated throughput illusion vs honest decode goodput.
"""

from pathlib import Path
import pandas as pd


def compute_first_principles_capacity():
    # Model Constants (FLM-4B)
    params = 4.2e9  # 4.2 Billion dense parameters
    layers = 28
    d_model = 3072
    query_heads = 24
    kv_heads = 8  # Grouped Query Attention (GQA)
    head_dim = 128
    bytes_per_elem = 2  # fp16
    max_seq_len = 4096

    # Hardware & Runtime Constants (NVIDIA L4 24GB)
    total_vram_gb = 24.0
    gpu_mem_util = 0.92
    usable_vram_gb = total_vram_gb * gpu_mem_util  # 22.08 GB
    runtime_overhead_gb = 1.6  # activations, CUDA graphs, workspace

    # 1. KV-Cache Bytes per Token: 2 * layers * num_kv_heads * head_dim * bytes_per_element
    # Factor of 2 accounts for Key and Value matrices
    kv_bytes_per_token = 2 * layers * kv_heads * head_dim * bytes_per_elem
    kv_kb_per_token = kv_bytes_per_token / 1024  # KiB
    kv_mb_per_token = kv_bytes_per_token / (1024**2)

    # 2. Model Weight Memory: 4.2B params * 2 bytes
    model_weight_bytes = params * bytes_per_elem
    model_weight_gb = model_weight_bytes / (1e9)  # 8.40 GB in decimal

    # 3. KV-Cache Budget: (Total VRAM * 0.92) - Model Weights - Overhead
    usable_vram_bytes = usable_vram_gb * 1e9
    overhead_bytes = runtime_overhead_gb * 1e9
    kv_budget_bytes = usable_vram_bytes - model_weight_bytes - overhead_bytes
    kv_budget_gb = kv_budget_bytes / 1e9  # 12.08 GB

    # 4. Max Concurrency & Capacity
    total_kv_tokens = int(kv_budget_bytes // kv_bytes_per_token)
    max_concurrency_4096 = total_kv_tokens / max_seq_len

    return {
        "params": params,
        "layers": layers,
        "d_model": d_model,
        "query_heads": query_heads,
        "kv_heads": kv_heads,
        "head_dim": head_dim,
        "bytes_per_elem": bytes_per_elem,
        "max_seq_len": max_seq_len,
        "total_vram_gb": total_vram_gb,
        "usable_vram_gb": usable_vram_gb,
        "runtime_overhead_gb": runtime_overhead_gb,
        "model_weight_gb": model_weight_gb,
        "kv_budget_gb": kv_budget_gb,
        "kv_bytes_per_token": kv_bytes_per_token,
        "kv_kb_per_token": kv_kb_per_token,
        "total_kv_tokens": total_kv_tokens,
        "max_concurrency_4096": max_concurrency_4096,
    }


def audit_bench_logs(csv_path: Path):
    df = pd.read_csv(csv_path)

    # Calculate Honest Goodput (Generation Decode Throughput): (batch_size * gen_len) / wall_clock_s
    df["total_tokens"] = df["batch_size"] * (
        df["prompt_len"] + df["gen_len"]
    )
    df["generated_tokens"] = df["batch_size"] * df["gen_len"]
    df["honest_goodput_tok_s"] = df["generated_tokens"] / df["wall_clock_s"]
    df["calc_reported_tok_s"] = df["total_tokens"] / df["wall_clock_s"]
    df["prefill_pct"] = (
        df["prompt_len"] / (df["prompt_len"] + df["gen_len"])
    ) * 100

    return df


def main():
    repo_root = Path(__file__).resolve().parents[1]
    csv_path = repo_root / "starter_kit" / "bench" / "bench_log.csv"

    cap = compute_first_principles_capacity()
    df = audit_bench_logs(csv_path)

    print("=" * 80)
    print("FEATURE 4: CAPACITY & KV-CACHE FORENSIC AUDIT (FLM-4B on NVIDIA L4)")
    print("=" * 80)
    print()
    print("--- 1. FIRST-PRINCIPLES KV-CACHE ARITHMETIC ---")
    print(f"Model Architecture:          FLM-4B ({cap['params']/1e9:.1f}B dense params, {cap['layers']} layers, {cap['kv_heads']} KV heads GQA, dim {cap['head_dim']})")
    print(f"KV-Cache Bytes per Token:    {cap['kv_bytes_per_token']:,} bytes ({cap['kv_kb_per_token']:.2f} KiB / token)")
    print(f"Peak VRAM:                   {cap['total_vram_gb']:.2f} GB")
    print(f"Usable VRAM (0.92 limit):    {cap['usable_vram_gb']:.2f} GB")
    print(f"Model Weights (fp16):        {cap['model_weight_gb']:.2f} GB")
    print(f"Non-KV Runtime Overhead:     {cap['runtime_overhead_gb']:.2f} GB")
    print(f"KV-Cache Budget:             {cap['kv_budget_gb']:.2f} GB ({cap['kv_budget_gb']*1e9:,.0f} bytes)")
    print(f"Total KV Token Capacity:     {cap['total_kv_tokens']:,} tokens")
    print(f"Max 4096-seq Concurrency:    {cap['max_concurrency_4096']:.2f} streams (Hard ceiling: 25 full concurrent sequences)")
    print()

    print("--- 2. BENCHMARK LOG AUDIT: PROMPT 3584 SWEEP (THE SCALING FALLACY) ---")
    prompt_3584_df = df[df["prompt_len"] == 3584].copy()
    
    cols_to_show = [
        "batch_size", "prompt_len", "gen_len", "wall_clock_s",
        "reported_tok_s", "honest_goodput_tok_s", "preempted_seqs", "kv_cache_util"
    ]
    print(f"{'Batch':<8}{'Wall(s)':<10}{'Reported tok/s':<18}{'Honest Goodput':<18}{'Preempted':<12}{'KV Util':<10}{'Status'}")
    print("-" * 88)
    for _, row in prompt_3584_df.iterrows():
        b = int(row["batch_size"])
        wall = f"{row['wall_clock_s']:.2f}"
        rep = f"{row['reported_tok_s']:.1f}"
        good = f"{row['honest_goodput_tok_s']:.2f} tok/s"
        pre = int(row["preempted_seqs"])
        util = f"{row['kv_cache_util']:.2f}"
        status = "HEALTHY" if pre == 0 else f"THRASHING ({pre} preemptions)"
        print(f"{b:<8}{wall:<10}{rep:<18}{good:<18}{pre:<12}{util:<10}{status}")
    print("-" * 88)
    print()

    print("--- 3. DETAILED AUDIT: BATCH 24 (PROMPT 3584 / GEN 512) ---")
    row_24 = df[(df["batch_size"] == 24) & (df["prompt_len"] == 3584)].iloc[0]
    total_tokens_24 = 24 * (3584 + 512)
    gen_tokens_24 = 24 * 512
    print(f"Batch Size:                  24")
    print(f"Prompt Length:               3,584 tokens")
    print(f"Generation Length:           512 tokens")
    print(f"Total Sequence Length:       4,096 tokens")
    print(f"Total Tokens Processed:      {total_tokens_24:,} tokens (Prefill: {24*3584:,} [87.5%], Decode: {gen_tokens_24:,} [12.5%])")
    print(f"Wall Clock Time:             {row_24['wall_clock_s']:.2f} seconds")
    print(f"Intern Reported Throughput:  {row_24['reported_tok_s']:.2f} tok/s  (Computed as Total Tokens / Wall Clock: {total_tokens_24}/{row_24['wall_clock_s']:.2f})")
    print(f"Honest Generation Goodput:   {row_24['honest_goodput_tok_s']:.2f} tok/s  (Computed as Generated Tokens / Wall Clock: {gen_tokens_24}/{row_24['wall_clock_s']:.2f})")
    print(f"Inflation Factor:            {row_24['reported_tok_s'] / row_24['honest_goodput_tok_s']:.2f}x (8.00x overestimation due to prefill bundling)")
    print()

    print("--- 4. FULL BENCHMARK SUMMARY TABLE ---")
    print(df[["batch_size", "prompt_len", "gen_len", "reported_tok_s", "honest_goodput_tok_s", "preempted_seqs", "kv_cache_util"]].to_string(index=False))


if __name__ == "__main__":
    main()
