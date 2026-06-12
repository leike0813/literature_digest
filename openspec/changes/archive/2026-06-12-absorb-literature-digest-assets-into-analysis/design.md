## Context

`literature-analysis` currently exposes a better workflow, but most behavior is implemented by subprocess calls into `literature-digest/scripts/stage_runtime.py`. That keeps tests green but does not make the new skill independent.

The old runtime is a 7k-line monolith. Fully copying it at once would create high regression risk. This change absorbs it by domain boundaries while keeping behavior compatible.

## Decisions

### Decision 1: Guidance is rewritten, not copied

The new references are short, stage-oriented documents that preserve the old rules but remove gate-only phrasing. `gate_runtime_interface.md` and `sql_playbook.md` are intentionally not exposed to agents for the new skill.

### Decision 2: Remove subprocess coupling before full code copy

New `analysis_runtime` modules directly import legacy functions where necessary. This is still a dependency, but it avoids CLI subprocess orchestration and gives each domain a stable local module boundary.

### Decision 3: Keep render as compatibility fallback

Rendering remains compatible with the old renderer in this phase. The new `rendering.py` module owns that fallback so `run_analysis.py` no longer embeds legacy subprocess knowledge for finalization.

### Decision 4: Metadata enrichment fallback remains explicit

Reference metadata enrichment can still use conservative fallback when no enrichment payload is supplied, but docs frame it as a recovery path rather than the preferred main path.

## Risks

- Imported legacy private functions can change. Tests cover source normalization, reference workset preparation, citation workset preparation, and final compatibility to detect drift.
- New guidance may omit useful old edge cases. The first pass prioritizes agent usability and avoids importing old gate complexity.
