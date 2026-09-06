# AI Transparency & Forensic Audit Log (Humble Audit)

This repository documents the comprehensive forensic audit and re-evaluation of LLM tokenizer fertility, serving capacity, and multilingual strategy. AI tooling (Antigravity IDE / Gemini) was utilized throughout the project under strict pair-programming and verification standards.

---

## 1. Principles of AI Interaction
- **The Evidence Rule**: Every single metric, efficiency ratio, and capacity limit in this repository is computed directly in executable Python code and verified via automated execution (`scripts/verify_all.py`).
- **Zero Hallucinated Numbers**: No numbers from chat suggestions or external decks were accepted without code-backed verification against raw dataset files or hardware specifications.
- **Human Authority**: All architectural recommendations, strategy decisions, and forensic conclusions are human-verified and owned by the engineering team.

---

## 2. The Humble Audit: Force Multipliers vs. Fact-Checked Interventions

### A. Where AI was a "Force Multiplier" (Efficiency & Velocity)
1. **Corpus Ingestion Pipeline**: Rapidly generated extraction boilerplate in `scripts/download_flores.py` to pull and align 1,012 parallel sentences from the HuggingFace `facebook/flores` dataset across four languages (`eng_Latn`, `hin_Deva`, `kan_Knda`, `tam_Taml`).
2. **Matrix Formatting & Documentation**: Automated the generation and markdown alignment of comparative evaluation tables across all three research memos (`partA/results_matrix.md`, `partA/recommendation.md`, `partB/answers_B.md`, `partC/memo.md`).
3. **Reviewer Capacity Modeling**: Scaffolded `partC/reviewer_simulator.py` to evaluate varying human-reviewer allocations and statistical power boundaries under tight time constraints.

### B. Where AI was "Fact-Checked" & Corrected by the Auditor
1. **Tokens per Character vs. Tokens per Byte**:
   - *AI Suggestion*: Early AI drafts suggested using "Tokens per Character" as a fix for the intern's whitespace counter bug.
   - *Auditor Correction*: The auditor rejected this metric. In Brahmic scripts, Unicode characters (code points) vary widely depending on normalization form (NFC vs NFD) and do not represent the physical wire payload or tokenization economics. The auditor mandated **Tokens per UTF-8 Byte** (economic ground truth) and **Tokens per Grapheme Cluster (`\X`)** (visual glyph truth).
2. **Linear Throughput Scaling Hallucination**:
   - *AI Suggestion*: In initial capacity brainstorming, the model suggested throughput could scale with batch size to 3,200+ tok/s.
   - *Auditor Correction*: The auditor verified the physical KV-cache memory budget on 24GB L4 GPUs ($112.00\text{ KiB/token} \rightarrow 12.08\text{ GB budget} \rightarrow 105,329\text{ tokens}$), proving that Batch 24 hits 93.3% utilization and Batch 32/48 causes preemption collapse.
3. **Uniform vs. Anchor Human Review Allocation**:
   - *AI Suggestion*: AI initially proposed splitting 1,200 human review rows evenly across all 6 languages ($N=200$ each).
   - *Auditor Correction*: The auditor pointed out that $N=200$ is statistically underpowered, pivoting to the **Anchor Strategy** ($N=600$ each for Hindi and Kannada) with LLM-as-a-judge for the remaining 4 transfer languages.

---

## 3. Log of AI-Assisted Tasks by Feature

| Milestone | Task Description | Human-AI Interaction & Verification Mode |
|---|---|---|
| **Feature 0** | Baseline Capture & Environment Setup | Automated execution of original `fertility.py` on baseline sample corpora. |
| **Feature 1** | FLORES-200 Corpus Pipeline | Script extraction of 1,012 parallel sentence pairs across 4 languages. |
| **Feature 2** | Forensic Audit Tooling (Whitespace, Density, Casing) | Built `bug_whitespace.py`, `concept_semantic_density.py`, `red_herring_casing.py`. |
| **Feature 3** | Source of Truth Benchmark & Recommendation Memo | Implemented `partA/fertility_fixed.py`, `partA/results_matrix.md`, and executive memo `partA/recommendation.md`. |
| **Feature 4** | Capacity Reconciliation & KV-Cache Math | Built `partB/capacity_math.py` and authored `partB/answers_B.md` proving the prefill inflation illusion. |
| **Feature 5** | Strategic Synthesis & Reviewer Simulator | Built `partC/reviewer_simulator.py` and authored `partC/memo.md` establishing the Day-3 Kill Criterion. |
| **Feature 6** | Hardening & Verification Suite | Built `scripts/verify_all.py`, verified zero hardcoded paths, updated defense prep. |
