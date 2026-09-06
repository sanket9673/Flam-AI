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

