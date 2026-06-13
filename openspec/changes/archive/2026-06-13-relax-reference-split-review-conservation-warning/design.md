## Design Notes

- Token conservation is a runtime-only validation detail. It should be stricter than fuzzy similarity but more tolerant than string equality.
- Conservation tokens should normalize Unicode, fullwidth/halfwidth variants, whitespace, common quotes, dash variants, and punctuation style.
- Protected evidence tokens such as URL, DOI, arXiv identifiers, years, and numeric identifiers must not be dropped.
- If conservation passes but boundary heuristics still report suspect blocks, the runtime should record `reference_boundary_suspicion_after_review` warnings and continue with regenerated review packages.
- The final public artifact contract is unchanged. Any split review audit data remains in tmp runtime sidecars or warnings.

## Non-Goals

- No new `accept_reviewed_entries` action.
- No new public CLI command.
- No change to `reference_reviews[]`, `metadata_reviews[]`, or final `references.json` schema.
