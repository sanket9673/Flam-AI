#!/usr/bin/env python3
"""
capture_baseline.py - Executes the intern's baseline fertility script and logs
the raw output into NOTEBOOK.md.
"""

import subprocess
import sys
from pathlib import Path


def main():
    root_dir = Path(__file__).resolve().parent.parent
    fertility_script = root_dir / "starter_kit" / "fertility.py"
    eng_sample = root_dir / "starter_kit" / "corpus_sample" / "eng_sample.txt"
    hin_sample = root_dir / "starter_kit" / "corpus_sample" / "hin_sample.txt"
    notebook_path = root_dir / "NOTEBOOK.md"

    # Command as specified
    cmd = [
        sys.executable,
        str(fertility_script.relative_to(root_dir)),
        f"--corpus=eng={eng_sample.relative_to(root_dir)}",
        f"--corpus=hin={hin_sample.relative_to(root_dir)}",
        "--tokenizer",
        "gpt2",
    ]

    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=root_dir,
        capture_output=True,
        text=True,
    )

    combined_output = result.stdout
    if result.stderr:
        combined_output += ("\nSTDERR:\n" + result.stderr)

    print("\n--- Raw Command Output ---")
    print(combined_output)
    print("--------------------------\n")

    # Read existing notebook
    notebook_content = notebook_path.read_text(encoding="utf-8")

    # Populate the Result section
    target_placeholder = "- **Result**: [To be populated by Step 3]"
    replacement = (
        "- **Result**:\n"
        "```text\n"
        f"{combined_output.strip()}\n"
        "```"
    )

    if target_placeholder in notebook_content:
        updated_content = notebook_content.replace(target_placeholder, replacement)
    else:
        updated_content = notebook_content + "\n" + replacement + "\n"

    notebook_path.write_text(updated_content, encoding="utf-8")
    print(f"Updated {notebook_path.relative_to(root_dir)} with baseline results.")


if __name__ == "__main__":
    main()
