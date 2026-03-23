# Codex Skill: Paper Digest + References + Citation Analysis

`literature-digest` 是一个后台自动化 skill。它读取本地论文源文件，输出：

- `digest.md`
- `references.json`
- `citation_analysis.json`
- `citation_analysis.md`

stdout 只返回一个 JSON 对象，主路径字段保持稳定，`citation_analysis_report_path` 为可选字段。

## Runtime Architecture

当前实现采用 SQLite + gate runtime：

- SQLite 是唯一过程真源：`<cwd>/.literature_digest_tmp/literature_digest.db`
- 所有中间结果先写库
- 不保留中间 JSON/MD 文件作为过程真源
- `scripts/gate_runtime.py` 是唯一合法 `next_action` 来源
- `scripts/stage_runtime.py` 是唯一阶段动作入口
- `scripts/runtime_db.py` 是唯一 DB 访问层与 render-context helper

状态机阶段固定为：

- `stage_0_bootstrap`
- `stage_1_normalize_source`
- `stage_2_outline_and_scopes`
- `stage_3_digest`
- `stage_4_references`
- `stage_5_citation`
- `stage_6_render_and_validate`
- `stage_7_completed`

## Skill Contract Layout

文档分层如下：

- `literature-digest/SKILL.md`
  - 精简但完整的主路径执行说明、项目统一参数词表、状态机、gate 纪律、LLM/脚本边界与公开输出约束
- `literature-digest/references/step_*.md`
  - 分阶段执行说明，只描述当前有效运行时结构与操作细则；按 gate `instruction_refs` 按需读取
- `literature-digest/references/sql_playbook.md`
  - SQL 模式与表职责
- `literature-digest/references/gate_runtime_interface.md`
  - `gate_runtime.py` 的 CLI 与 stdout payload 契约
- `literature-digest/references/stage_runtime_interface.md`
  - `stage_runtime.py` 的 subcommand 与输入输出接口
- `literature-digest/references/bibliography_formats.md`
  - references 体例判断与抽取启发

仓库级参考资料：

- `references/literature_digest_guidance_migration_map.md`
  - 文档迁移与内容归宿追溯
- `references/literature_digest_SKILL_legacy_snapshot.md`
  - 历史快照，仅用于追溯，不参与运行时

gate payload 会显式返回：

- `instruction_refs`
- `sql_examples`

因此 agent 以 `SKILL.md` 为主路径入口，先使用其中的统一参数词表理解脚本参数与 payload，再在当前阶段需要更多细则时，按 gate 指向的外置文档按需读取。

## Rendering System

最终产物通过模板系统生成：

- 模板位于 `literature-digest/assets/templates/`
- render context schema 位于 `literature-digest/assets/render_schemas/`

render 过程固定为：

1. 从 DB 读取数据并组装 render context
2. 用 `jsonschema` 校验 render context
3. 用 `jinja2` 渲染最终文件
4. 对 JSON 产物重新 parse 校验
5. 把公开产物登记到 `artifact_registry`

其中：

- digest 最终 Markdown 由 `digest_slots + digest_section_summaries` 渲染
- citation report 不再由 LLM 直写；`citation_analysis.json.summary` 来自 `citation_summary`，`citation_analysis.json.report_md` 与 `citation_analysis.md` 都由 renderer 从 `citation_summary + citation_items + citation_unmapped_mentions + citation_scope` 派生

## Runtime Layers

当前运行时按三层组织：

- `scripts/gate_runtime.py`
  - 读取 `workflow_state`
  - 生成 `next_action`、`instruction_refs`、`sql_examples`
- `scripts/stage_runtime.py`
  - 执行 `bootstrap_runtime_db`、`normalize_source`、`persist_outline_and_scopes`、`persist_digest`
  - 执行 `persist_references`、`prepare_citation_workset`、`persist_citation_semantics`、`persist_citation_summary`
  - 执行 `render_and_validate`
- `scripts/runtime_db.py`
  - 负责 schema 初始化、表级持久化、render context 构建、artifact registry 访问

约束：

- `citation_analysis.md` 必须与 `citation_analysis.json.report_md` 完全一致
- `citation_analysis.json` 必须包含顶层 `summary`
- `references.json` 的每个 item 至少含 `author/title/year/raw/confidence`
- 前序阶段一旦把决策写入 DB，后续主路径不得再通过 CLI / JSON 重新指定它

## Output Contract

stdout 必选字段：

- `digest_path`
- `references_path`
- `citation_analysis_path`
- `provenance.generated_at`
- `provenance.input_hash`
- `provenance.model`
- `warnings`
- `error`

stdout 可选字段：

- `citation_analysis_report_path`

## Notes For Future Changes

- 如果新增阶段或子流水线，必须同时更新：
  - `gate_runtime.py` 的 `instruction_refs`
  - `gate_runtime.py` 的 `sql_examples`
  - 对应 `references/step_*.md`
- 如果调整最终产物结构，必须同时更新：
  - `assets/templates/*`
  - `assets/render_schemas/*`
  - `stage_runtime.py`
  - 相应测试
