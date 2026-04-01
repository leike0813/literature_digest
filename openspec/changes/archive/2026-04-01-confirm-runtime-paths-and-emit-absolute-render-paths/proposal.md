# Change Proposal: confirm-runtime-paths-and-emit-absolute-render-paths

## Why

Different agents do not always agree on the effective working directory. Some agents `cd` into the skill package root before running any script, which causes runtime paths, temp files, and final result mirrors to be written into the wrong directory. The current startup flow also lets render emit relative or cwd-derived paths when directory state is incomplete.

## What Changes

- Add a new startup action `confirm_runtime_paths` before bootstrap.
- Require the runtime path set to be captured from the shell cwd and persisted to SQLite before other skill scripts run.
- Move directory ownership out of `bootstrap_runtime_db`.
- Make final render path fields absolute.
- Make the render result mirror file path DB-authoritative via `runtime_inputs.result_json_path`.

## Impact

- Main-path startup becomes: shell `pwd` -> `confirm_runtime_paths` -> `bootstrap_runtime_db`.
- Final stdout JSON continues to use the same field names, but emitted paths become absolute.
- Legacy DBs remain compatible through fallback path resolution.
