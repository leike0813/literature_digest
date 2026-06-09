"""Evaluation framework for comparing deterministic reference preprocessing against ground truth.

Provides scoring dimensions:
1. Entry count matching
2. Entry style classification
3. Year extraction accuracy
4. Title boundary quality (word-token F1)
5. Author detection (count proximity)
6. Suspect block / warning density
7. Negative case self-awareness (separate)
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Utility: text tokenization and similarity
# ---------------------------------------------------------------------------


def tokenize(text: str) -> set[str]:
    """Lowercase, split on whitespace and common punctuation, return word set.

    Preserves CJK characters as individual unigrams so that Chinese titles
    get meaningful similarity scores (not zeroed out by the Latin filter).
    """
    import re
    cjk_tokens = set(re.findall(r'[一-鿿㐀-䶿豈-﫿]', text))
    latin = re.sub(r'[一-鿿㐀-䶿豈-﫿]', ' ', text)
    latin_tokens = set(
        t for t in re.sub(r"[^a-z0-9]+", " ", latin.lower()).split()
        if len(t) >= 2
    )
    return cjk_tokens | latin_tokens


def jaccard_similarity(a: str, b: str) -> float:
    tokens_a = tokenize(a)
    tokens_b = tokenize(b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


# ---------------------------------------------------------------------------
# Entry alignment
# ---------------------------------------------------------------------------


def match_entries(
    gt_items: list[dict[str, Any]],
    pp_entries: list[dict[str, Any]],
    threshold: float = 0.25,
) -> dict[int, dict[str, Any]]:
    """Greedy 1:1 matching of GT items to PP entries by raw text Jaccard.

    Returns {gt_index: {"pp_index": int, "similarity": float}}.
    """
    matches: dict[int, dict[str, Any]] = {}
    used_pp: set[int] = set()

    for gi, gt_item in enumerate(gt_items):
        gt_raw = gt_item.get("raw", "")
        best_score = threshold
        best_pi = None

        for pi, pp_entry in enumerate(pp_entries):
            if pi in used_pp:
                continue
            pp_raw = (pp_entry.get("raw", "")
                      or pp_entry.get("source_text", "")
                      or "")
            if not pp_raw:
                continue
            score = jaccard_similarity(gt_raw, pp_raw)
            if score > best_score:
                best_score = score
                best_pi = pi

        if best_pi is not None:
            used_pp.add(best_pi)
            matches[gi] = {"pp_index": best_pi, "similarity": best_score}

    return matches


# ---------------------------------------------------------------------------
# Best candidate extraction
# ---------------------------------------------------------------------------


def _best_candidate(pp_entry: dict[str, Any]) -> dict[str, Any] | None:
    """Return the candidate with highest confidence, excluding fallback if better exists."""
    patterns = pp_entry.get("patterns", [])
    if not patterns:
        return None
    # Sort by confidence descending
    sorted_candidates = sorted(patterns, key=lambda c: c.get("confidence", 0), reverse=True)
    return sorted_candidates[0]


# ---------------------------------------------------------------------------
# Dimension scorers
# ---------------------------------------------------------------------------


def score_entry_count(gt_count: int, pp_count: int) -> dict[str, Any]:
    """Dimension 1: Entry count proximity."""
    if gt_count == 0 and pp_count == 0:
        score = 1.0
    elif gt_count == 0 or pp_count == 0:
        score = 0.0
    else:
        score = 1.0 - abs(pp_count - gt_count) / max(pp_count, gt_count)
    return {
        "score": max(0.0, min(1.0, score)),
        "gt_count": gt_count,
        "pp_count": pp_count,
        "delta": pp_count - gt_count,
    }


def score_entry_style(gt_style: str, pp_style: str) -> dict[str, Any]:
    """Dimension 2: Entry style classification exact match."""
    return {
        "score": 1.0 if gt_style == pp_style else 0.0,
        "gt_style": gt_style,
        "pp_style": pp_style,
    }


def score_year_accuracy(
    gt_items: list[dict[str, Any]],
    matches: dict[int, dict[str, Any]],
    pp_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    """Dimension 3: Year extraction accuracy for aligned entries."""
    correct = 0
    total = 0
    errors: list[dict[str, Any]] = []

    for gi, match_info in matches.items():
        gt_item = gt_items[gi]
        gt_year = gt_item.get("year")
        if gt_year is None:
            continue  # skip entries where GT has no year
        pi = match_info["pp_index"]
        pp_entry = pp_entries[pi]
        candidate = _best_candidate(pp_entry)
        pp_year = candidate.get("year_candidate") if candidate else None

        total += 1
        if pp_year == gt_year:
            correct += 1
        else:
            errors.append({
                "gt_index": gi,
                "pp_index": pi,
                "gt_year": gt_year,
                "pp_year": pp_year,
            })

    accuracy = correct / total if total > 0 else 0.0
    return {
        "score": accuracy,
        "correct": correct,
        "total": total,
        "errors": errors,
    }


def _word_f1(pred_text: str, gt_text: str) -> float:
    """Compute word-token-level F1 between two text strings.

    CJK characters are preserved as individual unigrams (same as tokenize).
    """
    import re
    def _tok(s: str) -> set[str]:
        cjk = set(re.findall(r'[一-鿿㐀-䶿豈-﫿]', s))
        latin = re.sub(r'[一-鿿㐀-䶿豈-﫿]', ' ', s)
        words = set(
            t for t in re.sub(r"[^a-z0-9]+", " ", latin.lower()).split()
            if len(t) >= 2
        )
        return cjk | words
    pred_tokens = _tok(pred_text)
    gt_tokens = _tok(gt_text)
    if not gt_tokens and not pred_tokens:
        return 1.0
    if not gt_tokens or not pred_tokens:
        return 0.0
    intersection = gt_tokens & pred_tokens
    precision = len(intersection) / len(pred_tokens)
    recall = len(intersection) / len(gt_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def score_title_quality(
    gt_items: list[dict[str, Any]],
    matches: dict[int, dict[str, Any]],
    pp_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    """Dimension 4: Title boundary quality via word-token F1."""
    f1_scores: list[float] = []

    for gi, match_info in matches.items():
        gt_item = gt_items[gi]
        gt_title = gt_item.get("title", "")
        if not gt_title:
            continue

        pi = match_info["pp_index"]
        candidate = _best_candidate(pp_entries[pi])
        if candidate is None:
            continue

        pp_title = candidate.get("title_candidate", "") or ""
        f1 = _word_f1(pp_title, gt_title)
        f1_scores.append(f1)

    mean_f1 = statistics.mean(f1_scores) if f1_scores else 0.0
    return {
        "score": mean_f1,
        "aligned_count": len(f1_scores),
        "mean_f1": mean_f1,
    }


def score_author_detection(
    gt_items: list[dict[str, Any]],
    matches: dict[int, dict[str, Any]],
    pp_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    """Dimension 5: Author count proximity for aligned entries."""
    accuracies: list[float] = []

    for gi, match_info in matches.items():
        gt_item = gt_items[gi]
        gt_authors = gt_item.get("author", [])
        gt_count = len(gt_authors)
        if gt_count == 0:
            continue

        pi = match_info["pp_index"]
        candidate = _best_candidate(pp_entries[pi])
        if candidate is None:
            continue
        pp_count = len(candidate.get("author_candidates", []))
        if pp_count == 0:
            continue

        entry_score = 1.0 - abs(pp_count - gt_count) / max(pp_count, gt_count, 1)
        accuracies.append(max(0.0, entry_score))

    mean_acc = statistics.mean(accuracies) if accuracies else 0.0
    return {
        "score": mean_acc,
        "aligned_count": len(accuracies),
        "mean_count_accuracy": mean_acc,
    }


def score_suspect_alert(pp_data: dict[str, Any]) -> dict[str, Any]:
    """Dimension 6: Warning/suspect density as self-consistency measure.

    Only counts "genuine" warnings — excludes pattern_ambiguous and numbering
    anomalies which are normal algorithm behavior (multiple candidates per
    entry is a feature, not a problem). Genuine warnings are:
      - reference_entry_grouping_suspect: potential grouped entries
      - reference_title_boundary_suspect: title boundary likely wrong
    """
    warnings = pp_data.get("warnings", [])
    entry_count = pp_data.get("meta", {}).get("entry_count", 1)
    if entry_count <= 0:
        entry_count = 1

    # Count only genuine warnings
    genuine_warnings = [
        w for w in warnings
        if w.startswith("reference_entry_grouping_suspect")
        or w.startswith("reference_title_boundary_suspect")
    ]
    all_warnings_count = len(warnings)
    genuine_count = len(genuine_warnings)
    genuine_wpe = genuine_count / entry_count

    # Score: 1.0 at 0 genuine warnings/entry → 0.0 at >=0.15 genuine w/e
    # Threshold 0.15 means: up to ~1.5 genuine warnings per 10 entries is OK
    raw_score = 1.0 - min(1.0, genuine_wpe / 0.15)
    score = max(0.0, raw_score)

    return {
        "score": score,
        "total_warnings": all_warnings_count,
        "genuine_warnings": genuine_count,
        "pattern_ambiguous": all_warnings_count - genuine_count,
        "suspect_blocks": len(pp_data.get("suspect_blocks", [])),
        "genuine_warnings_per_entry": genuine_wpe,
        "entry_count": entry_count,
    }


# ---------------------------------------------------------------------------
# Composite
# ---------------------------------------------------------------------------

WEIGHTS: dict[str, float] = {
    "entry_count": 0.20,
    "entry_style": 0.10,
    "year_accuracy": 0.25,
    "title_quality": 0.25,
    "author_detection": 0.10,
    "suspect_alert": 0.10,
}


def compute_composite(scores: dict[str, dict[str, Any]]) -> float:
    """Weighted sum of dimension scores."""
    total = 0.0
    for dim, weight in WEIGHTS.items():
        dim_score = scores.get(dim, {}).get("score", 0.0)
        total += weight * dim_score
    return total


# ---------------------------------------------------------------------------
# Per-file evaluation
# ---------------------------------------------------------------------------


def evaluate_file(
    gt_data: dict[str, Any],
    pp_data: dict[str, Any],
) -> dict[str, Any]:
    """Run all scoring dimensions on a single GT/PP pair."""
    gt_items = gt_data.get("items", [])
    pp_entries = pp_data.get("entries", [])
    pp_meta = pp_data.get("meta", {})
    gt_count = len(gt_items)
    pp_count = pp_meta.get("entry_count", len(pp_entries))

    # Alignment
    matches = match_entries(gt_items, pp_entries)

    # Dimensions
    scores: dict[str, dict[str, Any]] = {}
    scores["entry_count"] = score_entry_count(gt_count, pp_count)
    scores["entry_style"] = score_entry_style(
        gt_data.get("entry_style", ""),
        pp_meta.get("entry_style", ""),
    )
    scores["year_accuracy"] = score_year_accuracy(gt_items, matches, pp_entries)
    scores["title_quality"] = score_title_quality(gt_items, matches, pp_entries)
    scores["author_detection"] = score_author_detection(gt_items, matches, pp_entries)
    scores["suspect_alert"] = score_suspect_alert(pp_data)

    composite = compute_composite(scores)

    # Alignment summary
    alignment_summary = {
        "gt_total": gt_count,
        "pp_total": pp_count,
        "aligned_count": len(matches),
        "unmatched_gt": gt_count - len(matches),
        "avg_similarity": (
            statistics.mean(m["similarity"] for m in matches.values())
            if matches else 0.0
        ),
    }

    return {
        "entry_counts": {"gt": gt_count, "pp": pp_count, "delta": pp_count - gt_count},
        "entry_style": {"gt": gt_data.get("entry_style", ""), "pp": pp_meta.get("entry_style", "")},
        "alignment": alignment_summary,
        "scores": scores,
        "composite_score": composite,
        "is_negative_case": gt_data.get("is_negative_case", False),
    }


# ---------------------------------------------------------------------------
# Negative case assessment
# ---------------------------------------------------------------------------


def assess_negative_case(pp_data: dict[str, Any]) -> dict[str, Any]:
    """Dimension 7: Self-awareness assessment for negative case only.

    Measures whether the algorithm recognizes it cannot process the input.
    """
    entry_count = pp_data.get("meta", {}).get("entry_count", 0)
    warnings = pp_data.get("warnings", [])
    warnings_per_entry = len(warnings) / max(entry_count, 1)

    # Entry count anomaly: high entry_count from garbage = bad awareness
    entry_anomaly = min(1.0, entry_count / 50.0)

    # Warning awareness: high warning density = algorithm senses problems
    warning_awareness = min(1.0, warnings_per_entry / 1.0)

    # Effective entry_count gap: should be near 0 for garbled text
    # Combine: low entry_anomaly (=few entries from garbage) + high warning_awareness
    self_awareness = (1.0 - entry_anomaly) * 0.3 + warning_awareness * 0.7

    return {
        "self_awareness_score": self_awareness,
        "pp_entry_count": entry_count,
        "warning_count": len(warnings),
        "warnings_per_entry": warnings_per_entry,
        "suspect_blocks": len(pp_data.get("suspect_blocks", [])),
    }


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

DIM_LABELS = ["entry_count", "entry_style", "year_accuracy",
              "title_quality", "author_detection", "suspect_alert"]


def aggregate_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute summary statistics across all evaluated files."""
    composites = [r["composite_score"] for r in results]
    dim_scores: dict[str, list[float]] = {d: [] for d in DIM_LABELS}
    negative_assessments: list[dict[str, Any]] = []

    for r in results:
        if r.get("is_negative_case"):
            negative_assessments.append(r)
        for d in DIM_LABELS:
            dim_scores[d].append(r["scores"].get(d, {}).get("score", 0.0))

    def _stats(vals: list[float]) -> dict[str, float]:
        if not vals:
            return {"mean": 0.0, "min": 0.0, "max": 0.0, "median": 0.0, "std": 0.0}
        return {
            "mean": statistics.mean(vals),
            "median": statistics.median(vals),
            "min": min(vals),
            "max": max(vals),
            "std": statistics.stdev(vals) if len(vals) > 1 else 0.0,
        }

    aggregate: dict[str, Any] = {
        "total_files": len(results),
        "composite": _stats(composites),
    }
    for d in DIM_LABELS:
        aggregate[d] = _stats(dim_scores[d])

    # Top/bottom 5 by composite
    sorted_results = sorted(results, key=lambda r: r["composite_score"], reverse=True)
    aggregate["top_5"] = [
        {"file": r.get("_file_id", "?"), "composite": r["composite_score"]}
        for r in sorted_results[:5]
    ]
    aggregate["bottom_5"] = [
        {"file": r.get("_file_id", "?"), "composite": r["composite_score"]}
        for r in sorted_results[-5:]
    ]

    # Diagnostics
    over_splitters = [
        r for r in results
        if r["entry_counts"]["delta"] > 10 and not r.get("is_negative_case")
    ]
    style_mismatches = [
        r for r in results
        if r["entry_style"]["gt"] != r["entry_style"]["pp"]
    ]
    low_align = [
        r for r in results
        if not r.get("is_negative_case")
        and r["alignment"]["gt_total"] > 0
        and r["alignment"]["aligned_count"] / r["alignment"]["gt_total"] < 0.5
    ]

    aggregate["diagnostics"] = {
        "over_split_files": len(over_splitters),
        "over_split_examples": [
            {"file": r.get("_file_id", "?"), "delta": r["entry_counts"]["delta"]}
            for r in over_splitters[:10]
        ],
        "style_mismatches": [
            {"file": r.get("_file_id", "?"),
             "gt": r["entry_style"]["gt"],
             "pp": r["entry_style"]["pp"]}
            for r in style_mismatches
        ],
        "low_alignment_files": [
            {"file": r.get("_file_id", "?"),
             "rate": f"{r['alignment']['aligned_count']}/{r['alignment']['gt_total']}"}
            for r in low_align
        ],
    }

    if negative_assessments:
        aggregate["negative_case"] = negative_assessments[0]

    return aggregate


# ---------------------------------------------------------------------------
# Deviation report (agent-readable)
# ---------------------------------------------------------------------------


def _safe(txt: str, max_len: int = 120) -> str:
    """Truncate text for display, preserving the core message."""
    if len(txt) <= max_len:
        return txt
    return txt[:max_len] + "…"


def _find_by_key(
    data_map: dict[str, dict[str, Any]] | None,
    citekey: str,
    idx: int | None = None,
) -> dict[str, Any] | None:
    """Look up an item in a data map by citekey and optional item index."""
    if data_map is None:
        return None
    file_data = data_map.get(citekey)
    if file_data is None:
        return None
    if idx is None:
        return file_data
    # GT files use "items", preprocessed files use "entries"
    collection = file_data.get("items") or file_data.get("entries") or []
    if 0 <= idx < len(collection):
        return collection[idx]
    return None


def _best_pp_title(pp_entry: dict[str, Any] | None) -> str:
    """Extract the best title_candidate from a PP entry."""
    if pp_entry is None:
        return ""
    patterns = pp_entry.get("patterns", []) or []
    if not patterns:
        return ""
    best = max(patterns, key=lambda c: c.get("confidence", 0))
    return best.get("title_candidate", "") or ""


def _gt_author_str(gt_item: dict[str, Any] | None) -> str:
    if gt_item is None:
        return ""
    authors = gt_item.get("author", [])
    return "; ".join(str(a) for a in authors[:5]) if authors else "(no author)"


def _make_example(
    citekey: str,
    case_type: str,
    what_gt: str,
    what_pp: str,
    raw_text: str,
    reason: str,
) -> dict[str, str]:
    return {
        "file": citekey,
        "type": case_type,
        "what_gt_expected": what_gt,
        "what_script_produced": what_pp,
        "raw_text": _safe(raw_text, 200),
        "root_cause": reason,
    }


def generate_deviation_report(
    results: list[dict[str, Any]],
    gt_data_map: dict[str, dict[str, Any]] | None = None,
    pp_data_map: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generate a structured deviation report with concrete before/after examples.

    Each deviation entry shows:
      - what_gt_expected: what the correct value is
      - what_script_produced: what the script actually produced
      - raw_text: the original text that confused the script
      - root_cause: diagnosis of why the script got it wrong
    """
    examples: list[dict[str, str]] = []

    for r in results:
        fid = r.get("_file_id", "?")
        if r.get("is_negative_case"):
            continue

        gt_items = (gt_data_map or {}).get(fid, {}).get("items", []) if gt_data_map else []
        pp_entries = (pp_data_map or {}).get(fid, {}).get("entries", []) if pp_data_map else []

        # ---- Over-split examples ----
        dc = r["entry_counts"]
        if abs(dc["delta"]) > 30 and gt_items:
            # Show the raw text of a reference that got over-split
            mid_gt = gt_items[len(gt_items) // 2] if len(gt_items) > 1 else gt_items[0]
            examples.append(_make_example(
                fid, "over_split",
                f"1 reference entry: {_safe(mid_gt.get('raw',''), 100)}",
                f"Script split into many fragments (GT={dc['gt']} entries → PP={dc['pp']} entries)",
                mid_gt.get("raw", ""),
                "Trailing page number markers (e.g. ' 1, 2, 7') at end-of-line "
                "are parsed as new entry starts by the inline-split regex.",
            ))

        # ---- Style mismatch examples ----
        if r["entry_style"]["gt"] != r["entry_style"]["pp"] and gt_items:
            gt_item = gt_items[0]
            examples.append(_make_example(
                fid, "style_mismatch",
                f"style={r['entry_style']['gt']} (e.g. entry starts with [{gt_item.get('entry_index',0)}])",
                f"style={r['entry_style']['pp']} (detected as mixed due to trailing markers)",
                gt_item.get("raw", ""),
                "Lines have trailing page numbers like '...2017. 1, 2' — the '1, ' "
                "part triggers the author-year detection, overriding the numeric prefix.",
            ))

        # ---- Year error examples (top 2 per file) ----
        ye = r["scores"]["year_accuracy"]
        if ye.get("errors"):
            shown = 0
            for err in ye["errors"]:
                if shown >= 2:
                    break
                gi = err["gt_index"]
                pi = err["pp_index"]
                gt_item = _find_by_key(gt_data_map, fid, gi) if gt_data_map else None
                pp_entry = _find_by_key(pp_data_map, fid, pi) if pp_data_map else None
                pp_candidate = max(
                    (pp_entry.get("patterns", []) or []),
                    key=lambda c: c.get("confidence", 0),
                ) if pp_entry else {}

                gt_raw = (gt_item or {}).get("raw", "")
                pp_raw = (pp_entry or {}).get("raw", "")
                pp_year_src = pp_candidate.get("year_candidate", "?")
                selected_pattern = pp_candidate.get("pattern", "?")

                examples.append(_make_example(
                    fid, "year_error",
                    f"year={err['gt_year']}",
                    f"year={err['pp_year']} (pattern={selected_pattern}, "
                    f"extracted from: {_safe(str(pp_year_src), 40)})",
                    gt_raw or pp_raw,
                    f"The best candidate pattern ({selected_pattern}) picked year "
                    f"{err['pp_year']} from trailing text (page markers, volume numbers) "
                    f"rather than the actual publication year {err['gt_year']}.",
                ))
                shown += 1

        # ---- Title quality examples (top 2 per file) ----
        tq = r["scores"]["title_quality"]
        if tq["score"] < 0.3 and tq["aligned_count"] > 0 and gt_items:
            shown = 0
            for gi in range(min(len(gt_items), tq["aligned_count"])):
                if shown >= 2:
                    break
                gt_item = gt_items[gi]
                if not gt_item.get("title"):
                    continue
                gt_title = gt_item["title"]
                # Find matching PP entry
                pp_entry = pp_entries[gi] if gi < len(pp_entries) else None
                if pp_entry is None:
                    continue
                pp_title = _best_pp_title(pp_entry)
                if _word_f1(pp_title, gt_title) >= 0.3:
                    continue

                examples.append(_make_example(
                    fid, "title_error",
                    f"title=\"{_safe(gt_title, 80)}\"",
                    f"title=\"{_safe(pp_title, 80)}\"",
                    _safe(gt_item.get("raw", ""), 200),
                    f"Format \"Surname, I.:\" (LaTeX BibTeX / IEEE style) — the period after "
                    f"authors is parsed as end-of-sentence by authors_period_title pattern, "
                    f"so the actual author block colon and everything after the first period "
                    f"becomes the 'title'.",
                ))
                shown += 1

        # ---- Author detection issues (top 1 per file) ----
        ad = r["scores"]["author_detection"]
        if ad["score"] < 0.5 and ad["aligned_count"] > 0 and gt_items:
            for gi in range(min(3, len(gt_items))):
                pi = r.get("alignment", {}).get(str(gi), {}).get("pp_index")
                if pi is None:
                    continue
                pp_entry = pp_entries[pi] if pi < len(pp_entries) else None
                if pp_entry is None:
                    continue
                pp_cand = max(
                    (pp_entry.get("patterns", []) or []),
                    key=lambda c: c.get("confidence", 0),
                ) if pp_entry.get("patterns") else {}
                if not pp_cand:
                    continue
                gt_authors = len(gt_items[gi].get("author", []))
                pp_authors = len(pp_cand.get("author_candidates", []))
                if abs(pp_authors - gt_authors) > 2:
                    examples.append(_make_example(
                        fid, "author_error",
                        f"{gt_authors} authors (e.g. {_gt_author_str(gt_items[gi])})",
                        f"{pp_authors} candidates (text=\"{_safe(pp_cand.get('author_text',''), 60)}\")",
                        _safe(gt_items[gi].get("raw", ""), 200),
                        f"The heuristic author split ({pp_cand.get('pattern', '?')}) mis-parses "
                        f"the boundary between authors and title, merging partial names.",
                    ))
                    break

    # ---- Synthesize common themes with concrete evidence ----
    over_split_exs = [e for e in examples if e["type"] == "over_split"]
    title_exs = [e for e in examples if e["type"] == "title_error"]
    year_exs = [e for e in examples if e["type"] == "year_error"]
    style_exs = [e for e in examples if e["type"] == "style_mismatch"]

    themes: list[dict] = []
    if over_split_exs:
        themes.append({
            "pattern": "over_split_by_page_markers",
            "impact": f"{len(over_split_exs)} files",
            "diagnosis": "Lines ending with '1, 2, 7' (in-text citation page markers) "
                         "are treated as new reference entries by the inline-split logic.",
            "example": over_split_exs[0],
        })
    if style_exs:
        themes.append({
            "pattern": "style_detection_fooled_by_trailing_markers",
            "impact": f"{len(style_exs)} files",
            "diagnosis": "Trailing numbers ' 1, 2, 7' cause the author-year detector "
                         "to think the entry is 'mixed' style.",
            "example": style_exs[0],
        })
    if title_exs:
        themes.append({
            "pattern": "laTeX_bib_format_title_boundary",
            "impact": f"{len(title_exs)} files",
            "diagnosis": "'Surname, I.:' format — authors_period_title pattern splits on "
                         "the first period (after author block) rather than the period after "
                         "the actual title, so 'In: Proceedings of...' becomes the title.",
            "example": title_exs[0],
        })
    if year_exs:
        themes.append({
            "pattern": "year_from_trailing_text",
            "impact": f"{len(year_exs)} entries across multiple files",
            "diagnosis": "Volume/page numbers like '39(6):1137–1149' contain 4-digit "
                         "numbers that are picked up as publication years.",
            "example": year_exs[0],
        })

    return {
        "schema": "deviation_report.v2",
        "summary": {
            "total_files": len([r for r in results if not r.get("is_negative_case")]),
            "total_examples": len(examples),
            "by_type": {
                "over_split": len(over_split_exs),
                "style_mismatch": len(style_exs),
                "year_error": len(year_exs),
                "title_error": len(title_exs),
                "author_error": len([e for e in examples if e["type"] == "author_error"]),
            },
        },
        "common_themes": themes,
        "examples": examples,
    }
