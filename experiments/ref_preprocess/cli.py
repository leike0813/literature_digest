#!/usr/bin/env python3
"""CLI for preprocessing a single reference text file."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .preprocessing import process_reference_text


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: python -m experiments.ref_preprocess.cli <ref_file> [--pretty]", file=sys.stderr)
        sys.exit(1)

    ref_path = Path(sys.argv[1])
    pretty = "--pretty" in sys.argv

    if not ref_path.exists():
        print(f"File not found: {ref_path}", file=sys.stderr)
        sys.exit(1)

    raw_text = ref_path.read_text(encoding="utf-8")
    result = process_reference_text(raw_text)

    indent = 2 if pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
