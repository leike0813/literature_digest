# 项目级 AGENTS（`literature-digest` / `literature-digest-lite`）

本文件仅包含本仓库两个 digest skill 的项目级约定，用于补充上级/全局 `AGENTS.md`；全局通用规则不在此重复。

---

## 1. 运行形态（后台自动化）

- 本仓库内的 digest skill 设计为后台自动化执行：运行过程中不得询问用户做决策。
- 任何分支或不确定性都应采用默认行为并继续执行，确保可批量运行、可重复。
- stdout 只允许输出一个 JSON 对象，不得夹杂日志、解释文本或多段输出。

---

## 2. 适用范围

本仓库当前包含两个相关 skill：

- `literature-digest`
  - SQLite-gated、stage-and-gate 主路径
  - 产出 `digest.md`、`references.json`、`citation_analysis.json`、`citation_analysis.md`
- `literature-digest-lite`
  - 简化版 digest-only 主路径
  - 只产出 `digest.md`

若任务明确针对其中一个 skill，应优先遵守对应 skill 目录内的 [SKILL.md](/home/joshua/Workspace/Code/Skill/literature_digest/literature-digest/SKILL.md) 或 [SKILL.md](/home/joshua/Workspace/Code/Skill/literature_digest/literature-digest-lite/SKILL.md)。

---

## 3. 输入约定

### `literature-digest`

- 从 prompt payload 中读取：
  - `source_path`
  - `language`
- `source_path` 是唯一内容来源。
- 输入可以是：
  - Markdown
  - PDF
  - 单文件 `.tex`
  - LaTeX 工程目录
  - 无扩展名文本文件
- `language` 若用户显式指定则直接使用；否则先从 prompt 主要语言推断；仅在无法稳定判断时回退 `zh-CN`。

### `literature-digest-lite`

- 从 prompt payload 中读取：
  - `md_path`
  - `language`
  - `output_dir`
- `md_path` 是唯一内容来源。
- 输入可以是：
  - Markdown
  - PDF
  - 单文件 `.tex`
  - LaTeX 工程目录
  - 无扩展名文本文件
- `language` 若用户显式指定则直接使用；否则先从 prompt 主要语言推断；仅在无法稳定判断时回退 `zh-CN`。

---

## 4. `literature-digest` 特有运行约束

- 在调用任何 skill 脚本之前，必须先在当前 shell 显式执行一次 `cwd()` / `pwd` 取得当前工作目录。
- 不得先 `cd` 到 skill 包目录或其它目录，再去捕获工作目录。
- 新 run 的第一步必须是 `confirm_runtime_paths`，先把：
  - `working_dir`
  - `tmp_dir`
  - `db_path`
  - `result_json_path`
  - `output_dir`
  固化到 SQLite。
- 之后才允许执行：
  - `bootstrap_runtime_db`
  - `persist_render_templates`
  - 以及后续 gate 返回的 `next_action`
- 正常主路径下，只能通过：
  - `scripts/gate_runtime.py`
  - `scripts/stage_runtime.py <next_action>`
  与数据库交互。
- 不要直接写 SQLite 表来伪造阶段完成；repair 场景之外不要把 SQL 当成主接口。

---

## 5. 输出约定

### `literature-digest`

stdout JSON 必须包含：

- `digest_path`
- `references_path`
- `citation_analysis_path`
- `provenance.generated_at`
- `provenance.input_hash`
- `provenance.model`
- `warnings`
- `error`

stdout JSON 可选包含：

- `citation_analysis_report_path`

公开产物固定文件名：

- `digest.md`
- `references.json`
- `citation_analysis.json`
- `citation_analysis.md`

补充约束：

- render 输出的文件路径字段应为绝对路径。
- 最终结果 JSON 会镜像写到 `literature-digest.result.json`。
- `citation_analysis` 的分析范围由当前 workflow 中持久化的 `citation_scope` 决定，不再固定为“仅第一章 Introduction”。

`references_path` 指向的 JSON 数组中，每条 reference item 必须包含：

- `author: string[]`
- `title: string`
- `year: number|null`
- `raw: string`
- `confidence: number`

扩展字段可尽量提取，缺失允许，例如：

- `DOI`
- `url`
- `arxiv`
- `publicationTitle`
- `pages`
- `volume`
- `issue`
- `itemType`
- `creators`
- `date`
- `ISBN`
- `ISSN`
- `publisher`
- `place`

不输出字段：

- `citationKey`

### `literature-digest-lite`

stdout JSON 必须包含：

- `digest_path`
- `provenance.generated_at`
- `provenance.input_hash`
- `warnings`
- `error`

公开产物固定文件名：

- `digest.md`

---

## 6. 默认行为（必须遵守）

### 共同规则

- 读取输入失败（不存在、无权限、编码异常、不可识别）时，返回 schema-compatible JSON，并填充 `error`。
- 不要因为局部解析失败而中止全部产物；只要主路径允许，就保留可审计的低置信结果和 warning。

### `literature-digest`

- 无法定位或稳定提取 references 时，可保留低置信 `raw` 条目，但不要伪造字段。
- references 或 citation 某一步失败时，必须遵守 gate / stage runtime 的错误返回，不要手工拼装看似成功的最终 JSON。
- 若 language 未显式给出，先看 prompt 语言；仅在无法稳定判断时回退 `zh-CN`。

### `literature-digest-lite`

- `output_dir` 未提供时，默认写到 `md_path` 所在目录。
- `language` 未显式给出时，先看 prompt 语言；仅在无法稳定判断时回退 `zh-CN`。

