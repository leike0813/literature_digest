## 1. Runtime Inputs And State

- [x] 1.1 Add `identifier` to the runner parameter, CLI initialization, runtime inputs, and source profile with DOI/arXiv normalization and warning behavior.
- [x] 1.2 Add analysis-plan `source_identity` validation, normalized-source evidence checks, and SQLite persistence.
- [x] 1.3 Add SQLite fetch-cache and per-entry API-resolution tables, helpers, receipts, audit export, and invalidation behavior.

## 2. API Resolution

- [x] 2.1 Implement the provider-neutral candidate model, injectable bounded HTTP transport, Crossref adapter, and Semantic Scholar adapter in `reference_api.py`.
- [x] 2.2 Implement provider merging, identifier/title matching, completeness and quality gates, and deterministic per-entry decisions.
- [x] 2.3 Integrate API resolution after stable local preparation and emit warning-only provider outcomes with cached retry behavior.
- [x] 2.4 Apply the 0.95 title threshold only to non-exact Semantic Scholar candidates carrying a normalized arXiv identifier.

## 3. Partial Reference Workflow

- [x] 3.1 Generate core review batches and required coverage only for unresolved entries, protecting API-resolved keys from agent writes.
- [x] 3.2 Merge API and agent reference items atomically while retaining local order, raw evidence, parse audit, and quality checks.
- [x] 3.3 Filter metadata evidence work to locally reviewed items and auto-advance to citation when all entries are API-resolved.
- [x] 3.4 Run API resolution before split externalization, map suspect blocks to entry indexes, suppress only fully accepted blocks, and auto-keep them during partial split submission.

## 4. Skill Contract And Guidance

- [x] 4.1 Update `SKILL.md`, source/plan guidance, reference extraction guidance, and core instructions with the current API-first flow and LLM/script boundary.
- [x] 4.2 Update parameter schema, runner prompt/version, gate guidance, and optional-network compatibility without changing final output schemas.
- [x] 4.3 Remove affected brittle instruction-text assertions without adding replacement static wording tests.
- [x] 4.4 Describe the accepted-aware split order and whole-block partial-review rule as the current runtime contract.

## 5. Verification

- [x] 5.1 Add provider, normalization, matching, cache, and failure behavior tests using mocked HTTP only.
- [x] 5.2 Add runtime integration tests for partial/full resolution, split invalidation, fallback, metadata filtering, and unchanged public rendering.
- [x] 5.3 Run strict OpenSpec validation, focused tests, the full test suite, and the final skill quality-gate review.
- [x] 5.4 Add matching and runtime scenarios for arXiv threshold competition, fully accepted suspect blocks, partial accepted blocks, cache reuse, and boundary invalidation.
- [x] 5.5 Re-run strict OpenSpec validation, focused tests, the full test suite, and the final skill quality-gate review after the accepted-aware split changes.
