# localize-runtime-templates-and-infer-language-from-prompt

## Why

当前 `literature-digest` 虽然文档宣称 `language` 可为任意语言，但 digest 与 citation Markdown 渲染仍直接绑定仓库内的 `en-US` / `zh-CN` 模板。与此同时，语言缺省规则仍被写成“默认 `zh-CN`”，与希望由 agent 从 prompt 主语言先做判断的执行约束不一致。

## What Changes

- 在 `bootstrap_runtime_db` 之后新增 `persist_render_templates`，把本次 run 要使用的 digest / citation Markdown 模板固化到 `<tmp_dir>/templates/`。
- `render_and_validate --mode render` 改为只读取 DB 中登记的运行时模板路径来渲染 digest 与 citation Markdown 报告。
- 文档与 runner 统一改口径：未显式提供 `language` 时，先从 prompt 主要语言推断，仅在无法稳定判断时兼容回退 `zh-CN`。
- 为 `citation_analysis.md` 引入单语言源模板，不再在最终运行时模板内部保留硬编码双语分支。
