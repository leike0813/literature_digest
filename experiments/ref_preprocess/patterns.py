"""Regex constants and warning labels extracted from literature-digest stage_runtime.py."""

import re

# === Markdown/LaTeX structure ===
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LATEX_BIBITEM_RE = re.compile(r"\\bibitem\{([^}]+)\}")
BIBTEX_ENTRY_START_RE = re.compile(r"(?m)^\s*@([A-Za-z]+)\s*\{\s*([^,\s]+)\s*,")

# === Reference entry detection ===
REFERENCE_ENTRY_START_RE = re.compile(r"^(?:\[\d{1,3}\]|\d{1,3}[\.\)])\s*")
COMMA_STYLE_AUTHOR_RE = re.compile(
    r"[A-Z][A-Za-z'`-]+,\s*(?:[A-Z][A-Za-z.-]*\.?(?:\s*[A-Z][A-Za-z.-]*\.?)*)"
)
LEADING_PUNCTUATION_RE = re.compile(r"^[,.;:]\s*")
YEAR_WITH_TAIL_RE = re.compile(
    r"(?:\((?:19|20)\d{2}[a-z]?\)|(?:19|20)\d{2}[a-z]?)\.\s+"
)
REFERENCE_SENTENCE_BREAK_RE = re.compile(r"\.\s+")
LIKELY_AUTHOR_PREFIX_SEPARATOR_RE = re.compile(
    r"(?:;|,\s| and | & )", re.IGNORECASE
)

# === Year detection ===
YEAR_RE = re.compile(r"\b((?:19|20)\d{2})[a-z]?\b")
TERMINAL_PUBLICATION_YEAR_RE = re.compile(
    r"\b((?:19|20)\d{2})[a-z]?\b(?!\.\d{3,})"
)
REFERENCE_TAIL_RE = re.compile(
    r"(?:\((?:19|20)\d{2}[a-z]?\)|(?:19|20)\d{2}[a-z]?)(?:\.)?(?=\s|$)"
)
REFERENCE_TAIL_AT_END_RE = re.compile(
    r"(?:\((?:19|20)\d{2}[a-z]?\)|(?:19|20)\d{2}[a-z]?)(?:\.)?\s*$"
)

# === Author-related ===
SURNAME_RE = re.compile(r"[A-Za-z][A-Za-z'`-]+")

# === Trailing page marker stripping (v1.1) ===
# Matches trailing: ", 1", ", 2, 7", ", pp. 2070-2079", ", 4, 10, 21, 28"
TRAILING_PAGE_MARKER_RE = re.compile(
    r"(?:,\s*(?:pp?\.?\s*)?(?:\d+(?:\s*[–\-]\s*\d+)?))+\s*$"
)

# === Non-reference content filtering (v1.3) ===
NON_REFERENCE_LINE_RE = re.compile(
    r"^(?:!\[|<table|Figure\s+\d+|Table\s+\d+|#+\s)"
)

# === Venue marker patterns (v1.4) ===
# Ordered by reliability for title-container boundary detection.
# Each is a (regex, description) tuple.
VENUE_MARKERS: list[tuple[re.Pattern, str]] = [
    (re.compile(r',\s*[Ii]n\s+'), 'comma-in'),
    (re.compile(r'\.\s*[Ii]n\s+'), 'period-in'),
    (re.compile(r'\s+[Ii]n:\s*'), 'colon-in'),
    (re.compile(r'\s+arXiv\s*[(:]'), 'arxiv'),
    (re.compile(r'\s+CoRR\s*[(:]'), 'corr'),
    (re.compile(r'\s+Proceedings\s+of\b'), 'proceedings'),
    (re.compile(r'\.\s+(?:IEEE|ACM|Elsevier|Springer)\b'), 'pub-org'),
    (re.compile(r'\s+(?:Advances|European|International)\s'), 'container-keyword'),
]

# Known venue abbreviations (uppercase) that most likely introduce container
KNOWN_VENUE_ABBREV: set[str] = {
    "CVPR", "ICCV", "ECCV", "NeurIPS", "NIPS", "ICLR", "ICML", "AAAI",
    "IJCAI", "BMVC", "WACV", "ACCV", "MICCAI", "ICRA", "IROS", "CoRL",
    "ACL", "EMNLP", "NAACL", "ICASSP", "ICIP", "MM", "TIP", "TPAMI",
    "IJCV", "TNN", "TMI", "JMLR",
}

# === Warning labels ===
WARNING_REFERENCE_LOW_CONFIDENCE = "reference_parse_low_confidence"
WARNING_REFERENCE_PATTERN_AMBIGUOUS = "reference_pattern_ambiguous"
WARNING_REFERENCE_TITLE_BOUNDARY_SUSPECT = "reference_title_boundary_suspect"
WARNING_REFERENCE_AUTHOR_OVERSPLIT = "reference_author_oversplit_detected"
WARNING_REFERENCE_ENTRY_GROUPING_SUSPECT = "reference_entry_grouping_suspect"
