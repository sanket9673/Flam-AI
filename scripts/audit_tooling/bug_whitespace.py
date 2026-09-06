#!/usr/bin/env python3
"""
bug_whitespace.py -- Forensic audit for whitespace handling in word counting.

Demonstrates how `line.split(" ")` causes erroneous word counts when consecutive
spaces or untrimmed whitespaces are present, compared to regex non-whitespace tokenization.
"""

from pathlib import Path
import re


def truth_counter(text: str) -> int:
    """Truth Counter: matches non-whitespace character clusters."""
    return len(re.findall(r"\S+", text))


def intern_counter(text: str) -> int:
    """Intern Counter: naive split on single whitespace character."""
    return len(text.split(" "))


def main():
    repo_root = Path(__file__).resolve().parents[2]
    sample_path = repo_root / "starter_kit" / "corpus_sample" / "eng_sample.txt"

    print(f"=== Experiment 1: The Word-Count Bug ===")
    print(f"Target File: {sample_path}")
    print()

    total_truth = 0
    total_intern = 0
    highlight_line = "Please keep the books  in the cupboard."

    with open(sample_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"{'Line #':<8}{'Truth Words':<14}{'Intern Words':<14}{'Status'}")
    print("-" * 50)

    for idx, line in enumerate(lines, start=1):
        t_count = truth_counter(line)
        i_count = intern_counter(line)
        total_truth += t_count
        total_intern += i_count

        status = "MATCH" if t_count == i_count else "MISMATCH [BUG]"
        print(f"{idx:<8}{t_count:<14}{i_count:<14}{status}")

    print("-" * 50)
    print()

    # Highlight specific offending line
    print("--- Detailed Highlight of Offending Line ---")
    print(f"Target Line: {repr(highlight_line)}")
    print(f"Truth Counter (regex r'\\S+'): {truth_counter(highlight_line)} words")
    print(f"Intern Counter (line.split(' ')): {intern_counter(highlight_line)} words")
    print(f"Intern Split Tokens: {highlight_line.split(' ')}")
    print(
        f"Artifact: Naive splitting produces empty string token `''` due to double space."
    )
    print()

    diff = total_intern - total_truth
    pct_error = ((total_intern - total_truth) / total_truth) * 100

    print("--- Summary Statistics ---")
    print(f"Total Truth Word Count:   {total_truth}")
    print(f"Total Intern Word Count:  {total_intern}")
    print(f"Total Word Count Difference: +{diff} words")
    print(f"Percentage Error:         +{pct_error:.2f}%")


if __name__ == "__main__":
    main()
