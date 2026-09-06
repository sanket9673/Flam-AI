#!/usr/bin/env python3
"""
download_flores.py - Downloads the FLORES-200 devtest split for multilingual evaluation.
Target languages:
  - English: eng_Latn -> data/corpus_flores/eng.txt
  - Hindi: hin_Deva   -> data/corpus_flores/hin.txt
  - Kannada: kan_Knda -> data/corpus_flores/kan.txt
  - Tamil: tam_Taml   -> data/corpus_flores/tam.txt
"""

import io
import sys
import tarfile
import urllib.request
from pathlib import Path
from typing import Dict, List

# Official FLORES-200 archive source
FLORES_TAR_URL = "https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz"

LANGUAGE_MAP = {
    "eng_Latn": "eng.txt",
    "hin_Deva": "hin.txt",
    "kan_Knda": "kan.txt",
    "tam_Taml": "tam.txt",
}


def clean_sentence(text: str) -> str:
    """Clean sentence by stripping whitespace and removing internal newlines."""
    text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    return text.strip()


def fetch_from_datasets() -> Dict[str, List[str]]:
    """Attempt loading via the datasets library."""
    import datasets

    data = {}
    for lang_code in LANGUAGE_MAP:
        try:
            ds = datasets.load_dataset("facebook/flores", lang_code, split="devtest")
            sentences = [clean_sentence(row["sentence"]) for row in ds]
            data[lang_code] = sentences
        except Exception as e:
            print(f"[Notice] Could not load '{lang_code}' via datasets library: {e}")
            return {}
    return data


def fetch_from_archive() -> Dict[str, List[str]]:
    """Download and extract devtest split directly from the official FLORES-200 archive."""
    print(f"Fetching FLORES-200 archive from {FLORES_TAR_URL} ...")
    req = urllib.request.Request(
        FLORES_TAR_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    with urllib.request.urlopen(req) as response:
        content = response.read()

    print("Extracting target devtest language files...")
    data = {}
    with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as tar:
        for member in tar.getmembers():
            for lang_code in LANGUAGE_MAP:
                # Archive path format: ./flores200_dataset/devtest/<lang_code>.devtest
                if f"devtest/{lang_code}.devtest" in member.name:
                    extracted_file = tar.extractfile(member)
                    if extracted_file is not None:
                        lines = extracted_file.read().decode("utf-8").splitlines()
                        cleaned_lines = [clean_sentence(line) for line in lines if line.strip()]
                        data[lang_code] = cleaned_lines

    return data


def main():
    root_dir = Path(__file__).resolve().parent.parent
    output_dir = root_dir / "data" / "corpus_flores"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Step 1: Fetching FLORES-200 devtest split...")
    corpus_data = fetch_from_datasets()
    if not corpus_data or len(corpus_data) < len(LANGUAGE_MAP):
        print("Falling back to direct archive fetch...")
        corpus_data = fetch_from_archive()

    # Verify all languages present
    for lang_code in LANGUAGE_MAP:
        if lang_code not in corpus_data:
            raise ValueError(f"Missing data for language code: {lang_code}")

    # Write files
    print("\nStep 2: Writing cleaned parallel corpora...")
    line_counts = {}
    for lang_code, filename in LANGUAGE_MAP.items():
        file_path = output_dir / filename
        sentences = corpus_data[lang_code]
        file_path.write_text("\n".join(sentences) + "\n", encoding="utf-8")
        line_counts[filename] = len(sentences)
        print(f"  - Wrote {len(sentences)} lines to {file_path.relative_to(root_dir)}")

    # Verification Logic
    print("\nStep 3: Verifying parallel integrity...")
    counts_set = set(line_counts.values())
    if len(counts_set) != 1:
        raise ValueError(
            f"Parallel integrity check failed! Inconsistent line counts across files: {line_counts}"
        )

    expected_count = list(counts_set)[0]
    if expected_count != 1012:
        print(f"[Warning] Expected 1012 lines for devtest split, found {expected_count}")

    print(f"[Success] All {len(line_counts)} corpus files verified with exact line count: {expected_count}")


if __name__ == "__main__":
    main()
