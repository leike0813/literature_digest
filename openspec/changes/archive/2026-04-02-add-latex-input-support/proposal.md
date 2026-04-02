# add-latex-input-support

## Why

`literature-digest` 目前只能稳定处理 Markdown / PDF / 普通 UTF-8 文本。很多论文实际来源是单文件 `.tex` 或 LaTeX 工程目录；当前 skill 无法把这类输入规范化到现有 stage 2-6 流水线中。

## What Changes

- 扩展 step 1 输入协议，支持单文件 `.tex` 与 LaTeX 工程目录。
- `normalize_source` 对 LaTeX 输入采用 fenced raw source 策略，不做重型语义转写。
- stage 4 增加 `\bibitem` 与 `bibtex` references splitting。
- stage 5 增加 LaTeX citation commands 与 citekey 映射。
- 同步文档、schema 与测试。
