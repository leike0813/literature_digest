# Tasks

- [x] Add a new active change for DB-owned render output directories and fixed result JSON mirroring
- [x] Extend `bootstrap_runtime_db` to persist `runtime_inputs.output_dir` and report it in stdout
- [x] Remove render-mode output-directory override behavior while keeping `fix|check` helper behavior unchanged
- [x] Mirror render stdout JSON to `./literature-digest.result.json`
- [x] Update `SKILL.md`, step-01/step-06 guidance, runtime interface docs, gate docs, and runner prompts
- [x] Add regression coverage for bootstrap output_dir persistence, render cwd fallback, render `--out-dir` rejection, and result-json mirroring
- [x] Validate with mypy, pytest, and `openspec validate --changes --json --no-interactive`
