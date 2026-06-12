## 1. OpenSpec

- [x] 1.1 Create proposal, design, spec delta, and task checklist for the change.

## 2. Runtime

- [x] 2.1 Bootstrap `run_analysis.py` imports from its own script directory.
- [x] 2.2 Return structured JSON for payload file read and JSON parse failures.
- [x] 2.3 Add deterministic metadata alias normalization with warning collection.
- [x] 2.4 Apply metadata normalization to `reference_reviews[]` and `metadata_reviews[]`.
- [x] 2.5 Strengthen reference and citation prepare/JIT batch contracts and prompts.

## 3. Guidance

- [x] 3.1 Update skill and reference guidance to use portable bare-Python commands.
- [x] 3.2 Document JSON-safe payload files, subagent canonical return shapes, metadata aliases, and web-reference timeline warnings.

## 4. Tests

- [x] 4.1 Add runtime coverage for script-path invocation and invalid JSON payload errors.
- [x] 4.2 Add runtime coverage for metadata alias normalization warnings.
- [x] 4.3 Add guidance coverage for portable runtime commands and stronger subagent contracts.
- [x] 4.4 Run targeted runtime, guidance, and render artifact tests plus OpenSpec status.
