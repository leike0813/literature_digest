## Why

Some papers use source-local alpha citation labels such as `[RNSS18]`, `[DGV+18]`, or grouped forms like `[RNSS18, DCLT18]` instead of numeric or author-year citations. The current citation workset preparation ignores these labels, leaving citation analysis with no mapped workset for otherwise well-formed reference lists.

## What Changes

- Detect non-numeric bracket labels at the start of plain-text reference entries and preserve them as internal citation aliases.
- Extract bracket-alpha citation mentions from body text, including grouped labels and common OCR/TeX spacing noise.
- Join citation mentions to references by label alias before falling back to numeric and author-year mapping.
- Render mapped alpha-label references using their source label, while preserving numeric and author-year rendering behavior.
- Update skill guidance to describe bracket-alpha labels as runtime-managed mapping hints.

## Capabilities

### New Capabilities

### Modified Capabilities
- `literature-analysis`: Citation workset preparation supports source-local bracket-alpha citation labels.

## Impact

- Affects `literature-analysis` runtime citation/reference preprocessing, citation workset construction, citation rendering labels, guidance docs, and runtime tests.
- No public artifact schema or agent citation semantic payload fields are added.
