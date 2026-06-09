#!/usr/bin/env python3
"""Batch-preprocess all reference samples and write results to experiments/preprocessed/.

Usage:
  python experiments/preprocess_all.py                          # v1 baseline
  python experiments/preprocess_all.py --plugin line-first-v15  # v1.5
  python experiments/preprocess_all.py --list-plugins           # list available
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REF_SAMPLES_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "reference_samples"
OUTPUT_DIR = Path(__file__).resolve().parent / "preprocessed"


def collect_sample_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for entry in sorted(root.iterdir()):
        if not entry.is_file():
            continue
        if entry.suffix.lower() != ".txt":
            continue
        if entry.name in ("index.json", "extract_refs.py"):
            continue
        files.append(entry)
    return files


def summarize(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    total_entries = sum(r["meta"]["entry_count"] for r in results.values())
    total_candidates = sum(r["meta"]["candidate_count"] for r in results.values())
    total_suspects = sum(r["meta"]["grouping_suspect_count"] for r in results.values())
    total_warnings = sum(len(r.get("warnings", [])) for r in results.values())
    styles: dict[str, int] = {}
    for r in results.values():
        style = r["meta"]["entry_style"]
        styles[style] = styles.get(style, 0) + 1

    return {
        "total_files": len(results),
        "total_entries": total_entries,
        "total_candidates": total_candidates,
        "total_suspect_blocks": total_suspects,
        "total_warnings": total_warnings,
        "entry_styles": styles,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch-preprocess reference samples")
    parser.add_argument("--plugin", type=str, default=None, help="Plugin name (default: v1 baseline)")
    parser.add_argument("--list-plugins", action="store_true", help="List available plugins")
    args = parser.parse_args()

    if args.list_plugins:
        import experiments.ref_preprocess.plugins  # noqa: F401
        from experiments.ref_preprocess.plugin_base import list_plugins
        print("Available plugins:")
        for name in list_plugins():
            print(f"  {name}")
        return

    if args.plugin:
        import experiments.ref_preprocess.plugins  # noqa: F401
        from experiments.ref_preprocess.plugin_base import get_plugin
        preprocessor = get_plugin(args.plugin)
        label = f"plugin: {args.plugin}"
    else:
        preprocessor = None
        label = "v1 baseline (process_reference_text)"

    sample_files = collect_sample_files(REF_SAMPLES_DIR)
    if not sample_files:
        print(f"No .txt files found in {REF_SAMPLES_DIR}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Processing {len(sample_files)} reference samples ({label})...")

    all_results: dict[str, dict[str, Any]] = {}
    for i, filepath in enumerate(sample_files):
        raw_text = filepath.read_text(encoding="utf-8")
        if preprocessor:
            result = preprocessor.process(raw_text)
        else:
            result = process_reference_text(raw_text)

        stem = filepath.stem  # e.g. "S86GB385_Accelerating DETR..."
        out_path = OUTPUT_DIR / f"{stem}.json"
        out_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        all_results[stem] = result

        suspect_count = result["meta"]["grouping_suspect_count"]
        warnings_count = len(result.get("warnings", []))
        print(
            f"  [{i+1:2d}/{len(sample_files)}] {stem[:60]:60s} "
            f"entries={result['meta']['entry_count']:3d} "
            f"style={result['meta']['entry_style']:12s} "
            f"candidates={result['meta']['candidate_count']:3d} "
            f"suspect_blocks={suspect_count} "
            f"warnings={warnings_count}"
        )

    # Write summary
    summary = summarize(all_results)
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\nSummary ({len(all_results)} files):")
    print(f"  Total entries:     {summary['total_entries']}")
    print(f"  Total candidates:  {summary['total_candidates']}")
    print(f"  Suspect blocks:    {summary['total_suspect_blocks']}")
    print(f"  Total warnings:    {summary['total_warnings']}")
    print(f"  Entry styles:      {summary['entry_styles']}")
    print(f"\nResults written to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
