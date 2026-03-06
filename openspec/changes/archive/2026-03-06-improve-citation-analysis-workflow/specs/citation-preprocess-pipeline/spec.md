## ADDED Requirements

### Requirement: Deterministic Citation-Scope Preprocess
The system MUST run a deterministic preprocessing stage before citation semantic analysis. The stage MUST consume agent-provided `citation_scope`, extract citation mentions within that scope, and normalize mention records into a machine-readable intermediate artifact.

#### Scenario: Preprocess generates intermediate artifact
- **WHEN** citation analysis starts for a valid `md_path`
- **THEN** the system writes a preprocess artifact under `<cwd>/.literature_digest_tmp/`
- **AND** the artifact includes `citation_scope` metadata and normalized mention entries.

#### Scenario: Scope ownership boundary
- **WHEN** preprocess executes with a valid scope input
- **THEN** preprocess does not re-decide or narrow semantic review scope
- **AND** mention extraction is bounded to the provided scope lines.

### Requirement: Mention Normalization for Numeric and Author-Year Styles
The preprocess stage MUST support both numeric and author-year citation forms and MUST normalize each detected mention with a stable `mention_id`.

#### Scenario: Numeric marker normalization
- **WHEN** `citation_scope` text contains numeric markers such as `[5, 36]` or `[40–42]`
- **THEN** preprocess output includes normalized mention entries for each cited marker
- **AND** ranges are expanded into discrete mention targets.

#### Scenario: Author-year marker normalization
- **WHEN** `citation_scope` text contains author-year forms such as `(Smith, 2020)` or `Smith et al. (2020)`
- **THEN** preprocess output includes normalized mention entries with parsed author-year hints
- **AND** multi-citation groups separated by semicolons are split into independent mention entries.

### Requirement: Stable Temporary Artifact Location
Temporary preprocess artifacts MUST be written to `<cwd>/.literature_digest_tmp/` and MUST be retained by default.

#### Scenario: Temporary files are retained
- **WHEN** preprocess completes successfully
- **THEN** generated files remain in `<cwd>/.literature_digest_tmp/`
- **AND** the system does not perform automatic cleanup.
