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
