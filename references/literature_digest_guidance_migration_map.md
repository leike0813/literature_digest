# Guidance Migration Map

本文件用于追踪：长版 `SKILL.md` 中的详细内容在重构后的仓库中落到了哪里。

## 迁移原则

- `SKILL.md` 只保留核心执行契约与导航索引
- 原长版 `SKILL.md` 的详细内容不得丢失
- 每个原段落要么保留在 `SKILL.md`，要么完整迁移到外置文档
- 外置文档是承接原内容，不是摘要替代

## 段落迁移表

| 长版 `SKILL.md` 段落 | 现归宿 |
| --- | --- |
| `输入（prompt payload）` | `step_01_bootstrap_and_source.md` |
| `输出`、`stdout 输出格式`、`输出物化` | `step_06_render_and_validate.md`、`rendering_contracts.md` |
| `reference 文件格式` | `step_04_references_extraction.md`、`rendering_contracts.md` |
| `citation_analysis 输出格式`、`items 数组中条目的最小结构`、`report_md 建议结构` | `step_05_citation_pipeline.md`、`rendering_contracts.md` |
| `处理步骤（建议工作流）` | `step_01` 到 `step_06` 分拆承接 |
| `隐藏分阶段产物流水线（强制）` 与 staged 规则 | `step_02_outline_and_scopes.md`、`step_04_references_extraction.md`、`step_05_citation_pipeline.md` |
| `LLM 与脚本的职责边界（重要）` | `SKILL.md` 核心保留，并在 `step_01` / `step_05` / `step_06` 细化 |
| `文献 Digest 总结细则` 与 `Digest 模版` | `step_03_digest_generation.md`、模板注释、`rendering_contracts.md` |
| `参考文献抽取细则` 与 5 个示例 | `step_04_references_extraction.md` |
| `Citation Analysis（Dynamic Citation Scope）细则` | `step_05_citation_pipeline.md` |
| `默认行为协议（必须遵守）` | `step_01_bootstrap_and_source.md`、`step_06_render_and_validate.md` |
| `脚本（可选但推荐）` 及各脚本说明 | `step_01` / `step_04` / `step_05` / `step_06` |

## 当前需要读取的文档

- 若是阶段执行：优先读对应 `step_*.md`
- 若是模板与结构：读 `rendering_contracts.md`
- 若是 SQL 示例背景：读 `sql_playbook.md`
- 若是参考文献体例判断：读 `bibliography_formats.md`
