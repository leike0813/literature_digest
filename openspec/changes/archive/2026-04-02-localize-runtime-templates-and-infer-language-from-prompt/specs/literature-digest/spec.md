## ADDED Requirements

### Requirement: Runtime Markdown Templates SHALL Be Persisted Before Normalization

The skill SHALL persist run-specific digest and citation Markdown templates into the runtime tmp directory before source normalization proceeds.

#### Scenario: Bootstrap advances to runtime template persistence

- **WHEN** `bootstrap_runtime_db` succeeds
- **THEN** the next main-path action is `persist_render_templates`
- **AND** normalization does not proceed until runtime template paths are persisted

### Requirement: Render SHALL Use DB-Backed Runtime Templates

The final render step SHALL load digest and citation Markdown templates only from the runtime template paths persisted in SQLite for new runs.

#### Scenario: Runtime templates are present

- **WHEN** `render_and_validate --mode render` runs for a new workflow that completed `persist_render_templates`
- **THEN** digest Markdown is rendered from `runtime_inputs.digest_template_path`
- **AND** citation Markdown report is rendered from `runtime_inputs.citation_analysis_template_path`

### Requirement: Language Choice SHALL Prefer Prompt Inference Over Immediate zh-CN Default

The skill guidance SHALL state that missing explicit language input is resolved by prompt-language inference before any compatibility fallback to `zh-CN`.

#### Scenario: Prompt does not include explicit target language

- **WHEN** the agent starts a new run without an explicit language override
- **THEN** guidance instructs it to infer the target language from the prompt first
- **AND** only fall back to `zh-CN` if that inference is unstable
