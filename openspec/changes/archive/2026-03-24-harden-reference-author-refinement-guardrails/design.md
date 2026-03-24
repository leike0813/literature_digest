# Design: harden-reference-author-refinement-guardrails

## Overview

This change adds a narrow validation layer to stage 4:

1. `prepare_references_workset` continues to generate deterministic `author_candidates`
2. `persist_references` continues to accept refined `items[]`
3. before writing `reference_items`, `persist_references` now compares submitted `author[]` against the selected candidate boundaries

## Validation Rule

The validation only activates when the selected candidate already has stable author boundaries:

- multiple prepared `author_candidates`, or
- a comma-style prepared author such as `Surname, I.`

For those entries:

- exact reuse is valid
- light formatting normalization is valid
- splitting one prepared author into multiple array elements is invalid

The detection is intentionally conservative:

- it compares normalized candidate authors with normalized submitted authors
- it rejects submissions that can only be explained by concatenating multiple submitted elements back into each prepared author boundary

## Failure Semantics

When over-splitting is detected:

- `persist_references` fails
- the error code is `reference_author_refinement_invalid`
- a runtime warning with `reference_author_oversplit_detected` is recorded
- no malformed `reference_items` are written
