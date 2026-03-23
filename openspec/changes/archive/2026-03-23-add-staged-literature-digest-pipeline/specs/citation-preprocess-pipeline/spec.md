## MODIFIED Requirements

### Requirement: Deterministic Citation-Scope Preprocess

The system MUST run a deterministic preprocessing stage before citation semantic analysis. The stage MUST consume agent-provided `citation_scope`, operate on the dispatcher-normalized markdown derived from `source_path`, extract citation mentions within that scope, and normalize mention records into a machine-readable intermediate artifact.

#### Scenario: Preprocess remains extraction-only
- **WHEN** preprocess executes with a valid scope input
- **THEN** it does not merge semantic parts, publish final citation output, or perform final report aggregation
- **AND** it remains responsible only for normalized mention extraction and statistics.

### Requirement: Preprocess Mention Counts SHALL Be Merge Authority

The preprocess artifact MUST be the authoritative source for expected citation mention coverage during final merge.

#### Scenario: Merge validates against preprocess totals
- **WHEN** citation semantic parts are merged
- **THEN** the merge logic uses `citation_preprocess.json stats.total_mentions` as the expected mention count
- **AND** a mismatch causes merge failure instead of best-effort repair.
