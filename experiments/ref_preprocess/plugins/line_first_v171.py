"""v1.7.1 preprocessing algorithm plugin — v1.7 + file-level quality detection.

Detects files whose overall quality makes them unprocessable (negative cases
such as severe OCR corruption).  Unlike per-entry warnings which flag
individual entries, the file-level check computes holistic signals across
all entries and candidates.

Signals monitored:
  1. **Fallback ratio** — entries whose best candidate is fallback_raw_split
  2. **Year ratio** — entries with a valid year_candidate
  3. **Warning density** — warnings per entry
  4. **Numbering anomaly** — has_numbering_anomaly from the reference detector
  5. **Empty-title ratio** — entries whose best candidate has no title

When ≥4 of 5 signals exceed thresholds, a ``file_quality_low`` warning is
emitted and a ``file_quality`` signal dict is included in the output meta.
"""

from __future__ import annotations

from typing import Any

from experiments.ref_preprocess.plugin_base import ReferencePreprocessor, register
from experiments.ref_preprocess.preprocessing import (
    COMMA_STYLE_AUTHOR_RE,
    LEADING_PUNCTUATION_RE,
    NON_REFERENCE_LINE_RE,
    REFERENCE_TAIL_AT_END_RE,
    Scope,
    _build_reference_batches,
    _detect_reference_block_suspicions,
    _generate_reference_candidates,
    _is_valid_publication_year,
    _protect_author_initials,
    _restore_initials,
    _strip_trailing_page_markers,
    build_workset_export,
    prepare_reference_workset,
)
from .line_first_v17 import (
    _generate_candidates_cjk,
    _has_cjk,
    _is_cjk_entry,
    _merge_bilingual_entries,
)

# ---------------------------------------------------------------------------
# File-level quality detection
# ---------------------------------------------------------------------------

# Composite thresholds: at least 3 of 5 signals must cross their trigger
# boundary to emit a file_quality_low warning.
_FALLBACK_THRESHOLD = 0.50   # >50% of entries use fallback pattern
_YEAR_THRESHOLD = 0.20       # <20% of entries have valid year
_WARNING_DENSITY_THRESHOLD = 1.0  # >1 warning per entry
_EMPTY_TITLE_THRESHOLD = 0.30     # >30% of entries have empty title


def _detect_file_quality(
    entries: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    has_numbering_anomaly: bool,
    warnings: list[str],
) -> tuple[list[str], dict[str, float]]:
    """Compute file-level quality signals and emit warnings for negative cases.

    Returns:
        (quality_warnings, signals) where signals is a dict of computed
        signal values for downstream inspection.
    """
    entry_count = len(entries) or 1
    signals: dict[str, float] = {}

    # Build best-candidate lookup (lowest candidate_index per entry)
    best_by_entry: dict[int, dict[str, Any]] = {}
    for c in candidates:
        ei = int(c["entry_index"])
        if ei not in best_by_entry:
            best_by_entry[ei] = c

    best_candidates = list(best_by_entry.values())
    best_count = len(best_candidates) or 1

    # Signal 1: fallback_best_ratio — entries using fallback_raw_split as best
    fallback_count = sum(
        1 for c in best_candidates
        if str(c.get("pattern", "")) == "fallback_raw_split"
    )
    fallback_ratio = fallback_count / best_count
    signals["fallback_best_ratio"] = fallback_ratio

    # Signal 2: year_ratio — entries with a valid year_candidate
    year_count = sum(
        1 for c in best_candidates
        if c.get("year_candidate") is not None
    )
    year_ratio = year_count / best_count
    signals["year_ratio"] = year_ratio

    # Signal 3: warning_density — total warnings / entry count
    warning_density = len(warnings) / entry_count
    signals["warning_density"] = warning_density

    # Signal 4: numbering_anomaly flag (already computed by pipeline)
    signals["numbering_anomaly"] = 1.0 if has_numbering_anomaly else 0.0

    # Signal 5: empty_title_ratio — best candidates with no title text
    empty_title_count = sum(
        1 for c in best_candidates
        if not str(c.get("title_candidate", "")).strip()
    )
    empty_title_ratio = empty_title_count / best_count
    signals["empty_title_ratio"] = empty_title_ratio

    # Composite trigger: ≥4 of 5 signals cross thresholds (≥3 has false
    # positives on partially-noisy-but-valid files like J6DSFFBH).
    TRIGGER_MIN = 4
    triggers = 0
    trigger_details: list[str] = []

    if fallback_ratio > _FALLBACK_THRESHOLD:
        triggers += 1
        trigger_details.append(
            f"fallback_best_ratio={fallback_ratio:.2f} > {_FALLBACK_THRESHOLD}"
        )
    if year_ratio < _YEAR_THRESHOLD:
        triggers += 1
        trigger_details.append(
            f"year_ratio={year_ratio:.2f} < {_YEAR_THRESHOLD}"
        )
    if warning_density > _WARNING_DENSITY_THRESHOLD:
        triggers += 1
        trigger_details.append(
            f"warning_density={warning_density:.2f} > {_WARNING_DENSITY_THRESHOLD}"
        )
    if has_numbering_anomaly:
        triggers += 1
        trigger_details.append("numbering_anomaly=True")
    if empty_title_ratio > _EMPTY_TITLE_THRESHOLD:
        triggers += 1
        trigger_details.append(
            f"empty_title_ratio={empty_title_ratio:.2f} > {_EMPTY_TITLE_THRESHOLD}"
        )

    quality_warnings: list[str] = []
    if triggers >= TRIGGER_MIN:
        quality_warnings.append(
            f"file_quality_low: {triggers}/5 signals crossed thresholds "
            f"({' | '.join(trigger_details)})"
        )

    return quality_warnings, signals


# ---------------------------------------------------------------------------
# v1.6 helpers reused for non-CJK entries
# ---------------------------------------------------------------------------


def _dominant_style(entries: list[dict[str, Any]]) -> str:
    total = len(entries) or 1
    numeric_count = sum(
        1 for e in entries
        if dict(e.get("metadata", {})).get("detected_ref_number") is not None
    )
    author_year_count = sum(
        1 for e in entries
        if REFERENCE_TAIL_AT_END_RE.search(str(e.get("raw", "")).strip())
        and COMMA_STYLE_AUTHOR_RE.search(str(e.get("raw", "")))
    )
    num_ratio = numeric_count / total
    ay_ratio = author_year_count / total
    if num_ratio >= 0.8:
        return "numeric"
    if ay_ratio >= 0.8 and num_ratio < 0.3:
        return "author-year"
    if numeric_count and author_year_count:
        return "mixed"
    return "numeric" if numeric_count else ("author-year" if author_year_count else "mixed")


def _validate_years(entry: dict[str, Any], candidates: list[dict[str, Any]]) -> None:
    for candidate in candidates:
        yc = candidate.get("year_candidate")
        if yc is not None and not _is_valid_publication_year(yc):
            candidate["year_candidate"] = None


def _generate_candidates_v16(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Replicate v1.6 candidate generation for non-CJK entries."""
    raw = str(entry.get("raw", ""))
    clean_raw = _strip_trailing_page_markers(raw)
    protected_raw = _protect_author_initials(clean_raw)

    entry_copy = dict(entry)
    entry_copy["raw"] = protected_raw
    candidates = _generate_reference_candidates(entry_copy)

    for c in candidates:
        for key in ("author_text", "title_candidate", "container_candidate"):
            val = c.get(key, "")
            if isinstance(val, str):
                c[key] = _restore_initials(val)
    return candidates


# ---------------------------------------------------------------------------
# Plugin
# ---------------------------------------------------------------------------


@register
class LineFirstV171Preprocessor(ReferencePreprocessor):
    """v1.7.1: v1.7 + file-level quality detection for negative-case awareness."""

    name = "line-first-v171"

    def process(self, raw_text: str) -> dict[str, Any]:
        lines = raw_text.split("\n")

        # Filter non-reference lines (same as v1.6/v1.7)
        clean_lines: list[str] = []
        for l in lines:
            stripped = l.strip()
            if stripped and NON_REFERENCE_LINE_RE.match(stripped):
                continue
            clean_lines.append(_strip_trailing_page_markers(l))

        scope = Scope(
            section_title="References", line_start=1, line_end=len(lines), metadata={},
        )
        v1_result = prepare_reference_workset(clean_lines, scope)

        blocks = v1_result["blocks"]
        entries = v1_result["entries"]
        numbering_warnings = v1_result["numbering_warnings"]
        has_numbering_anomaly = v1_result["has_numbering_anomaly"]

        # Merge over-split bilingual entries (same as v1.7)
        entries = _merge_bilingual_entries(entries)

        candidates: list[dict[str, Any]] = []
        ambiguity_warnings: list[str] = []
        boundary_warnings: list[str] = []

        for entry in entries:
            if _is_cjk_entry(str(entry.get("raw", ""))):
                entry_candidates = _generate_candidates_cjk(entry)
            else:
                entry_candidates = _generate_candidates_v16(entry)

            _validate_years(entry, entry_candidates)

            if len(entry_candidates) > 1:
                ambiguity_warnings.append(
                    f"reference_pattern_ambiguous: entry_index={entry['entry_index']}"
                )
            for candidate in entry_candidates:
                title_candidate = str(candidate.get("title_candidate", "")).strip()
                if not title_candidate or LEADING_PUNCTUATION_RE.match(title_candidate):
                    boundary_warnings.append(
                        f"reference_title_boundary_suspect: "
                        f"entry_index={entry['entry_index']} pattern={candidate['pattern']}"
                    )
                candidates.append(candidate)

        entry_style = _dominant_style(entries)
        suspect_blocks = _detect_reference_block_suspicions(
            blocks=blocks, entries=entries, candidates=candidates,
            entry_style=entry_style,
        )
        grouping_warnings = [
            f"reference_entry_grouping_suspect: block_index={block['block_index']}"
            for block in suspect_blocks
        ]
        warnings = list(dict.fromkeys(
            [*numbering_warnings, *ambiguity_warnings, *boundary_warnings,
             *grouping_warnings]
        ))

        # === File-level quality detection (v1.7.1 addition) ===
        quality_warnings, quality_signals = _detect_file_quality(
            entries=entries,
            candidates=candidates,
            has_numbering_anomaly=has_numbering_anomaly,
            warnings=warnings,
        )
        warnings.extend(quality_warnings)

        batches = _build_reference_batches(entries)
        prepared = {
            "blocks": blocks, "entries": entries, "candidates": candidates,
            "batches": batches, "entry_style": entry_style,
            "suspect_blocks": suspect_blocks,
            "requires_split_review": bool(suspect_blocks),
            "numbering_warnings": numbering_warnings,
            "has_numbering_anomaly": has_numbering_anomaly,
            "warnings": warnings,
        }
        result = build_workset_export(prepared)
        # v1.7.1: add file-level quality signals after the standard export
        result["file_quality"] = quality_signals
        result["file_quality_low"] = bool(quality_warnings)
        return result
