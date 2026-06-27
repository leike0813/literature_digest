## Why

Citation analysis currently behaves like an all-or-nothing quality gate. When source text is irregular, strict citation review coverage and non-empty field checks can block final rendering and discard otherwise useful digest and reference artifacts.

## What Changes

- Relax citation analysis validation so incomplete semantic reviews can still be persisted.
- Allow empty citation semantic fields, empty timeline summaries, empty global summary, and empty citation items.
- Merge duplicate citation review entries by `citation_work_key` instead of failing.
- Keep hard failures only for unsafe structural problems such as invalid JSON, unknown citation keys, forbidden internal fields, missing normalized source, or missing citation scope.
- Ensure final render still produces `digest.md`, `references.json`, `citation_analysis.json`, `citation_analysis.md`, and `literature_matching_metadata.json` when citation content is partial or empty.
- Update skill guidance to describe citation analysis as tolerant best-effort persistence without runtime-generated pseudo-semantic content.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `literature-analysis`: citation analysis validation changes from strict complete-review gating to tolerant best-effort persistence.

## Impact

- Affects `literature-analysis` citation runtime validation, citation workset preparation, render prerequisites, public output validation, guidance docs, runner instruction text, and tests.
- No dependency changes.
- No public payload field changes.
