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

