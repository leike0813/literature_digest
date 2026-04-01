# Design: confirm-runtime-paths-and-emit-absolute-render-paths

## Overview

This change introduces an explicit runtime-path confirmation step before bootstrap. The goal is to stop all later path decisions from depending on whichever directory the agent happens to be in when it eventually calls a skill script.

## Runtime Path Model

The first persisted directory set is:

- `working_dir`
- `tmp_dir`
- `db_path`
- `result_json_path`
- `output_dir`

New runs persist these values through `confirm_runtime_paths`. Later runtime steps read them from SQLite.

## Startup Flow

1. Agent captures the shell cwd with `cwd()` / `pwd`.
2. Agent calls `confirm_runtime_paths --working-dir <captured-cwd> [--output-dir ...]`.
3. Agent reruns gate using the confirmed DB path.
4. Gate advances to `bootstrap_runtime_db`.

## Compatibility

- Gate and docs treat `confirm_runtime_paths` as the required startup action for new runs.
- Direct `bootstrap_runtime_db` remains backward-compatible by deriving the runtime path set from the explicit DB path when no confirmed path receipt exists.
- Render keeps fallback behavior for legacy DBs that do not yet contain the new runtime path keys.

## Render Path Contract

- Public artifacts are written under DB-backed `output_dir`.
- The result mirror file is written to DB-backed `result_json_path`.
- Final stdout JSON path fields are absolute.
