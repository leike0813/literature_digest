## ADDED Requirements

### Requirement: LaTeX Input Normalization

The skill SHALL accept a single `.tex` file or a LaTeX project directory as `source_path`.

#### Scenario: Single tex file

- **WHEN** `source_path` points to a readable `.tex` file
- **THEN** `normalize_source` produces fenced `tex` content in `source_documents.normalized_source`

#### Scenario: LaTeX project directory

- **WHEN** `source_path` points to a directory containing LaTeX sources
- **THEN** the runtime detects a main tex entry file, expands `\input` / `\include`, and stores fenced `tex` content in `source_documents.normalized_source`

### Requirement: Raw Bib Source Preservation

When bibliography sources are available as `.bib` files, the runtime SHALL append them to normalized source as fenced `bibtex` blocks.

#### Scenario: Linked bib files exist

- **WHEN** LaTeX input references `.bib` files through bibliography commands
- **THEN** each resolved `.bib` file is appended to normalized source with an explanatory note and a `bibtex` code fence

### Requirement: Deterministic LaTeX Reference Splitting

Stage 4 SHALL deterministically split `\bibitem` and `bibtex` bibliography sources before LLM refinement.

#### Scenario: Bibitem bibliography

- **WHEN** the references scope contains `\bibitem{...}`
- **THEN** `prepare_references_workset` splits entries on `\bibitem` boundaries

#### Scenario: Bibtex bibliography

- **WHEN** the references scope contains fenced bibtex entries
- **THEN** `prepare_references_workset` splits entries on top-level `@type{key,` boundaries and emits deterministic candidates from bib fields

### Requirement: LaTeX Citation Mapping

Stage 5 SHALL support LaTeX citation commands and prefer citekey mapping.

#### Scenario: Cite commands with keys

- **WHEN** normalized source contains `\cite{a,b}`-style markers
- **THEN** `prepare_citation_workset` extracts one mention per citekey and maps them to `reference_items` using citekey metadata when available
