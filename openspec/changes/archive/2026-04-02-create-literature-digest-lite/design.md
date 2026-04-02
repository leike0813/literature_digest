## Context

主 skill `literature-digest` 采用 SQLite-gated runtime 和复杂的状态机流程（7 个阶段），适合需要完整 citation analysis 和 references 抽取的场景。但部分用户只需要快速的 paper digest 生成，不需要复杂的 references 处理和 citation 分析。

当前项目结构：
- `literature-digest/`: 主 skill，包含完整的 SQLite-gated runtime
- `assets/templates/`: digest 模板文件（zh-CN 和 en-US）
- `scripts/`: 核心执行脚本

用户需求：提供一个轻量级的 digest 生成选项，保持与主 skill 完全一致的 digest 输出质量，但简化执行流程和输出 schema。

## Goals / Non-Goals

**Goals:**
- 创建独立的 `literature-digest-lite` skill 包
- 复用主 skill 的 digest 模板文件
- 保持 digest 输出结构与主 skill 完全一致（章节标题、篇幅要求、内容要求）
- 简化执行流程：移除 SQLite-gated runtime，移除 references 抽取，移除 citation analysis
- 简化输出 JSON schema：仅包含 digest_path 和 provenance
- 支持多种输入格式（Markdown、PDF、LaTeX）
- 支持任意 language 参数，en/zh 直接复制模板，其他语言由 agent 翻译

**Non-Goals:**
- 不修改主 skill 代码
- 不引入新的依赖
- 不支持独立的 references 抽取功能
- 不支持 citation analysis 功能
- 不支持复杂的 SQLite-gated 状态机流程

## Decisions

### Decision 1: 目录结构
**选择**: 在项目根目录创建 `literature-digest-lite/` 子目录，包含 assets/、scripts/、SKILL.md

**理由**: 
- 与主 skill 目录结构保持一致，便于维护
- 独立的 SKILL.md 文档，整合所有指令（不需要 references 目录）
- 复用主 skill 的模板文件（通过复制）

**替代方案**: 
- 方案 B: 在主 skill 目录下创建 lite 子目录 → 拒绝，因为 lite skill 是独立的 skill 包
- 方案 C: 仅创建一个脚本文件 → 拒绝，因为需要完整的 skill 结构（模板、文档）

### Decision 2: 执行模式
**选择**: run_digest.py 支持两种模式：`--mode normalize` 和 `--mode render`

**理由**:
- normalize 模式：负责输入标准化，输出 normalized_text 和 input_hash
- render 模式：负责读取 digest_slots + section_summaries，渲染最终 digest.md
- 两阶段设计符合主 skill 的职责边界（脚本不负责 LLM 生成）

**替代方案**:
- 方案 B: 单一模式，一步完成 → 拒绝，因为 LLM 生成需要 agent 介入
- 方案 C: 三阶段（normalize → translate → render）→ 拒绝，模板翻译由 agent 负责，不需要独立模式

### Decision 3: 语言处理
**选择**: language 可以是任意字符，en/zh 直接复制模板，其他语言由 agent 翻译

**理由**:
- 与主 skill 保持一致的语言处理逻辑
- en/zh 是最常用语言，直接复制模板效率高
- 其他语言由 agent 翻译，保持灵活性
- 翻译原则：仅翻译固定标题文本，保留 Jinja2 语法

**替代方案**:
- 方案 B: 仅支持 en/zh 两种语言 → 拒绝，限制了用户选择
- 方案 C: 脚本自动翻译（调用 LLM API）→ 拒绝，违反"脚本禁止调用外部 LLM API"的原则

### Decision 4: 输出目录
**选择**: digest.md 输出到 source_path 所在目录

**理由**:
- 简化设计，不需要额外的--output-dir 参数
- 符合 lite skill 的简化理念

**替代方案**:
- 方案 B: 支持--output-dir 参数 → 拒绝，增加复杂度，lite skill 优先简化

### Decision 5: Digest 生成细则
**选择**: SKILL.md 中整合完整的 Digest 生成细则，与主 skill 完全一致

**理由**:
- lite skill 不需要 references 目录，所有指令整合到 SKILL.md
- 保持与主 skill 完全一致的 digest 输出质量
- 包括：输出结构、payload 契约、映射关系、失败语义、合法/非法示例

## Risks / Trade-offs

### Risk 1: 代码重复
**风险**: 输入标准化逻辑与主 skill 重复（LaTeX 解析、PDF 处理）

**缓解**: 
- 未来可以考虑提取为共享库
- 当前优先保证 lite skill 的独立性

### Risk 2: 模板同步
**风险**: 主 skill 模板更新时，lite skill 模板可能不同步

**缓解**:
- 建立模板同步机制（如 git submodule 或同步脚本）
- 当前通过手动复制保持同步

### Risk 3: 文档维护
**风险**: SKILL.md 整合所有内容，文档较长（315 行），维护成本高

**缓解**:
- 使用清晰的章节结构
- 定期审查和更新

### Trade-off: 简化 vs 功能
**权衡**: lite skill 牺牲了 references 抽取和 citation analysis 功能，换取简化的执行流程

**理由**: 目标用户只需要快速的 digest 生成，不需要复杂功能
