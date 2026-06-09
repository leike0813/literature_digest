"""v1.4 preprocessing algorithm — venue-first title extraction.

Core change: instead of guessing author-title-venue boundaries with regex,
first find the venue marker (``in``, ``In:``, ``CVPR``, ``Proceedings``, etc.),
split off the container text, then parse only the author+title block.

This separates the hard problem (author-title boundary) from the easier one
(venue detection), dramatically reducing the ambiguity space.
"""

from __future__ import annotations

import re
from typing import Any

from experiments.ref_preprocess.plugin_base import ReferencePreprocessor, register
from experiments.ref_preprocess.preprocessing import (
    COMMA_STYLE_AUTHOR_RE,
    KNOWN_VENUE_ABBREV,
    REFERENCE_ENTRY_START_RE,
    SURNAME_RE,
    TERMINAL_PUBLICATION_YEAR_RE,
    VENUE_MARKERS,
    YEAR_RE,
    Scope,
    _build_reference_batches,
    _detect_reference_block_suspicions,
    _detect_reference_entry_style,
    _detect_reference_numbering,
    _extract_terminal_publication_year,
    _generate_reference_candidates,
    _is_valid_publication_year,
    _make_reference_candidate,
    _normalize_reference_entry_text,
    _protect_author_initials,
    _restore_initials,
    _split_at_venue,
    _split_reference_blocks,
    _split_reference_entries,
    _strip_reference_number_prefix,
    _strip_trailing_page_markers,
    build_workset_export,
    prepare_reference_workset,
    utc_now_iso,
)
from experiments.ref_preprocess.patterns import (
    LEADING_PUNCTUATION_RE,
    REFERENCE_TAIL_AT_END_RE,
    WARNING_REFERENCE_ENTRY_GROUPING_SUSPECT,
    WARNING_REFERENCE_PATTERN_AMBIGUOUS,
    WARNING_REFERENCE_TITLE_BOUNDARY_SUSPECT,
)


# ---------------------------------------------------------------------------
# Dominant-signal style detection (from v1.2)
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


# ---------------------------------------------------------------------------
# Title sanity guard
# ---------------------------------------------------------------------------


def _has_plausible_title(title: str) -> bool:
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
# v1.4: venue-first candidate generation
# ---------------------------------------------------------------------------


def _candidate_ieee_quote(author_title: str, container: str,
                          entry_index: int, terminal_year: int | None,
                          ) -> dict[str, Any] | None:
    # Extract from ``authors, "Title," container`` pattern.
    m = re.match(
        r'^(?P<authors>.+?),[\s ]*["](?P<title>.+?)["],?\s*$',
        author_title,
    )
    if m is None:
        return None
    year = terminal_year
    return _make_reference_candidate(
        entry_index=entry_index, pattern="v14_ieee_quote",
        author_text=m.group("authors"),
        title_candidate=m.group("title"),
        container_candidate=container,
        year_candidate=year,
        confidence=0.95,
        split_basis="IEEE quote: authors, 'Title',",
    )


def _candidate_colon_bibtex(author_title: str, container: str,
                            entry_index: int, terminal_year: int | None,
                            ) -> dict[str, Any] | None:
    """Extract from ``authors: Title`` (colon after real author list)."""
    m = re.match(
        r'^(?P<authors>.+?):\s*(?P<title>.+?)$',
        author_title,
    )
    if m is None:
        return None
    author_text = m.group("authors").strip()
    # Only high confidence if the author block contains comma-style authors
    has_authors = bool(re.search(r',', author_text)) and len(author_text.split()) >= 3
    confidence = 0.92 if has_authors else 0.40
    title_candidate = m.group("title").strip()
    # Strip trailing period
    title_candidate = re.sub(r'\.\s*$', '', title_candidate)
    return _make_reference_candidate(
        entry_index=entry_index, pattern="v14_colon_bibtex",
        author_text=author_text,
        title_candidate=title_candidate,
        container_candidate=container,
        year_candidate=terminal_year,
        confidence=confidence,
        split_basis="colon after comma-style authors",
    )


def _candidate_sentence_boundary(author_title: str, container: str,
                                 entry_index: int, terminal_year: int | None,
                                 ) -> dict[str, Any] | None:
    """Extract from ``I. Surname. Title`` — protected period after author block.

    Uses ``_protect_author_initials`` to prevent splitting on abbreviation periods,
    then finds the first unprotected period as the author-title boundary.
    """
    protected = _protect_author_initials(author_title)
    # Find first unprotected `. ` sequence
    m = re.match(
        r'^(?P<authors>.+?)\.\s+(?P<title>.+?)$',
        protected,
    )
    if m is None:
        return None
    author_text = _restore_initials(m.group("authors").strip())
    title_candidate = _restore_initials(m.group("title").strip())
    title_candidate = re.sub(r'\.\s*$', '', title_candidate)
    return _make_reference_candidate(
        entry_index=entry_index, pattern="v14_sentence",
        author_text=author_text,
        title_candidate=title_candidate,
        container_candidate=container,
        year_candidate=terminal_year,
        confidence=0.88,
        split_basis="sentence boundary with initial protection",
    )


def _candidate_author_paren_year(author_title: str, container: str,
                                  entry_index: int, terminal_year: int | None,
                                  ) -> dict[str, Any] | None:
    """Extract from ``Author (Year). Title`` APA-style."""
    m = re.match(
        r'^(?P<authors>.+?)\s*\((?P<year>(?:19|20)\d{2})[a-z]?\)\.?\s+(?P<title>.+?)$',
        author_title,
    )
    if m is None:
        return None
    title_candidate = re.sub(r'\.\s*$', '', m.group("title").strip())
    year = int(m.group("year")) if _is_valid_publication_year(int(m.group("year"))) else terminal_year
    return _make_reference_candidate(
        entry_index=entry_index, pattern="v14_apa_paren_year",
        author_text=m.group("authors").strip(),
        title_candidate=title_candidate,
        container_candidate=container,
        year_candidate=year,
        confidence=0.90,
        split_basis="APA: Author (Year). Title",
    )


def _generate_candidates_v14(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Venue-first candidate generation.

    1. Strip trailing page markers
    2. Split into (author+title, container) using _split_at_venue
    3. Try format-family specific extraction on the author+title block
    4. Fall back to v1.2 initial-protection pattern
    """
    raw = str(entry.get("raw", ""))
    clean_raw = _strip_trailing_page_markers(raw)
    entry_index = int(entry["entry_index"])
    terminal_year = _extract_terminal_publication_year(clean_raw)

    # Step 1: Strip number prefix
    text, detected_num = _strip_reference_number_prefix(clean_raw)
    text = _normalize_reference_entry_text(text)

    # Step 2: Split at venue marker
    author_title, venue_text = _split_at_venue(text)

    # If split failed, use the whole text as author+title
    if not venue_text:
        author_title = text
        venue_text = ""

    # Step 3: Try format-family specific extractors
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, int | None]] = set()

    builders = [
        _candidate_ieee_quote,
        _candidate_author_paren_year,
        _candidate_colon_bibtex,
        _candidate_sentence_boundary,
    ]

    for builder in builders:
        cand = builder(author_title, venue_text, entry_index, terminal_year)
        if cand is None:
            continue
        key = (cand["pattern"], cand["author_text"], cand["title_candidate"], cand.get("year_candidate"))
        if key in seen:
            continue
        seen.add(key)
        cand["candidate_index"] = len(candidates)
        candidates.append(cand)

    # Step 4: Fallback — try v1.2's full pipeline
    if not candidates:
        fallback = _generate_reference_candidates(entry)
        alist = [c for c in fallback if _has_plausible_title(str(c.get("title_candidate", "")))]
        return alist or fallback

    # Filter plausible titles
    plausible = [c for c in candidates if _has_plausible_title(str(c.get("title_candidate", "")))]
    if plausible:
        plausible.sort(key=lambda c: c.get("confidence", 0), reverse=True)
        return plausible
    return candidates


# ---------------------------------------------------------------------------
# Plugin
# ---------------------------------------------------------------------------


@register
class LineFirstV14Preprocessor(ReferencePreprocessor):
    """v1.4: venue-first title extraction — split venue first, then parse author-title."""

    name = "line-first-v14"

    def process(self, raw_text: str) -> dict[str, Any]:
        lines = raw_text.split("\n")
        clean_lines = [_strip_trailing_page_markers(l) for l in lines]
        scope = Scope(section_title="References", line_start=1, line_end=len(clean_lines), metadata={})

        blocks = _split_reference_blocks(clean_lines, scope)
        entries = _split_reference_entries(clean_lines, scope)
        normalized_entries, numbering_warnings, has_numbering_anomaly = _detect_reference_numbering(entries)

        # Generate candidates using v1.4 venue-first approach
        candidates: list[dict[str, Any]] = []
        ambiguity_warnings: list[str] = []
        boundary_warnings: list[str] = []

        for entry in normalized_entries:
            entry_candidates = _generate_candidates_v14(entry)
            if len(entry_candidates) > 1:
                ambiguity_warnings.append(
                    f"{WARNING_REFERENCE_PATTERN_AMBIGUOUS}: entry_index={entry['entry_index']}"
                )
            for cand in entry_candidates:
                title_candidate = str(cand.get("title_candidate", "")).strip()
                if not title_candidate or LEADING_PUNCTUATION_RE.match(title_candidate):
                    boundary_warnings.append(
                        f"{WARNING_REFERENCE_TITLE_BOUNDARY_SUSPECT}: "
                        f"entry_index={entry['entry_index']} pattern={cand['pattern']}"
                    )
                candidates.append(cand)

        entry_style = _dominant_style(normalized_entries)

        suspect_blocks = _detect_reference_block_suspicions(
            blocks=blocks, entries=normalized_entries, candidates=candidates, entry_style=entry_style,
        )
        grouping_warnings = [
            f"{WARNING_REFERENCE_ENTRY_GROUPING_SUSPECT}: block_index={block['block_index']}"
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
