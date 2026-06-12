## Context

`literature-analysis` is a SQLite-backed, automation-facing skill with six agent-facing stages. The current runtime already owns local algorithms and renderer assets, but recent live runs show three practical gaps: `analysis_runtime` imports can fail depending on how `run_analysis.py` is invoked, payload file read errors can escape as Python exceptions, and subagent draft quality depends too much on the main agent fixing field aliases after the fact.

The skill guidance must also remain portable. Repository-local verification uses `uv` and `$HOME/.ar`, but the skill package itself should not teach those machine-specific assumptions as the runtime contract.

## Goals / Non-Goals

**Goals:**

- Make `run_analysis.py` self-contained enough to run by script path without caller-managed `PYTHONPATH`.
- Preserve the current six-stage CLI and submit handlers.
- Keep validation as part of submit/gate behavior, not a separate user-visible stage.
- Make reference metadata aliases deterministic to normalize, with visible warnings.
- Improve JIT/subagent batch instructions so subagents return canonical fields by default.
- Keep skill docs current-state only and portable.

**Non-Goals:**

- Do not add a new `validate_payload` command.
- Do not change final artifact schemas or public filenames.
- Do not modify `literature-digest`.
- Do not try to automatically repair invalid JSON syntax.

## Decisions

- **Bootstrap imports in `run_analysis.py`.** The script inserts its own directory into `sys.path` before importing `analysis_runtime`. This fixes direct script invocation without imposing one required command shape.
- **Represent payload read failures as handler errors.** Payload file loading returns either a parsed object or a structured error payload. Invalid JSON is not normalized because missing escapes or delimiters are ambiguous.
- **Normalize only deterministic metadata aliases.** The runtime converts common aliases such as `journal` to `publicationTitle` and bare arXiv ids to `arXiv:<id>`. Unknown metadata fields are warning-worthy rather than blocking.
- **Move quality upstream into JIT contracts.** Prepare/status payloads expose batch ids, canonical field lists, forbidden fields, minimal examples, and merge guidance. The normalizer remains a fallback rather than the primary mechanism.

## Risks / Trade-offs

- **Risk: Unknown metadata fields might contain useful information.** Mitigation: preserve the current artifact schema behavior while surfacing `reference_metadata_field_unrecognized` warnings for main-agent review.
- **Risk: Additional JIT fields increase prepare payload size.** Mitigation: add concise contracts and examples per batch, not full duplicated source text.
- **Risk: Some invocation forms are impossible to support.** Mitigation: document recommended bare-Python commands without claiming hyphenated package module paths work.
