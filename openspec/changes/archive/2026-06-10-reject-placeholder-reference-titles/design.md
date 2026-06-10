# Design: Placeholder Reference Title Gate

## Classifier Rule

The classifier adds a `placeholder_title` hard reason code after title normalization. A title is considered a placeholder only when the whole normalized title matches the placeholder set.

Initial placeholders:

- `none`
- `null`
- `undefined`
- `n/a`
- `na`
- `not available`
- `unknown`
- `untitled`

The rule uses NFKC, trim, lowercase, whitespace collapse, and punctuation/symbol normalization consistent with the existing title quality classifier. Slash/dot/space variants of `n/a` collapse to the same compact key, so `N.A.`, `N / A`, and `NA` are rejected.

## Flow

`persist_references` continues to normalize rows and classify quality before writing `reference_items`. If any row hits `placeholder_title`, the runtime:

- does not write `reference_items`;
- stores active `reference_quality_issues`;
- keeps workflow at `stage_4_references / persist_references`;
- lets gate return the normal Stage 4 hard-block directives.

The recommendation tells the agent to recover the cited work title from raw/candidates in the original language/script or omit the row if unrecoverable.
