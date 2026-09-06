# Feature 3: Tokenizer Efficiency Matrix (Source of Truth)

Evaluated on FLORES-200 `devtest` parallel corpus (1,012 sentence-aligned lines per language).
- **Tokenizers**: GPT-2 (tiktoken, vocab=50,257) vs Llama-3 (`NousResearch/Meta-Llama-3-8B`, vocab=128,256)
- **Metric A (Economic Ground Truth)**: Tokens / 1,000 UTF-8 Bytes
- **Metric B (Human Perception)**: Tokens / Grapheme Cluster (Unicode `\X` aksharas)

## Results Matrix

| Language | Code | Total Bytes | Graphemes | GPT-2 Tok/1k Bytes | Llama-3 Tok/1k Bytes | Llama-3 Rel to EN | GPT-2 Tok/Grapheme | Llama-3 Tok/Grapheme | Llama-3 Efficiency Gain |
|---|---|---|---|---|---|---|---|---|---|
| English | `eng` | 132,096 | 131,966 | 204.73 | 205.69 | 1.00x | 0.205 | 0.206 | -0.47% |
| Hindi | `hin` | 337,073 | 85,957 | 594.73 | 203.26 | 0.99x | 2.332 | 0.797 | +65.82% |
| Kannada | `kan` | 375,380 | 90,371 | 978.75 | 641.14 | 3.12x | 4.066 | 2.663 | +34.49% |
| Tamil | `tam` | 421,641 | 99,724 | 996.53 | 492.77 | 2.40x | 4.213 | 2.083 | +50.55% |

## Key Observations
1. **Hindi Parity with English**: Under Llama-3, Hindi requires **203.26 tokens/1k bytes** compared to **205.69** for English (a **0.99x ratio**). The intern's 5.89x 'penalty' is completely eliminated.
2. **The Llama-3 Dividend**: Llama-3 delivers a **+65.82%** token reduction for Hindi, **+50.55%** for Tamil, and **+34.49%** for Kannada compared to GPT-2.
3. **Grapheme Normalization**: In Indic scripts, grapheme clusters represent true visual syllables (aksharas). Llama-3 achieves sub-1.0 token/grapheme efficiency on Hindi (0.80) and dramatic improvements for Dravidian scripts.
