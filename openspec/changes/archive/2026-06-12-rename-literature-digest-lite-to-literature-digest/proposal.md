## Why

原 `literature-digest`（SQLite-gated runtime 完整版）已被重命名为 `literature-digest.old` 并废弃，原 `literature-digest-lite`（轻量版）已重命名为 `literature-digest`。更名后 skill 包名与其实际提供的能力更加匹配——当前 `literature-digest` 专注于核心 digest 生成，不再承载复杂的 references 处理管线。

## What Changes

- **废弃** `literature-digest/`（原 SQLite-gated runtime 完整版），原地重命名为 `literature-digest.old/`
- **更名** `literature-digest-lite/` → `literature-digest/`，成为正式的 literature-digest skill 包
- **更新** SKILL.md 头部元数据（name、description），指向更名后的 skill 包
- **清理** 废弃 skill 包不再参与 skill 发现和加载

## Capabilities

### Modified Capabilities

- `literature-digest`: 原 lite-skill 正式接管 `literature-digest` 名称，能力边界不变（核心 digest 生成，无 references/citation 管线）
- `lite-skill`: 此名称不再使用，其能力已合并至 `literature-digest`

### Removed Capabilities

- `literature-digest`（旧）: SQLite-gated runtime 完整版已废弃，归档至 `literature-digest.old`

## Impact

- **代码影响**: 目录重命名，无代码逻辑修改
- **用户影响**: 调用 `literature-digest` skill 的请求将路由至原 lite 实现；旧 runtime 版不再可用
- **向后兼容**: 不兼容。旧版 `literature-digest` 的能力（references 处理、citation analysis）不再提供
