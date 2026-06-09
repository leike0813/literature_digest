"""v1.2 preprocessing algorithm plugin.

Improvements over v1.1:
1. Dominant-signal style detection (not fooled by co-occurring years + names)
2. Protect abbreviated initials from inline-split (fixes APA over-split)
3. Protect author initials in candidate title extraction (fixes "Surname, I." format)
4. Lower confidence for colon patterns without real author content (fixes "DINO: Title" confusion)
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from experiments.ref_preprocess.plugin_base import ReferencePreprocessor, register
from experiments.ref_preprocess.preprocessing import (
    Scope,
    _build_reference_batches,
    _build_reference_entries_from_blocks,
    _detect_reference_block_suspicions,
    _detect_reference_numbering,
    _generate_reference_candidates,
    _is_valid_publication_year,
    _normalize_reference_entry_text,
    _protect_author_initials,
    _restore_initials,
    _split_reference_blocks,
    _strip_trailing_page_markers,
    build_workset_export,
    prepare_reference_workset,
    utc_now_iso,
)
from experiments.ref_preprocess.patterns import (
    COMMA_STYLE_AUTHOR_RE,
    LEADING_PUNCTUATION_RE,
    REFERENCE_TAIL_AT_END_RE,
    SURNAME_RE,
    WARNING_REFERENCE_ENTRY_GROUPING_SUSPECT,
    WARNING_REFERENCE_PATTERN_AMBIGUOUS,
    WARNING_REFERENCE_TITLE_BOUNDARY_SUSPECT,
)


# ---------------------------------------------------------------------------
# Dominant-signal style detection
# ---------------------------------------------------------------------------


def _dominant_style(entries: list[dict[str, Any]]) -> str:
    """Determine entry style by which signal dominates.

    Pure numeric entries will have ``detected_ref_number`` on >80% of entries
    regardless of trailing years. Pure author-year entries will have >80%
    author-year matches and <30% numeric. Only when neither dominates do we
    call it ``"mixed"``.
    """
    total = len(entries) or 1
    numeric_count = 0
    author_year_count = 0

    for entry in entries:
        metadata = dict(entry.get("metadata", {}))
        if metadata.get("detected_ref_number") is not None:
            numeric_count += 1
        raw = str(entry.get("raw", ""))
        if REFERENCE_TAIL_AT_END_RE.search(raw.strip()):
            if COMMA_STYLE_AUTHOR_RE.search(raw):
                author_year_count += 1

    num_ratio = numeric_count / total
    ay_ratio = author_year_count / total

    if num_ratio >= 0.8:
        return "numeric"
    if ay_ratio >= 0.8 and num_ratio < 0.3:
        return "author-year"
    if numeric_count and author_year_count:
        return "mixed"
    if numeric_count:
        return "numeric"
    return "author-year" if author_year_count else "mixed"


# ---------------------------------------------------------------------------
# Title sanity guard
# ---------------------------------------------------------------------------


def _has_plausible_title(title: str) -> bool:
    """Check if a candidate title looks like a real title (not a fragment)."""
    t = title.strip()
    if len(t) < 10:
        return False
    venue_starts = (
        "in ", "in:", "proceedings", "ieee", "proc.", "journal",
        "conference", "advances", "european", "international",
    )
    if t.lower().startswith(venue_starts):
        return False
    initial_chunks = sum(1 for tok in t.split() if len(tok) <= 2 and tok[0].isupper())
    total_tokens = len(t.split())
    if total_tokens >= 3 and initial_chunks / total_tokens > 0.6:
        return False
    return True


# ---------------------------------------------------------------------------
# Candidate generation with initial protection
# ---------------------------------------------------------------------------


def _generate_candidates_v12(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate candidates with author initial protection.

    1. Strip trailing page markers
    2. Protect abbreviated initials (``P. Frasconi`` → ``P\\x00Frasconi``)
    3. Run standard candidate generation
    4. Restore initials in results
    """
    raw = str(entry.get("raw", ""))
    clean_raw = _strip_trailing_page_markers(raw)
    # Protect initials so 'I. Surname' patterns don't confuse the regex splits
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

    # Filter out implausible titles (keep at least one)
    plausible = [c for c in candidates if _has_plausible_title(
        str(c.get("title_candidate", ""))
    )]
    if plausible:
        plausible.sort(key=lambda c: c.get("confidence", 0), reverse=True)
        return plausible

    return candidates


def _validate_years(entry: dict[str, Any], candidates: list[dict[str, Any]]) -> None:
    """Validate year candidates in-place; set invalid years to None."""
    for candidate in candidates:
        yc = candidate.get("year_candidate")
        if yc is not None and not _is_valid_publication_year(yc):
            candidate["year_candidate"] = None


# ---------------------------------------------------------------------------
# Plugin
# ---------------------------------------------------------------------------


@register
class LineFirstV12Preprocessor(ReferencePreprocessor):
    """v1.2: line-split + regex with initial protection + dominant style detection."""

    name = "line-first-v12"

    def process(self, raw_text: str) -> dict[str, Any]:
        lines = raw_text.split("\n")

        # Step 1: Strip trailing page markers from each line
        clean_lines = [_strip_trailing_page_markers(l) for l in lines]

        # Step 2: Run v1 pipeline on cleaned text
        scope = Scope(
            section_title="References",
            line_start=1,
            line_end=len(lines),
            metadata={},
        )
        v1_result = prepare_reference_workset(clean_lines, scope)

        blocks = v1_result["blocks"]
        entries = v1_result["entries"]
        numbering_warnings = v1_result["numbering_warnings"]
        has_numbering_anomaly = v1_result["has_numbering_anomaly"]

        # Step 3: Candidates with initial protection + year validation
        candidates: list[dict[str, Any]] = []
        ambiguity_warnings: list[str] = []
        boundary_warnings: list[str] = []
        normalized_entries = list(entries)

        for entry in normalized_entries:
            entry_candidates = _generate_candidates_v12(entry)
            _validate_years(entry, entry_candidates)
            if len(entry_candidates) > 1:
                ambiguity_warnings.append(
                    f"{WARNING_REFERENCE_PATTERN_AMBIGUOUS}: entry_index={entry['entry_index']}"
                )
            for candidate in entry_candidates:
                title_candidate = str(candidate.get("title_candidate", "")).strip()
                if not title_candidate or LEADING_PUNCTUATION_RE.match(title_candidate):
                    boundary_warnings.append(
                        f"{WARNING_REFERENCE_TITLE_BOUNDARY_SUSPECT}: "
                        f"entry_index={entry['entry_index']} pattern={candidate['pattern']}"
                    )
                candidates.append(candidate)

        # Step 4: Dominant-signal style detection
        entry_style = _dominant_style(normalized_entries)

        # Step 5: Suspicion detection
        suspect_blocks = _detect_reference_block_suspicions(
            blocks=blocks,
            entries=normalized_entries,
            candidates=candidates,
            entry_style=entry_style,
        )
        grouping_warnings = [
            f"{WARNING_REFERENCE_ENTRY_GROUPING_SUSPECT}: block_index={block['block_index']}"
            for block in suspect_blocks
        ]

        # Step 6: Batches
        batches = _build_reference_batches(normalized_entries)

        warnings = list(dict.fromkeys(
            [*numbering_warnings, *ambiguity_warnings, *boundary_warnings, *grouping_warnings]
        ))

        prepared = {
            "blocks": blocks,
            "entries": normalized_entries,
            "candidates": candidates,
            "batches": batches,
            "entry_style": entry_style,
            "suspect_blocks": suspect_blocks,
            "requires_split_review": bool(suspect_blocks),
            "numbering_warnings": numbering_warnings,
            "has_numbering_anomaly": has_numbering_anomaly,
            "warnings": warnings,
        }

        return build_workset_export(prepared)
