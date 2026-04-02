## ADDED Requirements

### Requirement: LaTeX Runtime Metadata

The runtime SHALL persist LaTeX normalization metadata for later stages and auditing.

#### Scenario: LaTeX normalization succeeds

- **WHEN** `normalize_source` processes a `.tex` file or LaTeX project directory
- **THEN** `source_documents.normalized_source.metadata_json` includes `source_type`, `detection_method`, `conversion_backend`, and any resolved `main_tex_path` / `included_tex_files` / `bib_files`

### Requirement: Citekey-Aware Citation Workset

The citation workset SHALL allow mentions to carry citekey hints and references to expose citekey aliases through metadata without changing public output schema.

#### Scenario: Reference item has citekey metadata

- **WHEN** a reference item originates from `\bibitem` or `.bib`
- **THEN** its metadata retains the citekey or bibitem key for citekey-first mention mapping
