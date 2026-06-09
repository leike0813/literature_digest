# Design: Unicode-Aware Reference Title Quality Gate

## Tokenization

The classifier continues to normalize titles with NFKC, lowercase, punctuation/symbol replacement, and whitespace collapse. Content tokens are then derived without third-party dependencies:

- Keep contiguous Unicode letter runs.
- Keep ASCII mixed alphanumeric runs such as `yolov7`.
- Drop pure numeric runs.
- Apply existing ASCII stopwords to ASCII tokens only.

`no_usable_title_tokens` is emitted only when no usable Unicode letter or mixed alphanumeric token remains.

## Short Title Warning

`short_title_requires_context` remains for genuinely short Latin titles, but it does not fire for titles containing at least four non-ASCII letters. This avoids warning on a normal Chinese title that naturally appears as one continuous token.

## Language Preservation

Reference title recovery must preserve the raw reference's original language and script. Quality repair means recovering the cited work title from raw text or candidates, not translating, Anglicizing, or romanizing it.

