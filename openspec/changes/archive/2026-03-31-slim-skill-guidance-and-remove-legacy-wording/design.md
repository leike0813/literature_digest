# Design

## Documentation Scope

This change only updates active guidance and the tests that validate it.

Target files:

- `literature-digest/SKILL.md`
- `literature-digest/references/step_03_digest_generation.md`
- `literature-digest/references/stage_runtime_interface.md`
- `literature-digest/references/step_06_render_and_validate.md`
- `docs/dev_paper_digest_skill.md`
- related guidance tests

## SKILL.md slimming

Each stage section in `SKILL.md` keeps the current execution structure:

- 何时执行
- 调用命令
- 必须提供的参数 / payload
- 字段含义
- 最小合法示例
- 完成后 gate 结果

The trailing `本步最常见错误` block is removed from every step.

## Legacy wording removal

Active guidance should describe only the current contract. Historical comparison wording is replaced with positive contract wording:

- “本步只接受 …”
- “本步 payload 包含 …”
- “缺少这些字段会失败”
- “最终渲染由 … 派生”

Historical traceability documents may remain in the repository, but they should not be presented as runtime reading material for agents.
