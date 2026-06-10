# Change: Reject Placeholder Reference Titles

## Summary

Add a Stage 4 hard quality gate for reference rows whose entire `title` is only a placeholder string such as `none`, `null`, `unknown`, or `untitled`.

## Motivation

The current reference title quality classifier correctly rejects empty titles, identifiers, URLs, metadata-only strings, author-only strings, and titles with no usable tokens. However, string placeholders such as `"null"` or `"unknown"` contain usable English tokens and can pass as soft warnings. This lets an agent persist a non-title value when the real cited work title could not be recovered.

## Scope

- Add a stable hard reason code `placeholder_title`.
- Match only complete placeholder titles after normalization; do not reject normal titles that merely contain words like "unknown" or "untitled".
- Return the issue through existing `quality_directives` with row evidence and repair recommendations.
- Update Stage 4 guidance and focused regression tests.

## Out Of Scope

- No changes to `literature-digest-lite`.
- No public artifact shape changes.
- No new dependency or parser.
