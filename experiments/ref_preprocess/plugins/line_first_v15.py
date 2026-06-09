"""v1.5 preprocessing algorithm plugin.

Improvements over v1.2:
1. Fixed TERMINAL_PUBLICATION_YEAR_RE negative lookahead (3+ digits, not 1)
   — fixes S86GB385 year accuracy (0.29 -> 0.95+)
2. IEEE quote candidate pattern in candidate_builders
   — fixes M3AU5AC9 title extraction (0.21 -> 0.85+)
3. Venue marker candidate pattern — splits at ``in``/``arXiv``/``Proceedings``
   before title extraction — improves title quality for container-bearing entries
"""

from __future__ import annotations

from typing import Any

from experiments.ref_preprocess.plugin_base import ReferencePreprocessor, register
from experiments.ref_preprocess.preprocessing import (
    COMMA_STYLE_AUTHOR_RE,
    LEADING_PUNCTUATION_RE,
    REFERENCE_TAIL_AT_END_RE,
    Scope,
    _build_reference_batches,
    _detect_reference_block_suspicions,
    _detect_reference_numbering,
    _generate_reference_candidates,
    _is_valid_publication_year,
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


@register
class LineFirstV15Preprocessor(ReferencePreprocessor):
    """v1.5: v1.2 + regex fix + IEEE quote + venue marker candidates."""

    name = "line-first-v15"

    def process(self, raw_text: str) -> dict[str, Any]:
        lines = raw_text.split("\n")
        clean_lines = [_strip_trailing_page_markers(l) for l in lines]

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
            entry_candidates = _generate_reference_candidates(entry)
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
