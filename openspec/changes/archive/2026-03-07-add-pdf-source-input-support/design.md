## Context

`literature-digest` 的下游流程已经围绕 Markdown 建立起来：digest、大纲、references 抽取、citation preprocess 与 validate 都默认输入是一份可读取的 Markdown。为了支持 PDF，最稳妥的方式不是让每个下游阶段感知 PDF，而是在最前面增加一个统一入口，把原始输入先标准化成固定路径的 Markdown。

当前实现已经采用了这一思路，但缺少对应的 OpenSpec 设计记录。

## Goals / Non-Goals

**Goals:**
- 让 skill 接受单一 `source_path` 输入，支持 Markdown、PDF 和无扩展名文件
- 用 dispatcher 统一输入探测与标准化，确保下游继续只处理 Markdown
- 在 `pymupdf4llm` 不可用或失败时，仍然通过标准库兜底解析维持流程可运行
- 保持 stdout/output contract 基本稳定，仅更新输入语义和文档

**Non-Goals:**
- 不引入外部 DL 推理服务或 OCR 服务
- 不重写 digest / references / citation semantics 的主体逻辑
- 不把标准库 fallback 做成高保真的 PDF 版面恢复器

## Decisions

1. Single source contract
- Decision: 输入统一改为 `source_path`，不再区分 `md_path` / `pdf_path`
- Rationale: 调用方接口最简，且更适合处理无扩展名输入
- Alternative considered: 同时保留 `md_path` 与 `pdf_path`
- Why not: 会把分支复杂度暴露给调用方和下游文档

2. Content sniffing over extension
- Decision: dispatcher 先看文件头 `%PDF-`，否则尝试 UTF-8 文本读取，扩展名只用于 warning
- Rationale: skill-runner 下输入文件经常无扩展名，扩展名本身不可靠
- Alternative considered: 仅按扩展名判断
- Why not: 无法覆盖 extensionless 输入，也容易被伪装扩展名误导

3. Normalize all inputs to one markdown path
- Decision: 无论源输入为何，都统一生成 `<cwd>/.literature_digest_tmp/source.md`
- Rationale: 让下游所有脚本和 LLM 步骤不需要感知输入类型
- Alternative considered: Markdown 走原文件，PDF 才产出临时 Markdown
- Why not: 会让参数语义和路径处理在下游分叉

4. PDF conversion strategy
- Decision: PDF 主路径使用 `pymupdf4llm`，失败时用标准库文本兜底
- Rationale: `pymupdf4llm` 能尽量保留结构；标准库兜底保证在依赖缺失时仍可运行
- Alternative considered: 只依赖第三方解析器，或直接失败
- Why not: skill 执行环境不稳定时会显著降低可用性

5. Provenance hash semantics
- Decision: `provenance.input_hash` 对原始 `source_path` 文件 bytes 计算
- Rationale: 同一输入 PDF 不因转换器升级而改变输入哈希
- Alternative considered: 对标准化后的 `source.md` 计算
- Why not: 会把解析器版本波动混入输入身份

## Risks / Trade-offs

- [Risk] 标准库 fallback 对多栏、公式、表格 PDF 的质量有限
- Mitigation: 明确把 fallback 定位为“文本保底”，并在 warnings 中显式告警

- [Risk] 直接修改主 specs 后再补 change，未来 archive 可能出现“记录的是已存在行为”
- Mitigation: 在 proposal/specs 中明确说明这是补录 change，用于追溯这次已落地的修改

- [Risk] `pymupdf4llm` 是新增依赖，某些环境可能无法安装
- Mitigation: 将其视为可选依赖，并保证缺失时不会导致整个 skill 崩溃

- [Risk] dispatcher 增加了入口复杂度
- Mitigation: 把所有格式判断集中到单一脚本，避免复杂度渗透到下游脚本
