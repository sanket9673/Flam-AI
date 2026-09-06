# Research Notebook

## [Baseline] - Documentation of Intern's v0 Results
- **Hypothesis**: The intern's script `fertility.py` provides an accurate measurement of tokenizer performance as claimed in `REPORT_v0.md`.
- **Experiment**: Execute the original script using the provided sample corpora and the GPT-2 tokenizer.
- **Result**:
```text
tokenizer: gpt2
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.27       0.226
hin                       7.45       1.579

hin is 5.89x the fertility of eng (worse tokenization)
```

## [Feature 1] - Corpus Construction
- **Source**: FLORES-200 (`devtest` split).
- **Domain**: Wikipedia / Professional Translation (Formal).
- **Extraction Pipeline**: [`scripts/download_flores.py`](file:///Users/sanketkisanchavhan/Documents/Projects/starter_kit/scripts/download_flores.py) extracts parallel sentence-aligned files for English (`eng_Latn`), Hindi (`hin_Deva`), Kannada (`kan_Knda`), and Tamil (`tam_Taml`).
- **Integrity**: Exact 1:1 sentence alignment preserved across all files (verified 1,012 lines each).

### Corpus Statistics Table

| Language | Language Code | File Path | Line Count | Total Character Count |
|---|---|---|---|---|
| English | `eng_Latn` | [`data/corpus_flores/eng.txt`](file:///Users/sanketkisanchavhan/Documents/Projects/starter_kit/data/corpus_flores/eng.txt) | 1,012 | 132,978 |
| Hindi | `hin_Deva` | [`data/corpus_flores/hin.txt`](file:///Users/sanketkisanchavhan/Documents/Projects/starter_kit/data/corpus_flores/hin.txt) | 1,012 | 132,070 |
| Kannada | `kan_Knda` | [`data/corpus_flores/kan.txt`](file:///Users/sanketkisanchavhan/Documents/Projects/starter_kit/data/corpus_flores/kan.txt) | 1,012 | 139,052 |
| Tamil | `tam_Taml` | [`data/corpus_flores/tam.txt`](file:///Users/sanketkisanchavhan/Documents/Projects/starter_kit/data/corpus_flores/tam.txt) | 1,012 | 155,145 |

### Caveats & Limitations
This corpus consists of formal, professionally translated Wikipedia content. It may not accurately reflect tokenizer performance on 'casual' chat, code, or social media slang (to be addressed in future audits).

## [Feature 2] - The Audit Report

### Experiment 1: The Word-Count Bug

- **The Claim**: The word count calculated in `fertility.py` is inaccurate due to naive whitespace handling via `line.split(" ")`, which counts consecutive spaces and untrimmed whitespace as phantom empty words.
- **The Evidence**: 
```bash
python3 scripts/audit_tooling/bug_whitespace.py
```
- **The Result**:
```text
=== Experiment 1: The Word-Count Bug ===
Target File: /Users/sanketkisanchavhan/Documents/Projects/Flam AI/starter_kit/corpus_sample/eng_sample.txt

Line #  Truth Words   Intern Words  Status
--------------------------------------------------
1       8             8             MATCH
2       7             7             MATCH
3       12            12            MATCH
4       7             7             MATCH
5       6             6             MATCH
6       8             8             MATCH
7       7             8             MISMATCH [BUG]
8       6             6             MATCH
9       6             6             MATCH
10      11            11            MATCH
--------------------------------------------------

--- Detailed Highlight of Offending Line ---
Target Line: 'Please keep the books  in the cupboard.'
Truth Counter (regex r'\S+'): 7 words
Intern Counter (line.split(' ')): 8 words
Intern Split Tokens: ['Please', 'keep', 'the', 'books', '', 'in', 'the', 'cupboard.']
Artifact: Naive splitting produces empty string token `''` due to double space.

--- Summary Statistics ---
Total Truth Word Count:   78
Total Intern Word Count:  79
Total Word Count Difference: +1 words
Percentage Error:         +1.28%
```
- **The Verdict**: **Bug** (Implementation error resulting in inflated denominator and deflated fertility metrics on text with uneven whitespace).

---

### Experiment 2: The Semantic Density Flaw

- **The Claim**: "Tokens per Word" is a conceptually flawed and fundamentally biased metric for evaluating Indic languages because agglutinative and morphologically rich languages (such as Kannada) pack multiple morphemes into single compound words, making them appear artificially inefficient compared to analytical languages like English.
- **The Evidence**: 
```bash
python3 scripts/audit_tooling/concept_semantic_density.py
```
- **The Result**:
```text
=== Experiment 2: The Semantic Density Flaw ===
Comparing English (eng) vs Kannada (kan) on parallel FLORES-200 devtest

Metric                              English (EN)    Kannada (KN)    KN / EN Ratio  
-----------------------------------------------------------------------------------
Total Lines                         1012            1012            1.00x          
Total UTF-8 Bytes                   132096          375380          2.84x          
Total Words (Regex \S+)             21901           16100           0.74x          
Total GPT-2 Tokens                  27044           367405          13.59x         
-----------------------------------------------------------------------------------
Metric A: Tokens / Word (Intern)    1.23            22.82           18.48x         
Metric B: Tokens / UTF-8 Byte       0.2047          0.9788          4.78x          
-----------------------------------------------------------------------------------

--- Analysis & Key Takeaway ---
1. Metric A (Tokens / Word): Kannada appears 18.48x 'worse' than English.
   Why? Kannada is an agglutinative language where single compound words pack multiple morphemes/concepts
   (yielding only 16100 words vs 21901 in English for the exact same parallel sentences).
2. Metric B (Tokens / Byte): Kannada is only 4.78x that of English.
   Normalizing by UTF-8 bytes accounts for information payload rather than whitespace delimiters.
```
- **The Verdict**: **Conceptual Flaw** (The intern's Metric A introduces linguistic bias; Metric B [Tokens per Byte] provides a standardized, information-theoretic comparison).

---

### Experiment 3: The Red Herring

- **The Claim**: Applying `.lower()` to Indic script corpora introduces tokenization distortion or noise during tokenizer benchmarking.
- **The Evidence**: 
```bash
python3 scripts/audit_tooling/red_herring_casing.py
```
- **The Result**:
```text
=== Experiment 3: The Red Herring (Casing in Indic Scripts) ===
Target File: /Users/sanketkisanchavhan/Documents/Projects/Flam AI/data/corpus_flores/hin.txt
Tokenizer:   gpt2

--- Corpus-Wide Line Matching Results ---
Total Matches:          974
Total Lines:            1012
Overall Match Rate:     96.25%

--- Script-Level (Devanagari) Isolation ---
Pure Indic Lines:       967 / 967 (100.00% match)
Lines with Latin chars: 38 / 1012
Devanagari Characters with Case Distinction: 0 / 69 (0.00%)

--- Forensic Audit Verdict ---
Verdict: Harmless / Red Herring.
Indic scripts (Devanagari, Kannada, Tamil) are unicameral and have NO upper/lowercase distinction.
Applying `.lower()` has 0 effect on Indic characters and is therefore completely harmless.
The 38 mismatched lines in FLORES-200 are 100% caused by embedded English/Latin acronyms
such as 'PALM', 'ZMapp', and 'USOC', not by any property of the Indic tokenizer.
```
- **The Verdict**: **Harmless** (Red herring; Indic scripts are unicameral so `.lower()` is a no-op for Indic characters and does not alter token sequence outputs for native script).

## [Feature 3] - The Redemption (Corrected Analysis)

### The "Aha!" Moment: Linguistic Density vs. Tokenization Inefficiency

The core insight that debunks the intern's "6x Indic penalty" is the distinction between **Linguistic Density** and **Tokenization Inefficiency**:
1. **Linguistic Density**: Dravidian and Indo-Aryan languages (such as Kannada and Tamil) are morphologically rich and highly agglutinative. A single word often encapsulates what requires a multi-word prepositional phrase in English (e.g., compound nominals, postpositions, tense, and aspect markers). Across the exact same 1,012 parallel FLORES-200 sentences, Kannada expresses the full semantic meaning in only **16,100 words** compared to English's **21,901 words** (0.74x).
2. **The Metric Error**: Dividing tokens by word count artificially penalizes languages with higher information density per word. The intern mistook morphological compactness for poor tokenization.
3. **The Stable Denominators**: Evaluating efficiency using **Tokens per UTF-8 Byte** (economic ground truth) and **Tokens per Grapheme Cluster** (`\X` user-perceived visual syllables/aksharas) removes cross-lingual delimiter bias.

---

### Final Comparison Matrix (Source of Truth)

**Evaluation Corpus**: FLORES-200 `devtest` (1,012 parallel sentence-aligned lines per language).  
**Tokenizers**: GPT-2 (vocab=50,257) vs. Meta-Llama-3-8B (vocab=128,256).

| Language | Code | Total Bytes | Graphemes | GPT-2 Tok/1k Bytes | Llama-3 Tok/1k Bytes | Llama-3 Rel to EN | GPT-2 Tok/Grapheme | Llama-3 Tok/Grapheme | Llama-3 Efficiency Gain |
|---|---|---|---|---|---|---|---|---|---|
| **English** | `eng` | 132,096 | 131,966 | 204.73 | 205.69 | 1.00x | 0.205 | 0.206 | -0.47% |
| **Hindi** | `hin` | 337,073 | 85,957 | 594.73 | 203.26 | **0.99x** | 2.332 | 0.797 | **+65.82%** |
| **Kannada** | `kan` | 375,380 | 90,371 | 978.75 | 641.14 | **3.12x** | 4.066 | 2.663 | **+34.49%** |
| **Tamil** | `tam` | 421,641 | 99,724 | 996.53 | 492.77 | **2.40x** | 4.213 | 2.083 | **+50.55%** |

---

### Executive Insights
- **Full Parity for Hindi**: In Llama-3, Hindi requires **203.26 tokens per 1k bytes** vs **205.69** for English (0.99x ratio). Per byte of information, Hindi is as cost-effective to serve as English.
- **The Llama-3 Dividend**: The expanded 128k vocabulary provides massive token savings across all Indic scripts: **+65.8% for Hindi**, **+50.6% for Tamil**, and **+34.5% for Kannada**.
- **Infra Standard**: The production monitoring metric for LLM token economy is officially standardized to **Tokens / UTF-8 Byte**.

## [Feature 4] - Capacity Audit

### The "Aha!" Moment: Prefill-Heavy Throughput vs. Sustainable Generation Goodput

The intern made two fatal capacity planning errors in `REPORT_v0.md`:
1. **The Prefill Inflation Illusion**: At Batch 24 (Prompt 3584, Gen 512), the intern reported **1,607.4 tok/s**. However, prompt prefill constituted **87.5% of all tokens** ($24 \times 3584 = 86,016\text{ tokens}$). Because prefill is compute-bound and processed in parallel matrix multiplications, bundling prefill tokens inflated the top-line number by **8.00x**. The honest generation goodput delivered to clients was only **200.92 tok/s**.
2. **The Linear Scaling Hallucination**: The intern assumed throughput would scale linearly with batch size to ~3,200 tok/s at Batch 48. In reality, a single NVIDIA L4 (24GB VRAM) hits hard memory saturation at **Batch 24 (93.3% KV utilization)**. Pushing to Batch 32 and Batch 48 caused **KV-cache exhaustion and preemption thrashing (7 and 23 preemptions)**, causing throughput to collapse rather than scale.

---

### First-Principles KV-Cache Arithmetic (FLM-4B on NVIDIA L4)

- **Model Specifications**: 4.2B parameters (dense), 28 layers, 8 KV heads (GQA), head dimension 128, fp16 precision.
- **KV Cache Memory per Token**:
  $$\text{KV Bytes / Token} = 2 \times 28 \times 8 \times 128 \times 2 = \mathbf{114,688 \text{ bytes}} = \mathbf{112.00 \text{ KiB / token}}$$
- **VRAM Budget Breakdown (NVIDIA L4 24GB)**:
  - Total Usable VRAM (`gpu_memory_utilization = 0.92`): **22.08 GB**
  - Model Weights ($4.2\text{B} \times 2\text{ bytes}$): **8.40 GB**
  - Non-KV Runtime Overhead: **1.60 GB**
  - **Available KV-Cache Budget**: $22.08 - 8.40 - 1.60 = \mathbf{12.08 \text{ GB}}$ ($12,080,000,000\text{ bytes}$)
  - **Total Token Capacity**: $12,080,000,000 / 114,688 = \mathbf{105,329 \text{ tokens}}$
  - **Max Concurrent 4096-token Sequences**: $105,329 / 4096 = \mathbf{25.71 \rightarrow 25 \text{ full streams}}$

---

### Benchmark Audit: Prompt 3584 Sweep (Preemption & Saturation)

| Batch Size | Prompt Len | Gen Len | Wall Time (s) | Reported Throughput | Honest Goodput | Preempted Seqs | KV Cache Util | Engine State |
|---|---|---|---|---|---|---|---|---|
| **4** | 3584 | 512 | 28.98s | 565.4 tok/s | 70.67 tok/s | 0 | 0.16 | Healthy |
| **8** | 3584 | 512 | 36.30s | 902.6 tok/s | 112.84 tok/s | 0 | 0.31 | Healthy |
| **16** | 3584 | 512 | 49.97s | 1311.4 tok/s | 163.94 tok/s | 0 | 0.62 | Healthy |
| **24** | 3584 | 512 | 61.16s | **1607.4 tok/s** | **200.92 tok/s** | **0** | **0.93** | **Peak Capacity Ceiling** |
| **32** | 3584 | 512 | 94.71s | 1384.0 tok/s | 172.99 tok/s | 7 | 0.97 | Preemption Thrashing |
| **48** | 3584 | 512 | 151.41s | 1298.5 tok/s | 162.31 tok/s | 23 | 0.97 | Severe Thrashing |

---

### Sizing Guidelines & Golden Schedulability Metric
1. **Decode Goodput Metric**: $\text{effective\_decode\_goodput} = \frac{\sum \text{Generated Tokens}}{\text{Decode Wall Time}}$
2. **Admission Control Limit**: Cap concurrent reserved tokens at **$\le 85\%$ of KV-cache budget** (max $\approx 21$ concurrent full 4096-length requests per L4 GPU).

