"""v1.3 preprocessing algorithm plugin.

Structural improvements over v1.2:
1. **Reference section boundary detection** — skip content before "References"
   heading and after the next same-level heading (appendix).
2. **Non-reference line filtering** — skip image links, table markup, figure captions.
3. **Fragment merging** — reattach continuation lines split by PDF extraction.
4. **IEEE quote candidate** — extract title from ``"Title"`` delimiters.
5. **Removed colon candidate** — colon is not an author-title delimiter
   in any standard citation style.
"""

from __future__ import annotations

from typing import Any

from experiments.ref_preprocess.plugin_base import ReferencePreprocessor, register
from experiments.ref_preprocess.preprocessing import (
    HEADING_RE,
    NON_REFERENCE_LINE_RE,
    Scope,
    _build_reference_batches,
    _build_reference_entries_from_blocks,
    _detect_reference_block_suspicions,
    _detect_reference_numbering,
    _generate_reference_candidates,
    _is_valid_publication_year,
    _merge_fragments,
    _split_reference_blocks,
    _strip_trailing_page_markers,
    build_workset_export,
    prepare_reference_workset,
)
from experiments.ref_preprocess.patterns import (
    COMMA_STYLE_AUTHOR_RE,
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
# Candidate generation with initial protection (v1.2)
# ---------------------------------------------------------------------------


def _generate_candidates_v12(entry: dict[str, Any]) -> list[dict[str, Any]]:
    from experiments.ref_preprocess.preprocessing import (
        _protect_author_initials,
        _restore_initials,
        _strip_trailing_page_markers,
    )

    raw = str(entry.get("raw", ""))
    clean_raw = _strip_trailing_page_markers(raw)
    protected_raw = _protect_author_initials(clean_raw)

    entry_copy = dict(entry)
    entry_copy["raw"] = protected_raw
    candidates = _generate_reference_candidates(entry_copy)

    if not candidates:
        return candidates

    for c in candidates:
        for key in ("author_text", "title_candidate", "container_candidate"):
            val = c.get(key, "")
            if isinstance(val, str):
                c[key] = val.replace("\x00", ". ")

    plausible = [c for c in candidates if _has_plausible_title(
        str(c.get("title_candidate", ""))
    )]
    if plausible:
        plausible.sort(key=lambda c: c.get("confidence", 0), reverse=True)
        return plausible

    return candidates


def _validate_years(entry: dict[str, Any], candidates: list[dict[str, Any]]) -> None:
    for candidate in candidates:
        yc = candidate.get("year_candidate")
        if yc is not None and not _is_valid_publication_year(yc):
            candidate["year_candidate"] = None


# ---------------------------------------------------------------------------
# v1.3 pipeline helpers
# ---------------------------------------------------------------------------


def _locate_reference_scope(lines: list[str]) -> tuple[int, int]:
    """Find the ``References`` section boundaries.

    Returns ``(start_line_0based, end_line_0based)``.
    ``end`` is ``len(lines)`` if no later heading is found.
    """
    ref_heading_patterns = (
        r"^#\s+References$",
        r"^##\s+References$",
        r"^REFERENCES$",
        r"^#\s+Bibliography",
        r"^\\*Bibliography",
    )
    bare_patterns = (
        "^References$",
        "^REFERENCES$",
        "^Bibliography$",
    )
    start = 0
    end = len(lines)

    # Find start: first line that looks like a references heading
    for i, line in enumerate(lines):
        stripped = line.strip()
        for pat in ref_heading_patterns:
            if __import__("re").search(pat, stripped):
                start = i + 1
                break
        if start > 0:
            break
    # Fallback: search for bare "References" on its own line
    if start == 0:
        for i, line in enumerate(lines):
            stripped = line.strip()
            for pat in bare_patterns:
                if __import__("re").match(pat, stripped):
                    start = i + 1
                    break
            if start > 0:
                break

    # Find end: next heading at same or higher level
    heading_level = None
    for i in range(start, len(lines)):
        stripped = lines[i].strip()
        hm = HEADING_RE.match(stripped)
        if hm is None:
            continue
        level = len(hm.group(1))
        if heading_level is None:
            heading_level = level
        if level <= heading_level and i > start:
            end = i
            break

    return start, end


def _filter_lines(
    lines: list[str], start: int, end: int
) -> list[str]:
    """Return only the reference lines within ``[start, end)``,
    skipping known non-reference patterns."""
    result: list[str] = []
    for line in lines[start:end]:
        stripped = line.strip()
        if not stripped:
            continue
        if NON_REFERENCE_LINE_RE.search(stripped):
            continue
        # Skip image markdown
        if stripped.startswith("!["):
            continue
        # Skip standalone URLs (no author content before)
        if stripped.startswith("http://") or stripped.startswith("https://"):
            continue
        result.append(line)
    return result


# ---------------------------------------------------------------------------
# Plugin
# ---------------------------------------------------------------------------


@register
class LineFirstV13Preprocessor(ReferencePreprocessor):
    """v1.3: scope-aware, fragment-merged, IEEE-quote-aware line-first."""

    name = "line-first-v13"

    def process(self, raw_text: str) -> dict[str, Any]:
        all_lines = raw_text.split("\n")

        # Step 1: Locate the reference section
        ref_start, ref_end = _locate_reference_scope(all_lines)
        # Fallback: if no References heading found, use the full text
        if ref_start == 0:
            ref_end = len(all_lines)

        # Step 2: Strip trailing page markers + filter non-reference lines
        clean_lines = [
            _strip_trailing_page_markers(l)
            for l in all_lines[ref_start:ref_end]
        ]
        filtered_lines = _filter_lines(clean_lines, 0, len(clean_lines))

        if not filtered_lines:
            # Empty after filtering — return minimal empty result
            return build_workset_export(prepare_reference_workset(
                all_lines,
                Scope(section_title="References", line_start=1, line_end=len(all_lines)),
            ))

        # Step 3: Rejoin and run v1 pipeline
        scope = Scope(
            section_title="References",
            line_start=1,
            line_end=len(filtered_lines),
            metadata={},
        )
        v1_result = prepare_reference_workset(filtered_lines, scope)

        blocks = v1_result["blocks"]
        entries = v1_result["entries"]
        numbering_warnings = v1_result["numbering_warnings"]
        has_numbering_anomaly = v1_result["has_numbering_anomaly"]

        # Step 4: Merge fragments
        blocks = _merge_fragments(blocks)
        # Rebuild entries from merged blocks
        entries = _build_reference_entries_from_blocks(blocks)

        # Step 5: Candidates with initial protection + year validation
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

        # Step 6: Dominant-signal style detection
        entry_style = _dominant_style(normalized_entries)

        # Step 7: Suspicion detection
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

        # Step 8: Batches
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
