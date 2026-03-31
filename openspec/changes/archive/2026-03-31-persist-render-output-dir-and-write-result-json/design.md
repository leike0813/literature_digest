# Design

## Bootstrap-owned output directory

`bootstrap_runtime_db` gains an optional `--output-dir` argument and always writes one normalized directory path into `runtime_inputs.output_dir`.

Rules:

- If `--output-dir` is present, store its normalized absolute path.
- If it is absent, store the current working directory.
- Later stages never re-decide this directory.

The bootstrap stdout payload will include the chosen `output_dir` so callers can audit what became authoritative.

## DB-authoritative render output

`render_and_validate --mode render` will no longer accept output-directory override input.

Render output resolution becomes:

1. Read `runtime_inputs.output_dir`
2. If missing or empty, use `Path.cwd()`

Fixed filenames remain unchanged:

- `digest.md`
- `references.json`
- `citation_analysis.json`
- `citation_analysis.md`

`artifact_registry` and the final stdout payload continue to report the actual written paths.

`render_and_validate --mode fix|check` keeps its existing utility-only `--out-dir` behavior.

## Fixed stdout mirror file

After render mode produces its final stdout-compatible JSON object, the runtime writes the exact same object to:

- `./literature-digest.result.json`

The file location is intentionally hard-coded to the current working directory and is not stored in DB. It is an execution-sidecar for orchestration, not a public artifact.

The same mirror behavior applies to schema-compatible render failure payloads so automation always has one stable result file to inspect.

## Guidance alignment

Guidance changes are documentation-only:

- Step 1 explains that output directory ownership starts at bootstrap.
- Step 6 explains that render consumes DB state only and writes `literature-digest.result.json`.
- Gate `execution_note` highlights output-dir persistence at bootstrap and DB-authoritative render behavior at stage 6.
