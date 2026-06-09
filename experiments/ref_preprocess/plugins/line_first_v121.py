"""v1.2.1 preprocessing algorithm plugin.

Same as v1.2 but removes the colon-based candidate pattern entirely.

The ``authors_colon_title_in_year`` pattern assumes the colon is an
author-title delimiter — but in published-paper reference lists (as opposed
to BibTeX source), the colon nearly always belongs to the title
(e.g. ``DINO: DETR with...``, ``BEiT: BERT pre-training...``).
Removing it eliminates a systematic source of title corruption.
"""

from __future__ import annotations

from typing import Any

from experiments.ref_preprocess.plugin_base import ReferencePreprocessor, register
from experiments.ref_preprocess.preprocessing import (
    LATEX_BIBITEM_RE,
    Scope,
    _build_reference_batches,
    _build_reference_entries_from_blocks,
    _candidate_authors_period_title_period_venue_year,
    _candidate_authors_year_paren_title_venue,
    _candidate_bibtex_entry_fields,
    _candidate_fallback_raw_split,
    _candidate_ieee_quote_title,
    _candidate_thesis_or_book_tail_year,
    _detect_reference_block_suspicions,
    _detect_reference_numbering,
    _extract_bibitem_key,
    _extract_terminal_publication_year,
    _is_valid_publication_year,
    _normalize_reference_entry_text,
    _protect_author_initials,
    _restore_initials,
    _split_reference_blocks,
    _strip_reference_number_prefix,
    _strip_trailing_page_markers,
    build_workset_export,
    prepare_reference_workset,
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
# Candidate generation — v1.2.1: colon pattern removed
# ---------------------------------------------------------------------------


def _generate_reference_candidates_v121(
    entry: dict[str, Any],
) -> list[dict[str, Any]]:
    """Same as preprocessing._generate_reference_candidates but WITHOUT
    ``_candidate_authors_colon_title_in_year`` (colon is not an author-title
    delimiter in published reference lists)."""
    raw = str(entry.get("raw", ""))
    metadata = dict(entry.get("metadata", {}))
    source_format = str(metadata.get("source_format", ""))
    text, _ = _strip_reference_number_prefix(raw)
    bibitem_key = _extract_bibitem_key(text)
    if bibitem_key is not None:
        text = LATEX_BIBITEM_RE.sub("", text, count=1).strip()
    text = _normalize_reference_entry_text(text)
    entry_index = int(entry["entry_index"])
    terminal_year = _extract_terminal_publication_year(raw)

    if source_format == "bibtex":
        candidate = _candidate_bibtex_entry_fields(entry_index, raw)
        if candidate is not None:
            candidate["candidate_index"] = 0
            return [candidate]

    # NOTE: _candidate_authors_colon_title_in_year deliberately excluded
    candidate_builders = [
        _candidate_ieee_quote_title,
        _candidate_authors_period_title_period_venue_year,
        _candidate_authors_year_paren_title_venue,
        _candidate_thesis_or_book_tail_year,
    ]
    seen: set[tuple[str, str, str, int | None]] = set()
    candidates: list[dict[str, Any]] = []
    for builder in candidate_builders:
        candidate = builder(entry_index, text, terminal_year)
        if candidate is None:
            continue
        key = (
            str(candidate["pattern"]),
            str(candidate["author_text"]),
            str(candidate["title_candidate"]),
            candidate.get("year_candidate"),
        )
        if key in seen:
            continue
        seen.add(key)
        if bibitem_key is not None:
            candidate.setdefault("metadata", {})["bibitem_key"] = bibitem_key
        candidate["candidate_index"] = len(candidates)
        candidates.append(candidate)

    fallback = _candidate_fallback_raw_split(entry_index, text, terminal_year)
    fallback_key = (
        str(fallback["pattern"]),
        str(fallback["author_text"]),
        str(fallback["title_candidate"]),
        fallback.get("year_candidate"),
    )
    if fallback_key not in seen:
        if bibitem_key is not None:
            fallback.setdefault("metadata", {})["bibitem_key"] = bibitem_key
        fallback["candidate_index"] = len(candidates)
        candidates.append(fallback)
    return candidates


def _generate_candidates_v12(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate candidates with author initial protection (no colon pattern)."""
    raw = str(entry.get("raw", ""))
    clean_raw = _strip_trailing_page_markers(raw)
    protected_raw = _protect_author_initials(clean_raw)

    entry_copy = dict(entry)
    entry_copy["raw"] = protected_raw
    candidates = _generate_reference_candidates_v121(entry_copy)

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
class LineFirstV121Preprocessor(ReferencePreprocessor):
    """v1.2: line-split + regex with initial protection + dominant style detection."""

    name = "line-first-v1.2.1"

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
