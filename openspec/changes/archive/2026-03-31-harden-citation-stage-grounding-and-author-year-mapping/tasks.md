# Tasks

- [x] Add a new active change for stage-5 grounding hardening and author-year first-author alias matching
- [x] Add the `action_receipts` table and helper functions in the runtime DB layer
- [x] Record and invalidate action receipts across the main-path stage runtime actions
- [x] Make gate and render require a complete stage-5 receipt chain before final publication
- [x] Fail `prepare_citation_workset` when review-like or citation-shaped scopes produce no stable mentions/workset items
- [x] Ground citation timeline and summary ref-index validation on persisted `citation_items`
- [x] Fix author-year first-author alias matching for multi-token names such as `Waqas Zamir`
- [x] Update stage-5 guidance, runtime interface docs, gate docs, and core instructions
- [x] Add regression coverage for receipt-chain enforcement and multi-token author-year mapping
- [x] Validate with mypy, pytest, and `openspec validate --changes --json --no-interactive`
