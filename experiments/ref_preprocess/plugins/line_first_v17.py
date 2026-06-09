"""v1.7 preprocessing algorithm plugin — CJK reference format support.

Strategy: route CJK entries through a separate branch that:
  1. Normalizes full-width punctuation → half-width so existing English
     regex patterns (REFERENCE_ENTRY_START_RE, COMMA_STYLE_AUTHOR_RE,
     YEAR_RE, etc.) can match entries with CJK punctuation.
  2. Merges bilingual entries (Chinese + English transliteration on same
     line) that get over-split by the generic sentence-boundary detector.
  3. Tries a CJK-specific candidate pattern for entries with Chinese
     author names, then falls back to the v1.6 pipeline on normalized text.

Non-CJK entries are handled identically to v1.6.
"""

from __future__ import annotations

import re
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
    _make_reference_candidate,
    _normalize_reference_entry_text,
    _protect_author_initials,
    _restore_initials,
    _split_author_candidates,
    _strip_reference_number_prefix,
    _strip_trailing_page_markers,
    build_workset_export,
    prepare_reference_workset,
)

# ---------------------------------------------------------------------------
# CJK detection and full-width normalization
# ---------------------------------------------------------------------------

# Range capturing CJK Unified Ideographs, Extension A, and Compatibility
CJK_RE = re.compile(r"[一-鿿㐀-䶿豈-﫿]")

# Full-width → half-width punctuation mapping
_FULLWIDTH_TO_HALFWIDTH = str.maketrans({
    "［": "[",   # ［
    "］": "]",   # ］
    "，": ",",   # ，
    "．": ".",   # ．
    "：": ":",   # ：
    "（": "(",   # （
    "）": ")",   # ）
    "；": ";",   # ；
    "／": "/",   # ／
    "－": "-",   # －
    "‘": "'",   # '
    "’": "'",   # '
    "“": '"',   # "
    "”": '"',   # "
    "∥": "/",   # ∥ → /
})


def _has_cjk(text: str, threshold: float = 0.1) -> bool:
    """Return True if at least *threshold* fraction of chars are CJK."""
    if not text:
        return False
    cjk_count = sum(1 for c in text if CJK_RE.match(c))
    return cjk_count / max(len(text), 1) >= threshold


def _is_cjk_entry(raw: str) -> bool:
    """Check whether an entry needs CJK-aware processing.

    Returns True if the entry contains CJK ideographs OR full-width
    punctuation (brackets, commas, periods).  The latter catches
    entries like S7IWH3CG's English-author entries that use full-width
    ``［］`` and ``，`` but have no CJK ideographs.
    """
    text = re.sub(r"^[\[（［]?\s*\d{1,3}\s*[\]）］]?\s*", "", raw.strip(), count=1)
    if _has_cjk(text, threshold=0.1):
        return True
    # Also check for full-width punctuation alone (no CJK chars needed)
    return bool(re.search(r"[［］，．：（）]", raw))


def _normalize_fullwidth(text: str) -> str:
    """Convert full-width punctuation to half-width equivalents.

    Also collapses stray whitespace inside bracket pairs such as ``[1 ]``
    that appear in some CJK-formatted reference lists.
    """
    result = text.translate(_FULLWIDTH_TO_HALFWIDTH)
    # Normalize "[1 ]" → "[1]" (space before closing bracket)
    result = re.sub(r"\[(\d{1,3})\s+\]", r"[\1]", result)
    return result


# ---------------------------------------------------------------------------
# Bilingual entry merging
# ---------------------------------------------------------------------------

# Regex for English-author-like start: e.g. "REN H，", "WANG G M,", "ZHOU F Y."
_EN_START_RE = re.compile(r"^[A-Z][A-Za-z]{1,20}\s+[A-Z][,\.\s]")

# Regex for a trailing period/paren preceded by a digit (page number, year, etc.)
# Allows bilingual detection even when the CJK entry ends with numeric content.
_TRAILING_CLOSE_RE = re.compile(r"[\)\]\)\]]?\s*[\.。．]\s*$")


def _merge_bilingual_entries(
    entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge over-split bilingual entries back into single entries.

    Many Chinese papers include both the original Chinese reference and
    an English transliteration on the same line.  The generic sentence-
    boundary detector (``_split_inline_reference_chunk``) splits these
    into two fragments.  This function detects the pattern and merges
    the English tail back into the Chinese head.
    """
    if not entries:
        return entries

    merged: list[dict[str, Any]] = []
    skip: set[int] = set()

    for i in range(len(entries)):
        if i in skip:
            continue
        raw_i = str(entries[i].get("raw", ""))
        if i + 1 < len(entries):
            raw_next = str(entries[i + 1].get("raw", ""))
            # Merge when: current has CJK, next is Latin-only,
            # next starts like an English author block, and current
            # ends naturally (digit/period/paren).
            if (
                _has_cjk(raw_i)
                and not _has_cjk(raw_next)
                and _EN_START_RE.match(raw_next)
                and _TRAILING_CLOSE_RE.search(raw_i)
            ):
                skip.add(i + 1)
        merged.append(entries[i])
    return merged


# ---------------------------------------------------------------------------
# Type-marker-driven candidate pattern (handles both CJK and Latin authors)
# ---------------------------------------------------------------------------

# Type marker [J] [C] [D] [M] [N] [S] [P] [EB/OL] as the primary structural
# delimiter.  Matches:
#
#   CJK:   吴继敏. 薄片显微描绘…[J]. 矿物岩石, 1999
#   Latin: LECUN Y, BOTTOU L.Gradient-based…[J].Proceedings of the IEEE,1998
#
# Groups:
#   authors_and_title  — everything before the type marker
#   container          — journal / venue / publisher (before first comma)
#   year               — 4-digit publication year
_TYPE_MARKER_ENTRY_RE = re.compile(
    r"^(?P<authors_and_title>.+?)\s*"
    r"[［\[](?:J|C|D|M|N|S|P|EB/OL)[］\]]\s*"
    r"[。．\.]\s*"
    r"(?P<container>[^，,]*?)\s*"
    r"[，,]\s*"
    r"\(?(?P<year>(?:19|20)\d{2})"
)


def _split_authors_title(text: str) -> tuple[str, str]:
    """Split ``author_block.title_text`` at the LAST period.

    The type-marker pattern captures everything before ``[J]`` as one
    blob.  Since the standard format is ``Author. Title``, splitting at
    the last period recovers the author-title boundary even when there
    is no space after the period (a common OCR artifact).
    """
    idx = text.rfind(".")
    if idx > 0:
        return text[:idx].strip(), text[idx + 1:].strip()
    if ":" in text:
        parts = text.split(":", 1)
        return parts[0].strip(), parts[1].strip()
    return text, ""


def _generate_candidates_cjk(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate candidates for a CJK entry.

    1. Normalize full-width punctuation (so that ``［J］`` → ``[J]``, etc.).
    2. Try the type-marker-driven pattern (``Author…[J].Container, Year``).
       This handles both CJK and Latin author names as long as a type
       marker is present.
    3. Fall back to the v1.6 pipeline on the normalized text.
    """
    raw = str(entry.get("raw", ""))
    entry_index = int(entry.get("entry_index", 0))

    normalized = _normalize_fullwidth(raw)
    text, ref_num = _strip_reference_number_prefix(normalized)
    text = _normalize_reference_entry_text(text)

    # Attempt type-marker-driven pattern
    match = _TYPE_MARKER_ENTRY_RE.match(text)
    if match:
        authors_and_title = match.group("authors_and_title").strip()
        author_text, title = _split_authors_title(authors_and_title)
        year_str = match.group("year")
        year = int(year_str) if year_str else None

        candidate = _make_reference_candidate(
            entry_index=entry_index,
            pattern="cjk_type_marker_entry",
            author_text=author_text,
            title_candidate=title,
            container_candidate=match.group("container").strip(),
            year_candidate=year,
            confidence=0.75,
            split_basis="type-marker [J/C/D/...] delimits title and container",
        )
        # Override author_candidates: CJK names need custom splitting
        if _has_cjk(author_text):
            candidate["author_candidates"] = [
                a.strip().rstrip("，,、")
                for a in re.split(r"[，,、]\s*", author_text)
                if a.strip()
            ]
        candidate["candidate_index"] = 0
        return [candidate]

    # Fallback: v1.6 pipeline on full-width-normalized text
    entry_copy = dict(entry)
    entry_copy["raw"] = normalized
    return _generate_candidates_v16(entry_copy)


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
class LineFirstV17Preprocessor(ReferencePreprocessor):
    """v1.7: v1.6 + CJK reference format support as a separate branch."""

    name = "line-first-v17"

    def process(self, raw_text: str) -> dict[str, Any]:
        lines = raw_text.split("\n")

        # Filter non-reference lines (same as v1.6)
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

        # Merge over-split bilingual entries
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
        batches = _build_reference_batches(entries)
        warnings = list(dict.fromkeys(
            [*numbering_warnings, *ambiguity_warnings, *boundary_warnings,
             *grouping_warnings]
        ))

        prepared = {
            "blocks": blocks, "entries": entries, "candidates": candidates,
            "batches": batches, "entry_style": entry_style,
            "suspect_blocks": suspect_blocks,
            "requires_split_review": bool(suspect_blocks),
            "numbering_warnings": numbering_warnings,
            "has_numbering_anomaly": has_numbering_anomaly,
            "warnings": warnings,
        }
        return build_workset_export(prepared)
