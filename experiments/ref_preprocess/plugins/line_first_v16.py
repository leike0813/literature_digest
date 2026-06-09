"""v1.6 preprocessing algorithm plugin.

Improvements over v1.5:
1. Merged _protect_author_initials from v1.2 — protects abbreviated names
   before candidate generation (fixes M3AU5AC9, 34WIW5FH)
2. Fixed _candidate_ieee_quote_title regex — comma before closing quote
   (fixes UW8ZLVA6, M3AU5AC9)
3. Non-reference content filtering — filters image/table/figure headings
   at the line level (reduces oversplit in 8WM66ZL3, LUM266YT, etc.)
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
    _detect_reference_numbering,
    _generate_reference_candidates,
    _is_valid_publication_year,
    _protect_author_initials,
    _restore_initials,
    _strip_trailing_page_markers,
    build_workset_export,
    prepare_reference_workset,
)


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
    """Generate candidates with author initial protection.

    1. Strip trailing page markers
    2. Protect abbreviated initials (``P. Frasconi`` → ``P\\x00Frasconi``)
    3. Run standard candidate generation
    4. Restore initials in results
    """
    raw = str(entry.get("raw", ""))
    clean_raw = _strip_trailing_page_markers(raw)
    protected_raw = _protect_author_initials(clean_raw)

    entry_copy = dict(entry)
    entry_copy["raw"] = protected_raw
    candidates = _generate_reference_candidates(entry_copy)

    if not candidates:
        return candidates

    # Restore initials in all candidate fields
    for c in candidates:
        for key in ("author_text", "title_candidate", "container_candidate"):
            val = c.get(key, "")
            if isinstance(val, str):
                c[key] = _restore_initials(val)

    return candidates


@register
class LineFirstV16Preprocessor(ReferencePreprocessor):
    """v1.6: v1.5 + initial protection + non-ref filtering + IEEE fix."""

    name = "line-first-v16"

    def process(self, raw_text: str) -> dict[str, Any]:
        lines = raw_text.split("\n")

        # Filter non-reference lines (image/table/figure markers) + strip page markers
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

        candidates: list[dict[str, Any]] = []
        ambiguity_warnings: list[str] = []
        boundary_warnings: list[str] = []
        normalized_entries = list(entries)

        for entry in normalized_entries:
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

        entry_style = _dominant_style(normalized_entries)
        suspect_blocks = _detect_reference_block_suspicions(
            blocks=blocks, entries=normalized_entries, candidates=candidates, entry_style=entry_style,
        )
        grouping_warnings = [
            f"reference_entry_grouping_suspect: block_index={block['block_index']}"
            for block in suspect_blocks
        ]
        batches = _build_reference_batches(normalized_entries)
        warnings = list(dict.fromkeys(
            [*numbering_warnings, *ambiguity_warnings, *boundary_warnings, *grouping_warnings]
        ))

        prepared = {
            "blocks": blocks, "entries": normalized_entries, "candidates": candidates,
            "batches": batches, "entry_style": entry_style,
            "suspect_blocks": suspect_blocks, "requires_split_review": bool(suspect_blocks),
            "numbering_warnings": numbering_warnings, "has_numbering_anomaly": has_numbering_anomaly,
            "warnings": warnings,
        }
        return build_workset_export(prepared)
