# Design

## Runtime State Lifecycle

`runtime_errors` and `runtime_warnings` remain append-friendly audit tables, but
active state becomes explicit. Final payload construction reads only active
errors and active warnings. Successful stage actions resolve active errors from
the same stage/code family so a recovered run cannot finish with a stale error.

The stdout schema is not extended. Warning readability is improved by rendering
category-level strings such as `reference_pattern_ambiguous: 44 entries` instead
of one entry per warning instance.

## Repair API

`stage_runtime.py repair_db_state --db-path ...` is the supported recovery entry
point. It performs only safe repairs:

- fill missing `input_hash` when `source_path` exists
- resolve stale active errors when downstream receipts prove success
- restore workflow state from completed receipts

The gate still includes repair guidance, but it must expose a normal command
example for this action.

## Reference Split Hardening

Reference boundary detection must require actual reference-start evidence.
Venue fragments such as `In Proceedings ...`, plain `Proceedings ...`, pages
phrases, and initials must not independently start a new reference.

Split review payloads may include `review_generation_id`. The runtime reports
the current generation and rejects stale generations when present. A new
`force_keep` resolution lets the agent confirm a false-positive suspect block
without re-entering split review.

## Execution Experience

`persist_render_templates` auto-copies repository templates for `zh-*` and
`en-*` languages when no payload file is provided. Other target languages still
require translated templates through `--payload-file`.

All script-facing JSON files use UTF-8. Documentation and gate examples keep
`--payload-file` as the primary path for sizeable JSON payloads; stdin remains a
compatibility fallback only.
