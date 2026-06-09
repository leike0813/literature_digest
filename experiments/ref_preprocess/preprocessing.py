"""Deterministic reference preprocessing pipeline extracted from literature-digest.

This module contains the pure, script-only logic from stage_runtime.py's
`prepare_references_workset` flow. It has NO dependency on SQLite, gate_runtime,
or any other runtime machinery. All LLM-based semantic decisions are excluded.
"""

from __future__ import annotations

import hashlib
import json
import re
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .patterns import (
    BIBTEX_ENTRY_START_RE,
    COMMA_STYLE_AUTHOR_RE,
    HEADING_RE,
    KNOWN_VENUE_ABBREV,
    LATEX_BIBITEM_RE,
    LEADING_PUNCTUATION_RE,
    LIKELY_AUTHOR_PREFIX_SEPARATOR_RE,
    NON_REFERENCE_LINE_RE,
    REFERENCE_ENTRY_START_RE,
    REFERENCE_SENTENCE_BREAK_RE,
    REFERENCE_TAIL_AT_END_RE,
    REFERENCE_TAIL_RE,
    SURNAME_RE,
    TERMINAL_PUBLICATION_YEAR_RE,
    TRAILING_PAGE_MARKER_RE,
    VENUE_MARKERS,
    WARNING_REFERENCE_ENTRY_GROUPING_SUSPECT,
    WARNING_REFERENCE_PATTERN_AMBIGUOUS,
    WARNING_REFERENCE_TITLE_BOUNDARY_SUSPECT,
    YEAR_RE,
    YEAR_WITH_TAIL_RE,
)

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Scope:
    """Reference extraction scope (simplified — no DB backing)."""

    section_title: str
    line_start: int
    line_end: int
    metadata: dict[str, Any]


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------


def _normalize_reference_entry_text(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


# ---------------------------------------------------------------------------
# Scope helpers (simplified for standalone use)
# ---------------------------------------------------------------------------


def _scope_lines_without_heading(
    lines: list[str], scope: Scope
) -> tuple[list[str], int]:
    """Return lines within scope range, stripping the heading line if present."""
    start_index = max(scope.line_start - 1, 0)
    end_index = min(scope.line_end, len(lines))
    scoped_lines = lines[start_index:end_index]

    if scoped_lines:
        first_stripped = scoped_lines[0].strip()
        heading_match = HEADING_RE.match(first_stripped)
        if heading_match is not None:
            first_title = re.sub(r"^#{1,6}\s+", "", first_stripped).strip()
            if first_title.lower() == scope.section_title.strip().lower():
                scoped_lines = scoped_lines[1:]
                start_index += 1

    # Truncate at the next same-or-higher-level heading
    scope_heading_level = 1
    truncated_lines: list[str] = []
    for line in scoped_lines:
        stripped = line.strip()
        hm = HEADING_RE.match(stripped)
        if hm is not None and truncated_lines and len(hm.group(1)) <= scope_heading_level:
            break
        truncated_lines.append(line)
    return truncated_lines, start_index + 1


def _extract_scope_lines(
    lines: list[str], scope: Scope
) -> list[tuple[int, str]]:
    scoped_lines, scoped_line_start = _scope_lines_without_heading(lines, scope)
    return list(enumerate(scoped_lines, start=scoped_line_start))


# ---------------------------------------------------------------------------
# BibTeX / bibitem splitting
# ---------------------------------------------------------------------------


def _split_bibitem_entries(
    lines: list[str], scope: Scope
) -> list[dict[str, Any]] | None:
    scoped_lines = _extract_scope_lines(lines, scope)
    if not any(LATEX_BIBITEM_RE.search(line) for _, line in scoped_lines):
        return None

    blocks: list[dict[str, Any]] = []
    current_lines: list[str] = []
    current_key: str | None = None
    line_start = 0
    block_index = 0

    def flush(line_end: int) -> None:
        nonlocal current_lines, current_key, line_start, block_index
        if not current_lines:
            return
        source_text = _normalize_reference_entry_text(
            " ".join(part.strip() for part in current_lines if part.strip())
        )
        if source_text:
            blocks.append(
                {
                    "block_index": block_index,
                    "source_text": source_text,
                    "line_start": line_start,
                    "line_end": line_end,
                    "proposed_entries": [source_text],
                    "metadata": {
                        "bibitem_key": current_key,
                        "source_format": "latex_bibitem",
                    },
                }
            )
        current_lines = []
        current_key = None
        line_start = 0

    for line_no, line in scoped_lines:
        match = LATEX_BIBITEM_RE.search(line)
        if match is not None:
            flush(line_no - 1)
            line_start = line_no
            current_key = match.group(1).strip()
            current_lines = [line]
        elif current_lines:
            current_lines.append(line)
    flush(scoped_lines[-1][0] if scoped_lines else 0)
    return blocks


def _split_bibtex_entries(
    lines: list[str], scope: Scope
) -> list[dict[str, Any]] | None:
    scoped_lines = _extract_scope_lines(lines, scope)
    has_bibtex_start = any(
        BIBTEX_ENTRY_START_RE.match(line) for _, line in scoped_lines
    )
    has_bibtex_fence = any(
        line.strip() == "```bibtex" for _, line in scoped_lines
    )
    if not has_bibtex_start and not has_bibtex_fence:
        return None

    blocks: list[dict[str, Any]] = []
    in_bibtex_fence = False
    current_lines: list[str] = []
    current_key = ""
    current_type = ""
    line_start = 0
    brace_balance = 0
    block_index = 0

    def flush(line_end: int) -> None:
        nonlocal current_lines, current_key, current_type, line_start, brace_balance, block_index
        if not current_lines:
            return
        raw = "\n".join(current_lines).strip()
        if raw:
            blocks.append(
                {
                    "block_index": block_index,
                    "source_text": raw,
                    "line_start": line_start,
                    "line_end": line_end,
                    "proposed_entries": [raw],
                    "metadata": {
                        "citekey": current_key,
                        "bibtex_entry_type": current_type,
                        "source_format": "bibtex",
                    },
                }
            )
            block_index += 1
        current_lines = []
        current_key = ""
        current_type = ""
        line_start = 0
        brace_balance = 0

    for line_no, line in scoped_lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if stripped == "```bibtex":
                in_bibtex_fence = True
            elif in_bibtex_fence:
                flush(line_no - 1)
                in_bibtex_fence = False
            continue
        if not in_bibtex_fence and not BIBTEX_ENTRY_START_RE.match(stripped):
            continue
        start_match = BIBTEX_ENTRY_START_RE.match(line)
        if start_match is not None:
            flush(line_no - 1)
            line_start = line_no
            current_type = start_match.group(1).strip()
            current_key = start_match.group(2).strip()
            current_lines = [line]
            brace_balance = line.count("{") - line.count("}")
            if brace_balance <= 0:
                flush(line_no)
            continue
        if current_lines:
            current_lines.append(line)
            brace_balance += line.count("{") - line.count("}")
            if brace_balance <= 0:
                flush(line_no)

    flush(scoped_lines[-1][0] if scoped_lines else 0)
    return blocks or None


# ---------------------------------------------------------------------------
# Inline reference splitting
# ---------------------------------------------------------------------------


def _looks_like_author_year_entry_start(text: str) -> bool:
    normalized = _normalize_reference_entry_text(text)
    if not normalized:
        return False
    if REFERENCE_ENTRY_START_RE.match(normalized):
        return True
    year_match = YEAR_WITH_TAIL_RE.search(normalized)
    if year_match is None:
        return False
    prefix = normalized[: year_match.start()].strip(" ,;:")
    if not prefix or len(prefix) > 180:
        return False
    if ":" in prefix:
        return False
    if not LIKELY_AUTHOR_PREFIX_SEPARATOR_RE.search(prefix):
        return False
    if COMMA_STYLE_AUTHOR_RE.findall(prefix):
        return True
    return len(SURNAME_RE.findall(prefix)) >= 2


def _looks_like_reference_entry_start(text: str) -> bool:
    normalized = _normalize_reference_entry_text(text)
    if not normalized:
        return False
    lowered = normalized.lower()
    venue_prefixes = (
        "in proceedings", "proceedings", "in:", "pages ", "pp.",
        "journal ", "conference ", "in cvpr", "in iccv", "in eccv",
        "in neurips", "in nips", "in iclr", "in icml",
    )
    if lowered.startswith(venue_prefixes):
        return False
    if REFERENCE_ENTRY_START_RE.match(normalized):
        return True
    return _looks_like_author_year_entry_start(normalized)


def _has_nearby_year_marker(text: str, *, max_chars: int = 120) -> bool:
    window = _normalize_reference_entry_text(text)[:max_chars]
    return bool(
        re.search(
            r"(?:\((?:19|20)\d{2}[a-z]?\)|(?:19|20)\d{2}[a-z]?)(?:\.)?",
            window,
        )
    )


def _find_inline_reference_start_offsets(raw: str) -> list[int]:
    normalized = _normalize_reference_entry_text(raw)
    if not normalized:
        return []
    offsets = [0]
    for match in re.finditer(r"\s(?=\[\d{1,4}\]\s+\S)", normalized):
        candidate_offset = match.end()
        if candidate_offset > 0:
            offsets.append(candidate_offset)
    for match in REFERENCE_SENTENCE_BREAK_RE.finditer(normalized):
        candidate_offset = match.end()
        if candidate_offset >= len(normalized):
            continue
        # v1.2: skip split if the period before is an abbreviated initial (e.g. "R. ")
        before = normalized[:match.start()].rstrip()
        if before and re.search(r'\b[A-Z]$', before):
            continue
        if _looks_like_reference_entry_start(normalized[candidate_offset:]):
            offsets.append(candidate_offset)
    for match in COMMA_STYLE_AUTHOR_RE.finditer(normalized):
        candidate_offset = match.start()
        if candidate_offset <= 0:
            continue
        prefix = normalized[:candidate_offset].rstrip()
        if (
            re.search(
                r"(?:\((?:19|20)\d{2}[a-z]?\)|(?:19|20)\d{2}[a-z]?)(?:\.)?\s*$",
                prefix,
            )
            and _has_nearby_year_marker(normalized[candidate_offset:])
        ):
            offsets.append(candidate_offset)
    return sorted(set(offsets))


def _split_inline_reference_chunk(raw: str) -> list[str]:
    normalized = _normalize_reference_entry_text(raw)
    offsets = _find_inline_reference_start_offsets(normalized)
    if len(offsets) <= 1:
        return [normalized] if normalized else []
    parts: list[str] = []
    for index, start in enumerate(offsets):
        end = offsets[index + 1] if index + 1 < len(offsets) else len(normalized)
        part = _normalize_reference_entry_text(normalized[start:end])
        if part:
            parts.append(part)
    return parts


# ---------------------------------------------------------------------------
# Block-level splitting
# ---------------------------------------------------------------------------


def _split_reference_blocks(
    lines: list[str], scope: Scope
) -> list[dict[str, Any]]:
    bibtex_blocks = _split_bibtex_entries(lines, scope)
    if bibtex_blocks is not None:
        return bibtex_blocks
    bibitem_blocks = _split_bibitem_entries(lines, scope)
    if bibitem_blocks is not None:
        return bibitem_blocks

    scoped_lines, scoped_line_start = _scope_lines_without_heading(lines, scope)
    blocks: list[dict[str, Any]] = []
    for block_index, (offset, line) in enumerate(
        enumerate(scoped_lines, start=scoped_line_start)
    ):
        stripped = line.strip()
        if not stripped:
            continue
        source_text = _normalize_reference_entry_text(stripped)
        if not source_text:
            continue
        blocks.append(
            {
                "block_index": block_index,
                "source_text": source_text,
                "line_start": offset,
                "line_end": offset,
                "proposed_entries": _split_inline_reference_chunk(source_text),
                "metadata": {"source_format": "plain_text"},
            }
        )
    return blocks


# ---------------------------------------------------------------------------
# Entry construction from blocks
# ---------------------------------------------------------------------------


def _extract_detected_reference_number(raw: str) -> int | None:
    text = raw.strip()
    for pattern in (
        re.compile(r"^\[(\d{1,3})\]"),
        re.compile(r"^(\d{1,3})[\.\)]"),
        re.compile(r"^(\d{1,3})\s"),
    ):
        match = pattern.match(text)
        if match is not None:
            return int(match.group(1))
    return None


def _strip_reference_number_prefix(raw: str) -> tuple[str, int | None]:
    text = raw.strip()
    detected_ref_number = _extract_detected_reference_number(text)
    if detected_ref_number is not None:
        text = REFERENCE_ENTRY_START_RE.sub("", text, count=1).strip()
    return text, detected_ref_number


def _extract_terminal_publication_year(raw: str) -> int | None:
    matches = [
        int(match.group(1))
        for match in TERMINAL_PUBLICATION_YEAR_RE.finditer(raw)
    ]
    if not matches:
        return None
    return matches[-1]


def _build_reference_entries_from_blocks(
    blocks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    entry_index = 0
    for block in blocks:
        for part in list(block.get("proposed_entries", [])):
            raw = str(part)
            if not raw:
                continue
            normalized_text, detected_ref_number = _strip_reference_number_prefix(
                raw
            )
            entries.append(
                {
                    "entry_index": entry_index,
                    "raw": raw,
                    "year": _extract_terminal_publication_year(raw),
                    "metadata": {
                        "line_start": int(block["line_start"]),
                        "line_end": int(block["line_end"]),
                        "block_index": int(block["block_index"]),
                        "normalized_entry_text": normalized_text,
                        "detected_ref_number": detected_ref_number,
                        **dict(block.get("metadata", {})),
                    },
                }
            )
            entry_index += 1
    return entries


def _split_reference_entries(
    lines: list[str], scope: Scope
) -> list[dict[str, Any]]:
    blocks = _split_reference_blocks(lines, scope)
    return _build_reference_entries_from_blocks(blocks)


# ---------------------------------------------------------------------------
# Candidate generation
# ---------------------------------------------------------------------------


def _looks_like_full_name_author_part(text: str) -> bool:
    tokens = [
        token.strip(" .")
        for token in re.split(r"\s+", text.strip())
        if token.strip(" .")
    ]
    if len(tokens) < 2:
        return False
    if any(len(token) == 1 for token in tokens):
        return False
    return any(char.isalpha() for token in tokens for char in token)


def _split_author_candidates(author_text: str) -> list[str]:
    text = author_text.strip().strip(" ,;:")
    if not text:
        return []
    comma_style = [
        match.group(0).strip().rstrip(" ,;:")
        for match in COMMA_STYLE_AUTHOR_RE.finditer(text)
    ]
    if comma_style:
        return comma_style
    if "," in text:
        parts = [
            part.strip().rstrip(" ,;:")
            for part in text.split(",")
            if part.strip()
        ]
        if len(parts) > 1 and all(
            _looks_like_full_name_author_part(part) for part in parts
        ):
            return parts
    if ";" in text:
        return [
            part.strip().rstrip(" ,;:")
            for part in text.split(";")
            if part.strip()
        ]
    if " and " in text.lower():
        return [
            part.strip().rstrip(" ,;:")
            for part in re.split(r"\band\b|&", text, flags=re.IGNORECASE)
            if part.strip()
        ]
    return [text]


def _make_reference_candidate(
    *,
    entry_index: int,
    pattern: str,
    author_text: str,
    title_candidate: str,
    container_candidate: str,
    year_candidate: int | None,
    confidence: float,
    split_basis: str,
) -> dict[str, Any]:
    return {
        "entry_index": entry_index,
        "pattern": pattern,
        "author_text": author_text.strip().strip(" ,;:"),
        "author_candidates": _split_author_candidates(author_text),
        "title_candidate": title_candidate.strip().strip(" ."),
        "container_candidate": container_candidate.strip().strip(" ."),
        "year_candidate": year_candidate,
        "confidence": confidence,
        "metadata": {"split_basis": split_basis},
    }


def _candidate_authors_colon_title_in_year(
    entry_index: int, text: str, terminal_year: int | None
) -> dict[str, Any] | None:
    match = re.match(
        r"^(?P<authors>.+?):\s*(?P<title>.+?)(?:\.\s*In:\s*(?P<container>.+?))?\s*\((?P<year>(?:19|20)\d{2})[a-z]?\)\s*\.?$",
        text,
    )
    if match is None:
        return None
    # Detect whether the colon is an author-title boundary or a title-internal colon
    # (e.g. "DINO: DETR with..." — "DINO" is a model name, not an author).
    # In published-paper reference lists (as opposed to BibTeX source), the colon
    # is almost never the author-title delimiter.  Only keep high confidence when
    # there is a clear comma-style author list or "and" joining authors before it.
    author_block = match.group("authors").strip()
    has_real_authors = bool(re.search(r',', author_block)) or " and " in author_block.lower()
    # Also require at least 2 tokens in the author block for it to be plausible
    author_token_count = len(author_block.split())
    base_confidence = 0.92 if terminal_year == int(match.group("year")) else 0.84
    if not has_real_authors or author_token_count < 3:
        # Very likely a title-intrinsic colon (e.g. "DINO: DETR with...")
        # Set confidence low enough that sentence and IEEE patterns win
        base_confidence = 0.35
    return _make_reference_candidate(
        entry_index=entry_index,
        pattern="authors_colon_title_in_year",
        author_text=author_block,
        title_candidate=match.group("title"),
        container_candidate=match.group("container") or "",
        year_candidate=int(match.group("year")),
        confidence=base_confidence,
        split_basis="authors block before ':' and title before optional In:/year tail",
    )


def _candidate_ieee_quote_title(
    entry_index: int, text: str, terminal_year: int | None
) -> dict[str, Any] | None:
    """Match IEEE quote-wrapped title: ``I. Surname, ..., "Title," in Venue, Year.``

    Uses ``, \"`` as the boundary between author block and title,
    and ``\",`` as the boundary between title and container/venue text.
    """
    # IEEE format uses American punctuation: comma BEFORE closing quote ("Title,"),
    # while British/standard puts comma AFTER ("Title",).  The `,?` makes the
    # trailing comma optional so both conventions are handled.
    match = re.match(
        r'^(?P<authors>.+?),\s*["“](?P<title>.+?)["”],?\s*(?P<after>.+)$',
        text,
    )
    if match is None:
        return None
    # Extract year from the trailing text
    year_match = YEAR_RE.search(match.group("after"))
    year = int(year_match.group(1)) if year_match else terminal_year
    title = match.group("title").rstrip(",")
    return _make_reference_candidate(
        entry_index=entry_index,
        pattern="ieee_quote_title",
        author_text=match.group("authors"),
        title_candidate=title,
        container_candidate=match.group("after").strip().rstrip(" ."),
        year_candidate=year,
        confidence=0.88,
        split_basis="authors before ',' right-quote, title between quotes, container after quote-comma",
    )


def _candidate_authors_period_title_period_venue_year(
    entry_index: int, text: str, terminal_year: int | None
) -> dict[str, Any] | None:
    match = re.match(
        r"^(?P<authors>.+?)\.\s+(?P<title>.+?)\.(?:\s+(?P<container>.+?))?(?:\s*\(?((?P<year>(?:19|20)\d{2}))\)?)?\.?$",
        text,
    )
    if match is None:
        return None
    year = int(match.group("year")) if match.group("year") else terminal_year
    return _make_reference_candidate(
        entry_index=entry_index,
        pattern="authors_period_title_period_venue_year",
        author_text=match.group("authors"),
        title_candidate=match.group("title"),
        container_candidate=match.group("container") or "",
        year_candidate=year,
        confidence=0.75 if year is not None else 0.62,
        split_basis="first sentence as authors, second sentence as title, trailing sentence/year as container",
    )


def _candidate_authors_year_paren_title_venue(
    entry_index: int, text: str, terminal_year: int | None
) -> dict[str, Any] | None:
    match = re.match(
        r"^(?P<authors>.+?)\s*\((?P<year>(?:19|20)\d{2})[a-z]?\)\.?\s+(?P<title>.+?)(?:\.\s+(?P<container>.+))?$",
        text,
    )
    if match is None:
        return None
    return _make_reference_candidate(
        entry_index=entry_index,
        pattern="authors_year_paren_title_venue",
        author_text=match.group("authors"),
        title_candidate=match.group("title"),
        container_candidate=match.group("container") or "",
        year_candidate=int(match.group("year")) if match.group("year") else terminal_year,
        confidence=0.8,
        split_basis="authors before year parentheses, title after year marker",
    )


def _candidate_thesis_or_book_tail_year(
    entry_index: int, text: str, terminal_year: int | None
) -> dict[str, Any] | None:
    if terminal_year is None:
        return None
    head = re.sub(
        rf"[\s,.;:()]*{terminal_year}[\s,.;:()]*$", "", text
    ).strip()
    if not head:
        return None
    if ":" in head:
        author_text, title_candidate = head.split(":", 1)
    elif ". " in head:
        author_text, title_candidate = head.split(". ", 1)
    else:
        return None
    return _make_reference_candidate(
        entry_index=entry_index,
        pattern="thesis_or_book_tail_year",
        author_text=author_text,
        title_candidate=title_candidate,
        container_candidate="",
        year_candidate=terminal_year,
        confidence=0.58,
        split_basis="tail year stripped first, remaining text split on ':' or first period",
    )


def _candidate_fallback_raw_split(
    entry_index: int, text: str, terminal_year: int | None
) -> dict[str, Any]:
    if ":" in text:
        author_text, title_candidate = text.split(":", 1)
    elif ". " in text:
        author_text, title_candidate = text.split(". ", 1)
    else:
        author_text, title_candidate = text, ""
    return _make_reference_candidate(
        entry_index=entry_index,
        pattern="fallback_raw_split",
        author_text=author_text,
        title_candidate=title_candidate,
        container_candidate="",
        year_candidate=terminal_year,
        confidence=0.35,
        split_basis="fallback split using ':' or first sentence boundary",
    )


def _parse_bibtex_fields(
    raw: str,
) -> tuple[str | None, str | None, dict[str, str]]:
    entry_match = re.search(
        r"@([A-Za-z]+)\s*\{\s*([^,\s]+)\s*,", raw, re.DOTALL
    )
    if entry_match is None:
        return None, None, {}
    entry_type = entry_match.group(1).strip()
    citekey = entry_match.group(2).strip()
    body_start = entry_match.end()
    body = raw[body_start:].strip()
    if body.endswith("}"):
        body = body[:-1]

    fields: dict[str, str] = {}
    current: list[str] = []
    depth = 0
    in_quote = False
    for char in body:
        if char == '"' and depth == 0:
            in_quote = not in_quote
        elif char == "{":
            depth += 1
        elif char == "}":
            depth = max(0, depth - 1)
        if char == "," and depth == 0 and not in_quote:
            segment = "".join(current).strip()
            if "=" in segment:
                key, value = segment.split("=", 1)
                fields[key.strip().lower()] = value.strip()
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if "=" in tail:
        key, value = tail.split("=", 1)
        fields[key.strip().lower()] = value.strip()

    normalized_fields: dict[str, str] = {}
    for key, value in fields.items():
        stripped = value.strip().rstrip(",")
        if stripped.startswith("{") and stripped.endswith("}"):
            stripped = stripped[1:-1]
        if stripped.startswith('"') and stripped.endswith('"'):
            stripped = stripped[1:-1]
        normalized_fields[key] = re.sub(
            r"\s+", " ", stripped.replace("\n", " ")
        ).strip()
    return entry_type, citekey, normalized_fields


def _candidate_bibtex_entry_fields(
    entry_index: int, raw: str
) -> dict[str, Any] | None:
    entry_type, citekey, fields = _parse_bibtex_fields(raw)
    if not fields:
        return None
    author_text = fields.get("author", "")
    title_candidate = fields.get("title", "")
    container_candidate = (
        fields.get("journal")
        or fields.get("booktitle")
        or fields.get("publisher")
        or fields.get("school")
        or fields.get("institution")
        or ""
    )
    year_match = YEAR_RE.search(fields.get("year", ""))
    year_candidate = int(year_match.group(1)) if year_match is not None else None
    candidate = _make_reference_candidate(
        entry_index=entry_index,
        pattern="bibtex_entry_fields",
        author_text=author_text,
        title_candidate=title_candidate,
        container_candidate=container_candidate,
        year_candidate=year_candidate,
        confidence=0.96 if title_candidate and author_text else 0.82,
        split_basis="parsed direct bibtex fields",
    )
    candidate["metadata"].update(
        {
            "citekey": citekey,
            "entry_type": entry_type,
            "parsed_fields": fields,
        }
    )
    return candidate




# ---------------------------------------------------------------------------
# v1.5: venue-marker candidate
# ---------------------------------------------------------------------------

_GENERIC_VENUE_RE = re.compile(
    r'(?:'
    r',\s+[Ii]n\s+|\.\s+[Ii]n\s+|\s+[Ii]n:\s+'
    r'|\s+arXiv\s*[(:]'
    r'|\s+CoRR\s*[(:]'
    r'|\s+Proceedings\s+of[^a-z]'
    r')'
)


def _candidate_venue_marker(
    entry_index: int, text: str, terminal_year: int | None
) -> dict[str, Any] | None:
    """Split at the first universal venue marker, then extract author+title
    from the left side using the period-boundary with initial protection."""
    m = _GENERIC_VENUE_RE.search(text)
    if m is None:
        return None
    author_title = text[:m.start()].strip()
    venue_text = text[m.start():].strip()
    if not author_title or not venue_text:
        return None
    protected = _protect_author_initials(author_title)
    pm = re.match(r'^(?P<authors>.+?)\.\s+(?P<title>.+?)$', protected)
    if pm is None:
        cm = re.match(r'^(?P<authors>.+?):\s*(?P<title>.+?)$', protected)
        if cm is None:
            return None
        author_text = _restore_initials(cm.group("authors").strip())
        title_candidate = _restore_initials(cm.group("title").strip())
    else:
        author_text = _restore_initials(pm.group("authors").strip())
        title_candidate = _restore_initials(pm.group("title").strip())
    title_candidate = re.sub(r'\.\s*$', '', title_candidate)
    return _make_reference_candidate(
        entry_index=entry_index, pattern="venue_marker_split",
        author_text=author_text, title_candidate=title_candidate,
        container_candidate=venue_text, year_candidate=terminal_year,
        confidence=0.85,
        split_basis="split at generic venue marker",
    )


def _extract_bibitem_key(raw: str) -> str | None:
    match = LATEX_BIBITEM_RE.search(raw)
    if match is None:
        return None
    return match.group(1).strip()


# ---------------------------------------------------------------------------
# v1.4: venue-first title extraction
# ---------------------------------------------------------------------------


def _split_at_venue(text: str) -> tuple[str, str]:
    """Split reference text at the first venue-introducing marker.

    Returns ``(author_title_block, venue_text)`` — where venue_text
    is everything from the venue marker onward (including the marker).

    Uses a multi-layered approach:
    1. Venue marker regex patterns from VENUE_MARKERS
    2. Known venue abbreviation (CVPR, ICCV, etc.) as a full word
    """
    # Layer 1: regex venue markers
    for pattern, _name in VENUE_MARKERS:
        m = pattern.search(text)
        if m:
            split = m.start()
            return text[:split].strip(), text[split:].strip()

    # Layer 2: known venue abbreviations (sorted longest-first)
    for abbr in sorted(KNOWN_VENUE_ABBREV, key=len, reverse=True):
        pat = re.compile(r'(?<![A-Za-z])' + re.escape(abbr) + r'(?![A-Za-z])')
        m = pat.search(text)
        if m and m.start() > 15:
            return text[:m.start()].strip(), text[m.start():].strip()

    return text.strip(), ""


def _generate_reference_candidates(
    entry: dict[str, Any],
) -> list[dict[str, Any]]:
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

    candidate_builders = [
        _candidate_ieee_quote_title,
        _candidate_venue_marker,
        _candidate_authors_colon_title_in_year,
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


# ---------------------------------------------------------------------------
# Style detection
# ---------------------------------------------------------------------------


def _ends_with_reference_tail(raw: str) -> bool:
    return REFERENCE_TAIL_AT_END_RE.search(raw.strip()) is not None


def _count_reference_tail_markers(raw: str) -> int:
    return len(list(REFERENCE_TAIL_RE.finditer(raw)))


def _detect_reference_entry_style(entries: list[dict[str, Any]]) -> str:
    numeric_count = 0
    author_year_count = 0
    for entry in entries:
        metadata = dict(entry.get("metadata", {}))
        if metadata.get("detected_ref_number") is not None:
            numeric_count += 1
        if _ends_with_reference_tail(str(entry.get("raw", ""))):
            author_year_count += 1
    if numeric_count and author_year_count:
        return "mixed"
    if numeric_count:
        return "numeric"
    if author_year_count:
        return "author-year"
    return "mixed"


# ---------------------------------------------------------------------------
# Numbering detection
# ---------------------------------------------------------------------------


def _detect_reference_numbering(
    entries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str], bool]:
    numbered: list[tuple[int, int]] = []
    for entry in entries:
        detected = _extract_detected_reference_number(
            str(entry.get("raw", ""))
        )
        if detected is not None:
            numbered.append((int(entry["entry_index"]), detected))

    warnings: list[str] = []
    numbering_by_index = {ei: d for ei, d in numbered}
    anomaly_indices: set[int] = set()
    if len(numbered) > 1:
        previous: int | None = None
        for entry_index, detected in numbered:
            entry_warnings: list[str] = []
            if previous is None:
                if detected != 1:
                    entry_warnings.append(
                        "reference numbering does not start at 1"
                    )
            else:
                if detected <= previous:
                    entry_warnings.append(
                        "reference numbering is not strictly increasing"
                    )
                if detected != previous + 1:
                    entry_warnings.append(
                        "reference numbering is not continuous"
                    )
            previous = detected
            if entry_warnings:
                anomaly_indices.add(entry_index)
                warnings.extend(
                    [
                        f"reference entry {entry_index}: {msg} (detected_ref_number={detected})"
                        for msg in entry_warnings
                    ]
                )

    normalized_entries: list[dict[str, Any]] = []
    for entry in entries:
        entry_obj = dict(entry)
        ei = int(entry_obj["entry_index"])
        metadata = dict(entry_obj.get("metadata", {}))
        numbering_warning_messages = [
            w
            for w in warnings
            if w.startswith(f"reference entry {ei}:")
        ]
        numbering = {
            "detected_ref_number": numbering_by_index.get(ei),
            "has_anomaly": ei in anomaly_indices,
            "warnings": numbering_warning_messages,
        }
        metadata["numbering"] = numbering
        entry_obj["metadata"] = metadata
        normalized_entries.append(entry_obj)
    return normalized_entries, warnings, bool(anomaly_indices)


# ---------------------------------------------------------------------------
# Suspicion detection
# ---------------------------------------------------------------------------


def _detect_reference_block_suspicions(
    *,
    blocks: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    entry_style: str,
) -> list[dict[str, Any]]:
    candidates_by_entry: dict[int, list[dict[str, Any]]] = {}
    for candidate in candidates:
        candidates_by_entry.setdefault(
            int(candidate["entry_index"]), []
        ).append(candidate)

    entries_by_block: dict[int, list[dict[str, Any]]] = {}
    for entry in entries:
        block_index = int(
            dict(entry.get("metadata", {})).get("block_index", -1)
        )
        entries_by_block.setdefault(block_index, []).append(entry)

    block_by_index = {
        int(block["block_index"]): block for block in blocks
    }

    suspicions: list[dict[str, Any]] = []
    consumed_blocks: set[int] = set()

    for index, block in enumerate(blocks):
        block_index = int(block["block_index"])
        if block_index in consumed_blocks:
            continue
        source_text = str(block.get("source_text", ""))
        proposed_entries = [
            str(item)
            for item in block.get("proposed_entries", [])
            if str(item)
        ]
        reasons: list[str] = []
        suspicion_kind: str | None = None
        member_block_indexes = [block_index]
        source_format = str(
            dict(block.get("metadata", {})).get("source_format", "plain_text")
        )

        if source_format in {"bibtex", "latex_bibitem"}:
            reasons = []
        elif len(proposed_entries) > 1 and not all(
            REFERENCE_ENTRY_START_RE.match(entry.strip())
            for entry in proposed_entries
        ):
            reasons.append(
                "single line contains multiple strong reference starts"
            )
            suspicion_kind = "grouped_entries_in_single_line"
        elif not _ends_with_reference_tail(source_text):
            cursor = index + 1
            continuation_found = False
            while cursor < len(blocks):
                next_block = blocks[cursor]
                next_source_text = str(
                    next_block.get("source_text", "")
                )
                if _looks_like_reference_entry_start(next_source_text):
                    break
                continuation_found = True
                member_block_indexes.append(
                    int(next_block["block_index"])
                )
                cursor += 1
            if continuation_found:
                reasons.append(
                    "line does not end like a complete reference entry"
                )
                reasons.append(
                    "following line looks like continuation text rather than a new reference entry"
                )
                suspicion_kind = "possible_multiline_entry"
        else:
            has_detected_number = any(
                dict(entry.get("metadata", {})).get("detected_ref_number")
                is not None
                for entry in entries_by_block.get(block_index, [])
            )
            if (
                entry_style == "author-year"
                and not has_detected_number
                and len(source_text) > 450
            ):
                reasons.append(
                    "entry text is unusually long for a single author-year reference"
                )
                suspicion_kind = suspicion_kind or "mixed_or_ambiguous_boundary"

        # Check candidates for remaining inline reference starts
        for entry in entries_by_block.get(block_index, []):
            entry_index = int(entry["entry_index"])
            raw = str(entry.get("raw", ""))
            for candidate in candidates_by_entry.get(entry_index, []):
                combined = _normalize_reference_entry_text(
                    f"{candidate.get('title_candidate', '')} {candidate.get('container_candidate', '')}"
                )
                if (
                    len(_find_inline_reference_start_offsets(combined)) > 1
                    and len(raw) > 180
                ):
                    reasons.append(
                        "candidate title/container still contains another strong reference start; likely grouped entries remain"
                    )
                    suspicion_kind = suspicion_kind or "mixed_or_ambiguous_boundary"
                    break
            if reasons:
                break

        if reasons:
            source_parts = [
                str(block_by_index[mi]["source_text"])
                for mi in member_block_indexes
            ]
            proposed: list[str] = []
            for mi in member_block_indexes:
                mb = block_by_index[mi]
                proposed.extend(
                    [
                        str(item)
                        for item in mb.get("proposed_entries", [])
                        if str(item)
                    ]
                )
            suspicions.append(
                {
                    "block_index": block_index,
                    "source_text": _normalize_reference_entry_text(
                        " ".join(source_parts)
                    ),
                    "line_start": int(block["line_start"]),
                    "line_end": int(
                        block_by_index[member_block_indexes[-1]][
                            "line_end"
                        ]
                    ),
                    "reasons": list(dict.fromkeys(reasons)),
                    "proposed_entries": proposed,
                    "suspicion_kind": suspicion_kind
                    or "mixed_or_ambiguous_boundary",
                    "member_block_indexes": member_block_indexes,
                }
            )
            consumed_blocks.update(member_block_indexes)

    return suspicions


# ---------------------------------------------------------------------------
# Batch building
# ---------------------------------------------------------------------------


def _build_reference_batches(
    entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    batches: list[dict[str, Any]] = []
    if entries:
        chunk_size = 15
        for batch_index, start in enumerate(
            range(0, len(entries), chunk_size)
        ):
            end = min(start + chunk_size - 1, len(entries) - 1)
            batches.append(
                {
                    "batch_kind": "references_workset",
                    "batch_index": batch_index,
                    "status": "prepared",
                    "entry_start": start,
                    "entry_end": end,
                    "metadata": {"entry_count": end - start + 1},
                }
            )
    return batches


def _reference_review_generation_id(
    suspect_blocks: list[dict[str, Any]],
) -> str:
    basis = json.dumps(
        [
            {
                "block_index": block.get("block_index"),
                "source_text": block.get("source_text"),
                "member_block_indexes": block.get(
                    "member_block_indexes", []
                ),
            }
            for block in suspect_blocks
        ],
        ensure_ascii=False,
        sort_keys=True,
    )
    return f"review-{zlib.crc32(basis.encode('utf-8')) & 0xFFFFFFFF:08x}"


# ---------------------------------------------------------------------------
# Main pipeline entry point
# ---------------------------------------------------------------------------


def prepare_reference_workset(
    lines: list[str],
    scope: Scope,
    *,
    reviewed_raw_entries: list[str] | None = None,
) -> dict[str, Any]:
    """Run the full deterministic preprocessing pipeline.

    Returns the internal state dict (not the export view).  Use
    ``build_workset_export(result)`` to get the JSON-serializable export.
    """
    if reviewed_raw_entries is None:
        blocks = _split_reference_blocks(lines, scope)
        entries = _split_reference_entries(lines, scope)
    else:
        blocks = [
            {
                "block_index": block_index,
                "source_text": _normalize_reference_entry_text(raw),
                "line_start": scope.line_start,
                "line_end": scope.line_end,
                "proposed_entries": [
                    _normalize_reference_entry_text(raw)
                ],
            }
            for block_index, raw in enumerate(reviewed_raw_entries)
            if _normalize_reference_entry_text(raw)
        ]
        entries = _build_reference_entries_from_blocks(blocks)

    normalized_entries, numbering_warnings, has_numbering_anomaly = (
        _detect_reference_numbering(entries)
    )
    candidates: list[dict[str, Any]] = []
    ambiguity_warnings: list[str] = []
    boundary_warnings: list[str] = []

    for entry in normalized_entries:
        entry_candidates = _generate_reference_candidates(entry)
        if len(entry_candidates) > 1:
            ambiguity_warnings.append(
                f"{WARNING_REFERENCE_PATTERN_AMBIGUOUS}: entry_index={entry['entry_index']}"
            )
        for candidate in entry_candidates:
            title_candidate = str(
                candidate.get("title_candidate", "")
            ).strip()
            if not title_candidate or LEADING_PUNCTUATION_RE.match(
                title_candidate
            ):
                boundary_warnings.append(
                    f"{WARNING_REFERENCE_TITLE_BOUNDARY_SUSPECT}: entry_index={entry['entry_index']} pattern={candidate['pattern']}"
                )
            candidates.append(candidate)

    entry_style = _detect_reference_entry_style(normalized_entries)
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
    batches = _build_reference_batches(normalized_entries)

    return {
        "blocks": blocks,
        "entries": normalized_entries,
        "candidates": candidates,
        "batches": batches,
        "entry_style": entry_style,
        "suspect_blocks": suspect_blocks,
        "requires_split_review": bool(suspect_blocks),
        "numbering_warnings": numbering_warnings,
        "has_numbering_anomaly": has_numbering_anomaly,
        "warnings": list(
            dict.fromkeys(
                [
                    *numbering_warnings,
                    *ambiguity_warnings,
                    *boundary_warnings,
                    *grouping_warnings,
                ]
            )
        ),
    }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_workset_export(prepared: dict[str, Any]) -> dict[str, Any]:
    """Convert the internal prepared state to the export JSON structure."""
    blocks = prepared["blocks"]
    entries = prepared["entries"]
    candidates = prepared["candidates"]
    batches = prepared["batches"]
    entry_style = prepared["entry_style"]
    suspect_blocks = prepared["suspect_blocks"]
    requires_split_review = prepared["requires_split_review"]

    candidates_by_entry: dict[int, list[dict[str, Any]]] = {}
    for candidate in candidates:
        candidates_by_entry.setdefault(
            int(candidate["entry_index"]), []
        ).append(candidate)

    export_entries: list[dict[str, Any]] = []
    for entry in entries:
        metadata = dict(entry.get("metadata", {}))
        numbering = dict(metadata.get("numbering", {}))
        export_entries.append(
            {
                "entry_index": int(entry["entry_index"]),
                "raw": str(entry["raw"]),
                "detected_ref_number": numbering.get("detected_ref_number"),
                "numbering": numbering,
                "patterns": candidates_by_entry.get(
                    int(entry["entry_index"]), []
                ),
            }
        )

    return {
        "meta": {
            "generated_at": utc_now_iso(),
            "entry_count": len(export_entries),
            "candidate_count": len(candidates),
            "batch_count": len(batches),
            "entry_style": entry_style,
            "split_mode": "line-first",
            "grouping_suspect_count": len(suspect_blocks),
            "requires_split_review": requires_split_review,
            "review_generation_id": (
                _reference_review_generation_id(suspect_blocks)
                if suspect_blocks
                else ""
            ),
        },
        "blocks": [
            {
                "block_index": int(block["block_index"]),
                "source_text": str(block["source_text"]),
                "line_start": int(block["line_start"]),
                "line_end": int(block["line_end"]),
                "proposed_entries": [
                    str(item)
                    for item in block.get("proposed_entries", [])
                    if str(item)
                ],
            }
            for block in blocks
        ],
        "entries": export_entries,
        "batches": batches,
        "suspect_blocks": [
            {
                "block_index": int(block["block_index"]),
                "source_text": str(block["source_text"]),
                "line_start": int(block["line_start"]),
                "line_end": int(block["line_end"]),
                "reasons": list(block.get("reasons", [])),
                "proposed_entries": list(
                    block.get("proposed_entries", [])
                ),
                "suspicion_kind": str(
                    block.get("suspicion_kind", "")
                ),
            }
            for block in suspect_blocks
        ],
        "warnings": prepared["warnings"],
    }


# ---------------------------------------------------------------------------
# v1.1 helpers — strip trailing page markers, protect initials, year validation
# ---------------------------------------------------------------------------


def _merge_fragments(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge consecutive incomplete blocks into complete entries.

    A block is "incomplete" if:
    - It starts with a lowercase letter (likely a continuation line)
    - It contains no reference number prefix and no year (likely a fragment)

    Merged blocks' source_text is joined with a space, and proposed_entries
    are extended.
    """
    if not blocks:
        return blocks

    merged: list[dict[str, Any]] = []
    for block in blocks:
        text = str(block.get("source_text", ""))
        source_fmt = str(
            dict(block.get("metadata", {})).get("source_format", "plain_text")
        )
        has_ref_number = bool(
            _extract_detected_reference_number(text)
            or REFERENCE_ENTRY_START_RE.match(text)
        )
        has_year = _extract_terminal_publication_year(text) is not None
        is_capital_start = bool(text and text[0].isupper())

        is_fragment = (
            not has_ref_number
            and not has_year
            and not is_capital_start
            and len(text) < 80
        ) or (
            text
            and text[0].islower()
            and not has_ref_number
        )

        if is_fragment and merged:
            # Merge into previous block
            prev = merged[-1]
            prev["source_text"] += " " + text
            prev["line_end"] = int(block["line_end"])
            prev["proposed_entries"] = (
                prev.get("proposed_entries", [])
                + block.get("proposed_entries", [])
            )
        else:
            merged.append(dict(block))
            merged[-1]["block_index"] = len(merged) - 1

    return merged


def _strip_trailing_page_markers(raw: str) -> str:
    """Strip trailing in-text citation page number markers (e.g. '1, 2, 7').

    A line like '[3] Author. Title. Venue, 2010. 4, 10, 21, 28' becomes
    '[3] Author. Title. Venue, 2010.' — the trailing '4, 10, 21, 28' is removed.
    """
    text = raw.rstrip()
    if not text:
        return raw
    matches = list(TERMINAL_PUBLICATION_YEAR_RE.finditer(text))
    if not matches:
        return raw
    for m in reversed(matches):
        after = text[m.end():]
        clean_after = after.strip().lstrip(",.;: ")
        if clean_after and TRAILING_PAGE_MARKER_RE.match("," + clean_after):
            return text[:m.end()].rstrip(" ,.") + "."
    return raw


def _is_valid_publication_year(year: int) -> bool:
    """Check if a 4-digit number is a plausible publication year.

    Rejects arXiv prefix fragments, volume/issue numbers, and page ranges.
    Upper bound is current year + 1 (preprints / early access).
    """
    from datetime import date
    return 1800 <= year <= date.today().year + 1


def _protect_author_initials(text: str) -> str:
    """Protect abbreviated author initials from being treated as sentence boundaries.

    Only protects initials that follow a comma, ``"and "``, or start of text
    (i.e. initials that are clearly part of an author list). This avoids false
    positives on ``A. Title description`` where ``A.`` starts the title.

    ``K. He, X. Zhang`` → ``K\\x00He, X\\x00Zhang`` (after comma)
    ``and P. Frasconi`` → ``and P\\x00Frasconi`` (after ``and``)
    ``Y. Bengio`` at start of text → ``Y\\x00Bengio``
    ``V. 2001`` → NOT protected (no uppercase letter after space)
    """
    return re.sub(
        r"(?:^|,\s*|\band\s+(?:et\s+al\.\s*)?|\[\d+\]\.?\s*)([A-Z])\.\s+(?=[A-Z])",
        lambda m: m.group(0).replace(
            m.group(1) + ". ",
            m.group(1) + "\x00",
        ),
        text,
    )


def _restore_initials(text: str) -> str:
    """Reverse :func:`_protect_author_initials` — replace ``\\x00`` with ``. ``."""
    return text.replace("\x00", ". ")



# ---------------------------------------------------------------------------
# Single-call convenience
# ---------------------------------------------------------------------------


def process_reference_text(
    raw_text: str,
    *,
    section_title: str = "References",
) -> dict[str, Any]:
    """Preprocess raw reference text and return the export JSON object.

    This is the simplest entry point: pass a block of reference text
    and get back the full workset export.
    """
    lines = raw_text.split("\n")
    scope = Scope(
        section_title=section_title,
        line_start=1,
        line_end=len(lines),
        metadata={},
    )
    prepared = prepare_reference_workset(lines, scope)
    return build_workset_export(prepared)
