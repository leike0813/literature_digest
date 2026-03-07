## Why

`literature-digest` 已经实现了 `source_path + dispatcher + PDF fallback`，但这些修改是在未创建 OpenSpec change 的情况下直接落到主线 specs 与实现里的，缺少可追溯的变更记录。需要补一条 change，把这次输入契约和预处理架构的演进正式记录下来。

## What Changes

- 将 skill 输入契约从 `md_path` 扩展为统一 `source_path`
- 增加 dispatcher，基于文件内容而非扩展名探测输入格式
- 无论输入是 Markdown 还是 PDF，都统一生成 `<cwd>/.literature_digest_tmp/source.md`
- PDF 主路径使用 `pymupdf4llm` 转 Markdown，失败时降级到 Python 标准库兜底解析
- `provenance.input_hash` 改为对原始 `source_path` 计算
- 更新相关文档、脚本接口与测试，保证行为与契约一致

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `literature-digest`: 输入契约、输入归一化流程、输出物化目录语义从 `md_path` 演进到 `source_path`
- `citation-preprocess-pipeline`: 预处理阶段改为消费 dispatcher 统一生成的标准化 Markdown，而不是假定上游直接提供 Markdown 文件

## Impact

- Affected code:
  - `literature-digest/assets/input.schema.json`
  - `literature-digest/assets/runner.json`
  - `literature-digest/scripts/dispatch_source.py`
  - `literature-digest/scripts/provenance.py`
  - `literature-digest/scripts/validate_output.py`
- Affected docs:
  - `literature-digest/SKILL.md`
  - `README.md`
  - `docs/dev_paper_digest_skill.md`
  - `docs/dev_overview.md`
- Affected specs:
  - `openspec/specs/literature-digest/spec.md`
  - `openspec/specs/citation-preprocess-pipeline/spec.md`
- Dependency impact:
  - add optional runtime dependency `pymupdf4llm`
