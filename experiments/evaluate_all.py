#!/usr/bin/env python3
"""Batch evaluation of reference preprocessing against ground truth.

Usage:
  # Evaluate using precomputed results (default):
  python experiments/evaluate_all.py

  # Evaluate by running a plugin directly:
  python experiments/evaluate_all.py --plugin line-first

  # List available plugins:
  python experiments/evaluate_all.py --list-plugins

Produces:
  - experiments/evaluation_results.json    (detailed per-file scores)
  - experiments/deviation_report.json      (agent-readable deviation analysis)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from experiments.ref_preprocess.evaluation import (
    aggregate_results,
    assess_negative_case,
    evaluate_file,
    generate_deviation_report,
)

GT_DIR = Path(__file__).resolve().parent / "ground_truth"
PP_DIR = Path(__file__).resolve().parent / "preprocessed"
REF_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "reference_samples"
RESULTS_PATH = Path(__file__).resolve().parent / "evaluation_results.json"
REPORT_PATH = Path(__file__).resolve().parent / "deviation_report.json"

# Default output files (overwritten each run unless --output-suffix is given)
_OUTPUT_DIR = Path(__file__).resolve().parent


def _output_paths(suffix: str | None) -> tuple[Path, Path]:
    """Return (results_path, report_path) with optional suffix."""
    if not suffix:
        return _OUTPUT_DIR / "evaluation_results.json", _OUTPUT_DIR / "deviation_report.json"
    return (
        _OUTPUT_DIR / f"evaluation_results_{suffix}.json",
        _OUTPUT_DIR / f"deviation_report_{suffix}.json",
    )


def _find_pp_file(gt_stem: str, pp_dir: Path) -> Path | None:
    citekey = gt_stem[:8]
    candidates = sorted(pp_dir.glob(f"{citekey}*.json"))
    return candidates[0] if candidates else None


def _find_ref_file(gt_data: dict, ref_dir: Path) -> Path | None:
    """Find the original reference text file from gt_data's source_file."""
    src = gt_data.get("source_file", "")
    if not src:
        return None
    # src is like "tests/fixtures/reference_samples/xxx.txt"
    name = Path(src).name
    candidates = sorted(ref_dir.glob(f"{name[:8]}*.txt"))
    return candidates[0] if candidates else None


def _resolve_style(gt_data: dict) -> str:
    s = gt_data.get("entry_style", "")
    return "garbled_ocr" if s == "garbled_ocr_negative_case" else s


def evaluate_from_precomputed(
    gt_files: list[Path],
) -> tuple[list[dict], dict | None]:
    """Evaluate using precomputed JSON in experiments/preprocessed/."""
    results: list[dict] = []
    negative_case_result = None

    for i, gt_path in enumerate(gt_files):
        gt_data = json.loads(gt_path.read_text(encoding="utf-8"))
        gt_stem = gt_path.stem
        citekey = gt_stem[:8]

        pp_path = _find_pp_file(gt_stem, PP_DIR)
        if pp_path is None:
            print(f"  [{i+1:2d}] {citekey:8s}  SKIP (no preprocessed file)")
            continue

        pp_data = json.loads(pp_path.read_text(encoding="utf-8"))
        result, neg = _score_one(gt_data, pp_data, citekey)
        if neg:
            negative_case_result = result
        results.append(result)

        _print_one(i + 1, result, pp_data)

    return results, negative_case_result


def evaluate_with_plugin(
    gt_files: list[Path],
    plugin_name: str,
) -> tuple[list[dict], dict | None]:
    """Evaluate by running a plugin on each reference sample directly."""
    import experiments.ref_preprocess.plugins  # noqa: F401 — trigger registration
    from experiments.ref_preprocess.plugin_base import get_plugin

    plugin = get_plugin(plugin_name)
    results: list[dict] = []
    negative_case_result = None

    print(f"  Using plugin: {plugin.name}\n")

    for i, gt_path in enumerate(gt_files):
        gt_data = json.loads(gt_path.read_text(encoding="utf-8"))
        citekey = gt_path.stem[:8]
        is_negative = gt_data.get("is_negative_case", False)

        if is_negative:
            # Negative case: run plugin anyway
            ref_path = _find_ref_file(gt_data, REF_DIR)
            if ref_path is None:
                print(f"  [{i+1:2d}] {citekey:8s}  SKIP (no ref file)")
                continue
            raw = ref_path.read_text(encoding="utf-8")
            pp_data = plugin.process(raw)
            neg = assess_negative_case(pp_data)
            result: dict[str, Any] = {
                "_file_id": citekey,
                "is_negative_case": True,
                "entry_counts": {
                    "gt": len(gt_data.get("items", [])),
                    "pp": pp_data.get("meta", {}).get("entry_count", 0),
                },
                "negative_assessment": neg,
            }
            negative_case_result = result
            results.append(result)
            print(f"  [{i+1:2d}] {citekey:8s}  ⚠ NEGATIVE CASE  "
                  f"pp_entries={neg['pp_entry_count']:3d}  warnings={neg['warning_count']:3d}")
            continue

        ref_path = _find_ref_file(gt_data, REF_DIR)
        if ref_path is None:
            print(f"  [{i+1:2d}] {citekey:8s}  SKIP (no ref file)")
            continue

        raw = ref_path.read_text(encoding="utf-8")
        pp_data = plugin.process(raw)
        result, _ = _score_one(gt_data, pp_data, citekey)
        results.append(result)
        _print_one(i + 1, result, pp_data)

    return results, negative_case_result


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------


def _score_one(
    gt_data: dict, pp_data: dict, citekey: str
) -> tuple[dict, bool]:
    """Score one GT/PP pair. Returns (result_dict, is_negative)."""
    is_negative = gt_data.get("is_negative_case", False)

    if is_negative:
        neg = assess_negative_case(pp_data)
        result = {
            "_file_id": citekey,
            "is_negative_case": True,
            "entry_counts": {
                "gt": len(gt_data.get("items", [])),
                "pp": pp_data.get("meta", {}).get("entry_count", 0),
            },
            "negative_assessment": neg,
        }
        return result, True

    gt_data["entry_style"] = _resolve_style(gt_data)
    result = evaluate_file(gt_data, pp_data)
    result["_file_id"] = citekey
    return result, False


def _print_one(idx: int, result: dict, pp_data: dict | None = None) -> None:
    if result.get("is_negative_case"):
        return
    comp = result["composite_score"]
    dc = result["entry_counts"]
    dt = dc["delta"]
    sign = "+" if dt > 0 else ""
    align = result["alignment"]
    sa = result["scores"]["suspect_alert"]
    year_acc = result["scores"]["year_accuracy"]
    title_acc = result["scores"]["title_quality"]
    print(f"  [{idx:2d}] {result['_file_id']:8s}  "
          f"composite={comp:.3f}  "
          f"count={dc['gt']:3d}→{dc['pp']:3d} ({sign}{dt:3d})  "
          f"align={align['aligned_count']:2d}/{align['gt_total']:2d}  "
          f"year={year_acc['score']:.2f}  "
          f"title={title_acc['score']:.2f}  "
          f"style={'✓' if result['scores']['entry_style']['score']==1 else '✗'}  "
          f"gen_warn={sa['genuine_warnings']}/{sa['total_warnings']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate reference preprocessing")
    parser.add_argument(
        "--plugin", type=str, default=None,
        help="Run a preprocessing plugin directly (default: read precomputed JSON)",
    )
    parser.add_argument(
        "--list-plugins", action="store_true",
        help="List available preprocessing plugins and exit",
    )
    parser.add_argument(
        "--output-suffix", type=str, default=None,
        help="Suffix for output files (e.g. 'v11' → evaluation_results_v11.json)",
    )
    args = parser.parse_args()

    if args.list_plugins:
        import experiments.ref_preprocess.plugins  # noqa: F401 — trigger registration
        from experiments.ref_preprocess.plugin_base import list_plugins
        print("Available plugins:")
        for name in list_plugins():
            print(f"  {name}")
        return

    gt_files = sorted(GT_DIR.glob("*_ground_truth.json"))
    if not gt_files:
        print("No ground truth files found.", file=sys.stderr)
        sys.exit(1)

    print(f"Evaluating {len(gt_files)} ground truth files...\n")

    if args.plugin:
        results, neg_result = evaluate_with_plugin(gt_files, args.plugin)
    else:
        results, neg_result = evaluate_from_precomputed(gt_files)

    # Compute output paths
    res_path, rep_path = _output_paths(args.output_suffix)

    # Build data maps for deviation report
    gt_data_map: dict[str, dict] = {}
    pp_data_map: dict[str, dict] = {}

    for i, gt_path in enumerate(gt_files):
        gt = json.loads(gt_path.read_text(encoding="utf-8"))
        ck = gt_path.stem[:8]
        gt_data_map[ck] = gt

        pp_path = _find_pp_file(gt_path.stem, PP_DIR)
        if pp_path:
            pp_data_map[ck] = json.loads(pp_path.read_text(encoding="utf-8"))

    # Aggregate
    normal_results = [r for r in results if not r.get("is_negative_case")]
    aggregate = aggregate_results(normal_results)
    aggregate["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    aggregate["schema"] = "batch_evaluation.v1"
    aggregate["total_files"] = len(normal_results)

    if args.plugin:
        aggregate["plugin"] = args.plugin

    if neg_result:
        aggregate["negative_case"] = neg_result

    per_file_sorted = sorted(
        [r for r in results if not r.get("is_negative_case")],
        key=lambda r: r["composite_score"],
        reverse=True,
    )
    aggregate["per_file"] = per_file_sorted

    res_path.write_text(json.dumps(aggregate, ensure_ascii=False, indent=2))

    # Generate deviation report with detailed examples
    report = generate_deviation_report(results, gt_data_map, pp_data_map)
    report["timestamp"] = aggregate["timestamp"]
    if args.plugin:
        report["plugin"] = args.plugin
    rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))

    # Terminal summary
    print(f"\n{'='*70}")
    print(f"Completed: {len(normal_results)} normal + {1 if neg_result else 0} negative")
    print(f"Composite: "
          f"mean={aggregate['composite']['mean']:.3f}  "
          f"median={aggregate['composite']['median']:.3f}  "
          f"min={aggregate['composite']['min']:.3f}  "
          f"max={aggregate['composite']['max']:.3f}")
    print(f"Year accuracy: mean={aggregate['year_accuracy']['mean']:.3f}")
    print(f"Title quality: mean={aggregate['title_quality']['mean']:.3f}")
    print(f"Over-split files (delta > 10): {aggregate['diagnostics']['over_split_files']}")
    print(f"Style mismatches: {len(aggregate['diagnostics']['style_mismatches'])}")

    dev = report.get("summary", {})
    types = dev.get("by_type", {})
    print(f"\nDeviation report: {sum(types.values())} concrete examples "
          f"(over_split={types.get('over_split',0)}, "
          f"year={types.get('year_error',0)}, "
          f"title={types.get('title_error',0)}, "
          f"author={types.get('author_error',0)}, "
          f"style={types.get('style_mismatch',0)})")
    for theme in report.get("common_themes", []):
        print(f"  • [{theme['pattern']}] {theme['diagnosis'][:100]}…")
        ex = theme.get("example", {})
        if ex:
            print(f"    ↳ e.g. {ex['file']}: GT=\"{ex.get('what_gt_expected','')[:60]}…\" "
                  f"→ PP=\"{ex.get('what_script_produced','')[:60]}…\"")

    if neg_result:
        neg = neg_result["negative_assessment"]
        print(f"\nNegative case (M68XPFA9): self_awareness={neg['self_awareness_score']:.3f}")

    print(f"\nResults:  {res_path}")
    print(f"Report:   {rep_path}")


if __name__ == "__main__":
    main()
