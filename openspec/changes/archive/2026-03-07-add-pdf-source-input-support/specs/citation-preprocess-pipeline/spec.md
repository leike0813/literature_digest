## MODIFIED Requirements

### Requirement: Deterministic Citation-Scope Preprocess

The system MUST run a deterministic preprocessing stage before citation semantic analysis. The stage MUST consume agent-provided `citation_scope`, operate on the dispatcher-normalized markdown derived from `source_path`, extract citation mentions within that scope, and normalize mention records into a machine-readable intermediate artifact.

#### Scenario: Preprocess generates intermediate artifact
- **WHEN** citation analysis starts for a valid `source_path`
- **THEN** the system writes a preprocess artifact under `<cwd>/.literature_digest_tmp/`
- **AND** the artifact includes `citation_scope` metadata and normalized mention entries.

#### Scenario: Scope ownership boundary
- **WHEN** preprocess executes with a valid scope input
- **THEN** preprocess does not re-decide or narrow semantic review scope
- **AND** mention extraction is bounded to the provided scope lines.
