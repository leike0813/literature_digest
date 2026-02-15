# 项目级 AGENTS（literature-digest / `$literature-digest`）

本文件仅包含 **literature-digest** skill 项目特有约定，用于补充上级/全局 `AGENTS.md`；全局通用规则不在此重复。

---

## 1. 运行形态（后台自动化）

- 本 skill 设计为后台自动化执行：运行过程中**不得询问用户做决策**。
- 任何分支/不确定性必须采用默认行为并继续执行，确保可批量运行、可重复。
- stdout **仅允许输出一个 JSON 对象**（不得夹杂日志/解释文本/多段输出）。

---

## 2. 输入约定（prompt 内 payload）

- 本 skill 以 `$literature-digest` 被调用。
- 从 prompt 中读取：
  - `md_path`：待解析的论文 Markdown 文件路径。（唯一内容来源，skill 自行读取该文件）
  - `language`： 论文总结使用的语言。（支持 `zh-CN`/`en-US`，默认 `zh-CN`）

---

## 3. 输出约定（schema 硬约束）

输出 JSON 必须包含（即使为空也要存在）：
- `digest_path`（输出文件路径；内容为 Markdown 纯文本；**不包含**插件侧协议头）
- `references_path`（输出文件路径；内容为 UTF‑8 JSON 数组）
- `provenance.generated_at`（UTC ISO‑8601）
- `provenance.input_hash`（建议 `sha256:<hex>`，对 `md_path` 文件内容计算）
- `warnings`（数组）
- `error`（`object|null`）

`references_path` 指向的 JSON 数组中，每条 reference item 必须包含：
- `author: string[]`
- `title: string`
- `year: number|null`
- `raw: string`
- `confidence: number`（0~1）

扩展字段（尽量提取，缺失允许）：
- `DOI/url/arxiv/publicationTitle/pages/volume/issue`
- `itemType/creators/date/ISBN/ISSN/publisher/place`（尽量对齐 Zotero 字段）

不输出字段：
- `citationKey`（由 Better BibTeX 负责）

---

## 4. 默认行为（必须遵守，不可交互询问）

- 读取 `md_path` 失败（不存在/无权限/编码异常）：返回 schema 兼容 JSON，并填充 `error`；`digest_path=""`，`references_path=""`。
- 无法定位参考文献章节：`references_path=""`（digest 可正常生成；仍需生成 `digest_path`）。
- 存在多个“References/参考文献”候选章节：默认选择“最后一个且长度合理”的章节。
- 分割条目失败或字段抽取不可靠：保留 `raw`，输出 `author=[]`、`title=""`、`year=null`，并将 `confidence` 置低值。
- `language` 非支持值：默认回退 `zh-CN`（只影响 digest 输出语言）。

---

## 5. 防串单对齐（必须回显）

响应必须回显：
 - `md_path`
 - `language`

调用方会用它们做一致性校验；不一致将导致写回被拒绝。
