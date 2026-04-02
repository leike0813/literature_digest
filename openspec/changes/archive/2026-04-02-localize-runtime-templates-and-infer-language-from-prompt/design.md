# Design

## Overview

本次变更把语言与模板相关的职责收口成三步：

1. `bootstrap_runtime_db` 只持久化已经确定好的 `language`
2. `persist_render_templates` 把本次 run 的 digest / citation Markdown 模板写入 `<tmp_dir>/templates/`
3. `render_and_validate --mode render` 只从 DB 中登记的运行时模板路径加载模板

仓库模板仍保留，作为 `persist_render_templates` 的源模板；真正参与 render 的模板必须是本次 run 已经固化到临时目录的运行时模板。

## Language Resolution

- 若用户显式提供目标语言，agent 直接采用该值
- 否则 agent 从 prompt 主要语言推断
- 仅当推断不稳定时，兼容回退 `zh-CN`

脚本不负责推断 prompt 语言；它只持久化最终选定值并校验后续模板动作与该语言一致。

## Runtime Templates

运行时模板固定写到：

- `<tmp_dir>/templates/digest.runtime.md.j2`
- `<tmp_dir>/templates/citation_analysis.runtime.md.j2`

`persist_render_templates` 接受结构化 payload：

- `target_language`
- `digest_template`
- `citation_analysis_template`

`en-*` / `zh-*` 目标语言可以直接复制仓库源模板；其它语言由 agent 先翻译仓库源模板，再把最终模板字符串持久化到运行时模板文件。

## Render Behavior

新 run 的 `render_and_validate --mode render` 只读取 DB 中登记的运行时模板路径。

- digest Markdown 使用 `runtime_inputs.digest_template_path`
- citation Markdown report 使用 `runtime_inputs.citation_analysis_template_path`

`references.json.j2` 与 `citation_analysis.json.j2` 继续使用仓库模板；本次只收口两个 Markdown 模板。
