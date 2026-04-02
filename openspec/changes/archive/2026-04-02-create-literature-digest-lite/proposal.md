## Why

主 skill `literature-digest` 采用 SQLite-gated runtime 和复杂的状态机流程，适合需要完整 citation analysis 和 references 抽取的场景。但部分用户只需要快速的 paper digest 生成，不需要复杂的 references 处理和 citation 分析。`literature-digest-lite` 通过简化设计，提供更轻量级的 digest 生成能力，同时保持与主 skill 完全一致的 digest 输出质量。

## What Changes

- **新增** `literature-digest-lite` skill 包，位于项目根目录 `literature-digest-lite/`
- **新增** 简化版执行脚本 `run_digest.py`，支持 `normalize` 和 `render` 两种模式
- **复用** 主 skill 的 digest 模板（`digest.zh-CN.md.j2` 和 `digest.en-US.md.j2`）
- **新增** 完整的 SKILL.md 文档，包含 Digest 生成细则（与主 skill 完全一致）
- **简化** 执行流程：移除 SQLite-gated runtime，移除 references 抽取，移除 citation analysis
- **保持** digest 输出结构与主 skill 完全一致（章节标题、篇幅要求、内容要求）

## Capabilities

### New Capabilities

- `lite-skill`: literature-digest-lite skill 的完整规范，包括输入输出契约、执行流程、LLM 与脚本职责边界、Digest 生成细则

### Modified Capabilities

<!-- 无修改现有能力 -->

## Impact

- **代码影响**: 新增独立的 skill 包，不修改主 skill 代码
- **依赖影响**: 复用主 skill 的模板文件和输入标准化逻辑（`pymupdf4llm`、LaTeX 解析）
- **用户影响**: 提供一个更轻量的 digest 生成选项，输出 JSON schema 简化（仅 `digest_path` 和 `provenance`）
- **向后兼容**: 完全兼容，不影响现有 `literature-digest` skill
