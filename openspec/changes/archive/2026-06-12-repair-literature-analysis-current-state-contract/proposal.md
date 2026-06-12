## Why

`literature-analysis` now has a current agent-facing runtime contract, but several package assets still describe the old execution protocol. Reference split review is also documented as supported while the public `persist_references` adapter does not yet process `split_reviews[]`.

This creates two practical risks: runner prompts can send agents down the wrong script path, and LNCS/grouped reference repair remains a paper contract rather than an executable path.

## What Changes

- Clean `literature-analysis` assets and guidance so they describe only the current `scripts/run_analysis.py` workflow.
- Add `split_reviews[]` handling to the reference runtime adapter.
- Return regenerated reference work packages after split repair.
- Add tests for asset current-state hygiene, bytecode exclusion, and split review behavior.

## Impact

- **Public CLI**: unchanged.
- **Final artifacts/stdout**: unchanged.
- **Agent-facing payloads**: `split_reviews[]` becomes executable; `reference_reviews[]` and `citation_semantic_reviews[]` remain the main submit payloads.
- **Old skill**: unchanged.
