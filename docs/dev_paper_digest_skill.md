# Codex skill：论文 Digest + References 抽取（literature_digest_v1）

本 skill 用于在本机 `codex exec` 场景下，读取 MinerU 解析得到的论文 Markdown（`.md` 文件路径由 Zotero 插件提供），并输出：

1) 中文 digest（Markdown）
2) 参考文献条目列表（结构化 JSON；至少 `author[]/title/year`）

> 本 skill 是“可靠性中心”：Zotero 插件只传路径，不做任何正文预处理与抽取规则。

---

## 0. 目标与非目标

### 0.1 目标

- 输入只有一个 `.md` 路径（来自 MinerU 解析结果），尽可能稳定地产出：
  - digest：可直接写入 Zotero note
  - references：可用于后续“文献匹配组件”继续做 citekey 匹配/递归入库
- 输出必须是**严格 JSON**（stdout 仅输出 JSON，不夹杂解释/日志）。
- 批量场景下必须可校验不串单：响应需要包含 `digest_path`/`references_path`，并保证 `md_path`/`language` 调用一致性。
- 本 skill 用于后台自动化：运行过程中**不得询问用户做决策**；遇到分支必须采用文档约定的默认行为并继续执行，保证可批处理。
  - 协议头/幂等标识由 Zotero 插件负责写入 note；skill 输出的 `digest` 必须保持为纯 Markdown 文本（可直接渲染）。
  - 为避免 stdout 截断，skill 不直接在 stdout 输出 `digest`/`references` 正文；而是将其写入**输入文档 `md_path` 所在目录**下的固定文件名，并在 stdout JSON 中回传路径。

### 0.2 非目标

- 不负责生成/校验 citekey（citekey 的唯一性由用户维护）。
- 不负责文献库匹配（后续由 `docs/dev_literature_match_skill.md` 的匹配组件处理）。
- 不负责写回 Zotero（由 Zotero 插件执行）。

---

## 0.3 后台自动化默认行为（必须遵守）

本 skill 在后台运行时必须“自决策”，不得向用户提问。遇到以下分支时的默认行为如下：

- `md_path` 不存在/无法读取：返回 JSON，填充 `error`，`digest_path=""`，`references_path=""`。
- 参考文献章节定位失败：`references_path=""`（允许 digest 仍正常生成；仍需生成 `digest_path`）。
- 找到多个“References/参考文献”候选章节：默认选择“最后一个”且长度合理的章节。
- 条目分割失败或字段抽取不稳定：保留 `raw`，`author=[]`、`title=""`、`year=null`，并将 `confidence` 置低值。
- `language` 不是支持值：默认退回 `zh-CN`（只影响 digest 输出语言）。

---

## 1. 输入契约（prompt payload）

本 skill 以 `$literature-digest` 的形式被调用。Zotero 插件会把输入 payload 直接嵌入到 prompt 中（不传正文），例如：

````text
$literature-digest 请按以下输入执行解析：
```json
{ ...payload json... }
```
````

skill 端约定：从 prompt 中读取 **第一个 fenced `json` code block**，其内容即为输入 payload。

payload 字段极简只包含：

```json
{
  "md_path": "C:\\\\Zotero\\\\storage\\\\XXXX\\\\paper.md",
  "language": "zh-CN"
}
```

约束：
- `md_path` 是唯一内容来源；skill 必须自行读取文件（UTF‑8）。
- `language` 支持：
  - `zh-CN`（默认）
  - `en-US`
  不支持值回退 `zh-CN`（只影响 digest 输出语言，不影响 references 结构）。

---

## 2. 输出契约（response.json）

### 2.1 总体约束（非常重要）

- stdout **只能**输出 JSON（单个对象），不得输出多余文本。
- 输出对象必须包含下列字段（即使为空也要存在）：
  - `digest_path`（输出文件路径；文件内容为 Markdown 纯文本；不包含插件侧协议头）
  - `references_path`（输出文件路径；文件内容为 UTF‑8 JSON 数组）
  - `provenance.generated_at`
  - `provenance.input_hash`
  - `warnings`（数组）
  - `error`（`object|null`）

### 2.2 示例

```json
{
  "digest_path": "C:\\\\Zotero\\\\storage\\\\XXXX\\\\digest.md",
  "references_path": "C:\\\\Zotero\\\\storage\\\\XXXX\\\\references.json",
  "provenance": {
    "generated_at": "2026-01-17T12:34:56Z",
    "input_hash": "sha256:..."
  },
  "warnings": [],
  "error": null
}
```

### 2.3 references 的硬约束

`references_path` 指向的 JSON 数组中，每一条 reference item：
- 必须包含：`author`（`string[]`）、`title`（`string`）、`year`（`number|null`）、`raw`（`string`）、`confidence`（`0~1`）
- 允许缺失：`DOI/url/arxiv/publicationTitle/pages/volume/issue` 等扩展字段
- 不输出：`citationKey`（由 Better BibTeX 负责）

> 当无法可靠抽取 `author/title/year` 时，仍需输出：
> - `raw` 保留原始条目
> - `author=[]`、`title=""`、`year=null`
> - `confidence` 设置为低值（例如 `0.1`）

---

## 3. 处理流程（推荐实现）

### 3.1 读入与审计

1) 从 prompt 中提取并解析 payload JSON（第一个 fenced `json` code block）
2) 读取 `md_path` 文件内容（UTF‑8）
3) 计算 `input_hash = sha256(file_bytes)`（以文件内容为准）
4) 生成 `generated_at`（UTC ISO‑8601）

### 3.2 Digest 生成（中文默认）

目标是供“研究卡片”直接呈现的 digest，建议输出 Markdown，结构固定以便后续模板稳定渲染：

当 `language=zh-CN`：
- `## TL;DR`（3~6 行）
- `## 研究问题与贡献`
- `## 方法要点`
- `## 关键结果`
- `## 局限与可复现性线索`（例如数据/代码/假设/边界）
- `## 分章节总结`（按全文大纲逐章总结；标题尽量沿用原文 heading）

当 `language=en-US`：
- `## TL;DR`（3~6 lines）
- `## Research Question & Contributions`
- `## Method Highlights`
- `## Key Results`
- `## Limitations & Reproducibility`
- `## Section-by-Section Summary`（in outline order; keep original headings when possible）

注意：
- 不要引入“项目视角内容”（必须保持通用）。
- 不要臆造不存在的实验结果；不确定就写“未明确给出/需核对原文”。

### 3.3 References 抽取（核心）

推荐优先级（从确定性到不确定性）：

1) **定位参考文献章节**
   - 在全文中查找标题/分隔符关键字（大小写敏感不做额外规范化）：
     - `References`
     - `REFERENCES`
     - `参考文献`
     - `Bibliography`
     - `Works Cited`
   - 若找到多个，优先选择“最后一个”且长度合理的章节作为 refs 区块
2) **分割条目（entry splitting）**
   - 先识别“编号型”：
     - `^\s*\[\d+\]\s+`
     - `^\s*\d+\.\s+`
     - `^\s*\d+\)\s+`
   - 若编号型不存在，尝试“作者‑年份型”启发式：
     - 行首出现作者串 + 紧随 `(19|20)\d{2}` 或 `(?:19|20)\d{2}`，并在后续出现标题/期刊信息
   - 对跨行的条目做合并（直到遇到下一条目起始模式）
3) **字段抽取（per entry）**
   - `raw`: 合并后的原始条目字符串（清理多余空白，但不丢信息）
   - `DOI`: 通过 `10.\d{4,9}/...` 形式正则提取（若有多个取最可信一个）
   - `url`: 提取 `http(s)://...`
   - `arxiv`: 提取 `arXiv:\d{4}\.\d{4,5}` 或 `arxiv.org/abs/...`
   - `year`: 抽取第一个可信的 `19xx/20xx`（如存在多个，优先靠近作者段的那个）
   - `author[]` 与 `title`：使用启发式抽取（允许失败）：
     - 作者通常在条目起始，直到 year 或第一个句点/逗号组合
     - 标题通常在 year 之后、期刊/会议名之前；若出现引号，可优先取引号内
   - `confidence`: 根据可抽取字段数量/一致性给出 0~1

> v1 的目标不是完美 BibTeX 解析，而是“对后续匹配组件有用且可审计”：raw 永远保留，结构化字段尽力补全。

### 3.4 自检与修正（必须做）

在输出 JSON 前做最小自检：

- 检查 `digest_path`/`references_path` 对应的文件是否存在，可读。
- 验证 `references_path` 指向的 JSON 是否为数组；每条仍需含 `author/title/year/raw/confidence`。
- 保证 `provenance`/`warnings`/`error` 合理，避免遗漏。

推荐：将“自检与修正 + 输出物化”脚本化（确定性、可重复），例如：
- `literature-digest/scripts/provenance.py`：生成 `provenance.generated_at/input_hash`
- `literature-digest/scripts/validate_output.py`：校验输出；在失败时可用 `--mode fix` 进行自动修复（含将 digest/references 写入 `md_path` 所在目录并回传路径）并将修复记录写入 `warnings`

---

## 4. 与 Zotero 插件的对齐点（防串单）

skill 输出的 `digest_path`/`references_path` 与 `md_path`/`language` 的组合共同确保幂等；Zotero 插件可根据调用时的输入再次对齐。

---

## 5. 失败模式（建议结构化错误，但不强制）

若读取文件失败/路径无效，建议返回一个 JSON 响应，例如：

```json
{
  "digest_path": "",
  "references_path": "",
  "provenance": { "generated_at": "2026-01-17T12:34:56Z", "input_hash": "" },
  "warnings": [],
  "error": { "code": "FILE_NOT_FOUND", "message": "md_path not found" }
}
```

这样 Zotero 插件可以统一解析 JSON 并给出更清晰的错误提示。
