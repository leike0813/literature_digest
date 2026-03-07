# literature-digest

用于从输入源文件（`source_path`，可为 Markdown、PDF 或无扩展名文件）生成：
- `digest`：中文/英文（`zh-CN`/`en-US`）论文摘要 Markdown
- `references`：结构化参考文献条目（JSON 数组）
- `citation_analysis`：仅基于第一章 Introduction 的引文分析（JSON 对象，支持 numeric 与 author-year）

## 输入

以 `$literature-digest` 调用，并从 prompt 中读取：
- `source_path`：待解析论文输入路径；格式按文件内容探测
- `language`：论文总结语言，`zh-CN`（默认）或 `en-US`

## 输出（stdout）

stdout 仅输出一个 JSON 对象（`literature_digest_v1`），为避免截断只回传文件路径：
- `digest_path`：Markdown 文件路径
- `references_path`：JSON 文件路径（数组）
- `citation_analysis_path`：JSON 文件路径（对象）

运行时会先统一生成 `<cwd>/.literature_digest_tmp/source.md`，后续流程都只消费这份标准化 Markdown。
结果文件默认写入原始输入 `source_path` 所在目录，文件名固定为 `digest.md`、`references.json`、`citation_analysis.json`。

更多细节见 `SKILL.md`。 
