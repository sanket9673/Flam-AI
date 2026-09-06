#!/usr/bin/env python3
"""
concept_semantic_density.py -- Forensic audit for semantic density and metric bias.

Proves that "Tokens per Word" (Metric A) is conceptually flawed and biased against
agglutinative and morphologically rich Indic languages (like Kannada), whereas
"Tokens per UTF-8 Byte" (Metric B) provides a fair, normalized evaluation.
"""

from pathlib import Path
import re
import tiktoken


def truth_word_counter(text: str) -> int:
    """Regex-based word counter matching non-whitespace sequences."""
    return len(re.findall(r"\S+", text))


def load_corpus_stats(file_path: Path, enc):
    """Compute tokens, regex words, characters, and UTF-8 bytes for a corpus file."""
    total_tokens = 0
    total_words = 0
    total_chars = 0
    total_bytes = 0
    line_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            line_count += 1
            tokens = enc.encode(line)
            total_tokens += len(tokens)
            total_words += truth_word_counter(line)
            total_chars += len(line)
            total_bytes += len(line.encode("utf-8"))

    metric_a = total_tokens / total_words if total_words else 0.0
    metric_b = total_tokens / total_bytes if total_bytes else 0.0

    return {
        "line_count": line_count,
        "total_tokens": total_tokens,
        "total_words": total_words,
        "total_chars": total_chars,
        "total_bytes": total_bytes,
        "metric_a_tok_per_word": metric_a,
        "metric_b_tok_per_byte": metric_b,
    }


def main():
    repo_root = Path(__file__).resolve().parents[2]
    flores_dir = repo_root / "data" / "corpus_flores"
    eng_path = flores_dir / "eng.txt"
    kan_path = flores_dir / "kan.txt"

    enc = tiktoken.get_encoding("gpt2")

    stats_eng = load_corpus_stats(eng_path, enc)
    stats_kan = load_corpus_stats(kan_path, enc)

    ratio_metric_a = (
        stats_kan["metric_a_tok_per_word"] / stats_eng["metric_a_tok_per_word"]
    )
    ratio_metric_b = (
        stats_kan["metric_b_tok_per_byte"] / stats_eng["metric_b_tok_per_byte"]
    )

    byte_ratio_str = f"{stats_kan['total_bytes'] / stats_eng['total_bytes']:.2f}x"
    word_ratio_str = f"{stats_kan['total_words'] / stats_eng['total_words']:.2f}x"
    token_ratio_str = f"{stats_kan['total_tokens'] / stats_eng['total_tokens']:.2f}x"
    metric_a_ratio_str = f"{ratio_metric_a:.2f}x"
    metric_b_ratio_str = f"{ratio_metric_b:.2f}x"

    eng_metric_a_str = f"{stats_eng['metric_a_tok_per_word']:.2f}"
    kan_metric_a_str = f"{stats_kan['metric_a_tok_per_word']:.2f}"
    eng_metric_b_str = f"{stats_eng['metric_b_tok_per_byte']:.4f}"
    kan_metric_b_str = f"{stats_kan['metric_b_tok_per_byte']:.4f}"

    print("=== Experiment 2: The Semantic Density Flaw ===")
    print("Comparing English (eng) vs Kannada (kan) on parallel FLORES-200 devtest\n")

    print(
        f"{'Metric':<36}{'English (EN)':<16}{'Kannada (KN)':<16}{'KN / EN Ratio':<15}"
    )
    print("-" * 83)
    print(
        f"{'Total Lines':<36}{str(stats_eng['line_count']):<16}{str(stats_kan['line_count']):<16}{'1.00x':<15}"
    )
    print(
        f"{'Total UTF-8 Bytes':<36}{str(stats_eng['total_bytes']):<16}{str(stats_kan['total_bytes']):<16}{byte_ratio_str:<15}"
    )
    print(
        f"{'Total Words (Regex \\S+)':<36}{str(stats_eng['total_words']):<16}{str(stats_kan['total_words']):<16}{word_ratio_str:<15}"
    )
    print(
        f"{'Total GPT-2 Tokens':<36}{str(stats_eng['total_tokens']):<16}{str(stats_kan['total_tokens']):<16}{token_ratio_str:<15}"
    )
    print("-" * 83)
    print(
        f"{'Metric A: Tokens / Word (Intern)':<36}{eng_metric_a_str:<16}{kan_metric_a_str:<16}{metric_a_ratio_str:<15}"
    )
    print(
        f"{'Metric B: Tokens / UTF-8 Byte':<36}{eng_metric_b_str:<16}{kan_metric_b_str:<16}{metric_b_ratio_str:<15}"
    )
    print("-" * 83)
    print()
    print("--- Analysis & Key Takeaway ---")
    print(
        f"1. Metric A (Tokens / Word): Kannada appears {ratio_metric_a:.2f}x 'worse' than English."
    )
    print(
        f"   Why? Kannada is an agglutinative language where single compound words pack multiple morphemes/concepts"
    )
    print(
        f"   (yielding only {stats_kan['total_words']} words vs {stats_eng['total_words']} in English for the exact same parallel sentences)."
    )
    print(
        f"2. Metric B (Tokens / Byte): Kannada is only {ratio_metric_b:.2f}x that of English."
    )
    print(
        f"   Normalizing by UTF-8 bytes accounts for information payload rather than whitespace delimiters."
    )


if __name__ == "__main__":
    main()
