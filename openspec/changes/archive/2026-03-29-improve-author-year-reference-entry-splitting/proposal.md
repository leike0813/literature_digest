# improve-author-year-reference-entry-splitting

## Summary

Improve stage 4 reference preprocessing for author-year bibliographies by combining stronger deterministic splitting with an agent split-review step that runs only when grouped-entry suspicion remains.

## Why

Real runs showed that author-year references can be grouped into a few paragraph-sized entries when the bibliography does not use numeric prefixes. Downstream candidate generation and agent refinement then operate on malformed raw entries and silently lose valid references.

## What Changes

- Strengthen deterministic entry splitting for author-year references, including year suffix forms such as `2017a` / `2020b`
- Add grouped-entry suspicion detection and route suspicious stage-4 worksets to a new `persist_reference_entry_splits` action
- Let the split-review action rewrite only raw entry boundaries, then regenerate parse candidates before final reference refinement
- Add regression fixtures and tests for grouped author-year references and appendix truncation
- Update skill and runtime docs so stage 4 clearly distinguishes split review from final reference refinement
