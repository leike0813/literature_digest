# Design

## Overview

本次变更不引入新的公开阶段，也不改变最终 stdout schema。核心策略是把 LaTeX 输入在 step 1 规范化为一个可审阅的 `source.md`：

- `.tex` 原文放入 ` ```tex ` fence
- 工程目录展平后的 tex 放入 ` ```tex ` fence
- `.bib` 原文追加到末尾的 ` ```bibtex ` fence

这样后续 LLM 和现有 stage 4/5 可以直接消费原始 tex / bib 内容，而不需要额外的 LaTeX-to-Markdown 语义转换层。

## References Handling

- `\bibitem{...}` bibliography：按 `\bibitem` 起点切条
- `bibtex` fence：按顶层 `@type{key,` 起点切条
- `.bib` 条目增加 deterministic field parsing，直接抽取 `author/title/year/container`

## Citation Handling

- 支持 `\cite{...}`、`\citep{...}`、`\citet{...}` 和多 key 形式
- 优先按 citekey / bibitem key 映射到 `reference_items`
- author-year / numeric 逻辑作为兜底
