## 1. Input Contract and Dispatcher

- [x] 1.1 Replace the public input contract with `source_path` in schema, runner prompt, and skill documentation.
- [x] 1.2 Implement a dispatcher that detects PDF by signature and otherwise falls back to UTF-8 text detection.
- [x] 1.3 Normalize every input into `<cwd>/.literature_digest_tmp/source.md` and emit `source_meta.json`.

## 2. PDF Conversion and Provenance

- [x] 2.1 Add `pymupdf4llm` as the preferred PDF-to-Markdown path without making it a hard runtime requirement.
- [x] 2.2 Implement a Python-standard-library PDF text fallback that preserves enough text for downstream processing.
- [x] 2.3 Update provenance and output-fix scripts so `input_hash` and artifact directories are based on the original `source_path`.

## 3. Validation, Specs, and Regression Coverage

- [x] 3.1 Add regression tests for extensionless inputs, disguised extensions, stdlib fallback, and unsupported binary inputs.
- [x] 3.2 Update canonical OpenSpec specs to reflect `source_path`, normalization, and PDF fallback behavior.
- [x] 3.3 Run `conda run --no-capture-output -n DataProcessing mypy literature-digest/scripts`.
- [x] 3.4 Run `conda run --no-capture-output -n DataProcessing pytest -q tests/test_dispatch_source.py tests/test_validate_output.py tests/test_citation_preprocess.py`.
