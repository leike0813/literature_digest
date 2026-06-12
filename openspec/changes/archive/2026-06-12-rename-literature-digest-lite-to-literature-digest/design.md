## Context

项目中有两个 skill 包长期共存：
- `literature-digest/`: SQLite-gated runtime 完整版，包含 7 阶段管线（preprocess → extract → enrich → gate → citation → render）
- `literature-digest-lite/`: 轻量版，仅包含 normalize → render 两阶段，专注于核心 digest 生成

实际使用中，用户绝大多数场景只需要快速的 digest 生成，完整版的 references/citation 管线很少被使用。两个 skill 包的名称与能力存在错位：`literature-digest` 本应是核心功能，却承载了过多重量级管线；`literature-digest-lite` 才是实际完成 digest 生成的 skill。

## Goals / Non-Goals

**Goals:**
- 将 `literature-digest` 名称赋予实际承担 digest 生成的 skill 包（原 lite 版）
- 将旧版完整 skill 包标记为废弃并归档至 `literature-digest.old`
- 确保更名后 `literature-digest` skill 可被正常发现和加载

**Non-Goals:**
- 不修改 skill 能力边界和实现逻辑
- 不涉及 references/citation 管线的迁移或复用
- 不删除旧版代码（仅重命名归档）

## Decisions

### Decision 1: 废弃方式
**选择**: 原地重命名旧目录为 `literature-digest.old`，而非删除

**理由**: 保留旧版代码以便将来需要时参考；重命名而非删除符合"可追溯"原则

**替代方案**:
- 方案 B: 直接删除 → 拒绝，失去历史参考价值
- 方案 C: 移入 archive/ 目录 → 拒绝，破坏可能的相对路径引用，且移动到 `literature-digest.old` 语义更清晰

### Decision 2: 更名接管
**选择**: 原 `literature-digest-lite` 重命名为 `literature-digest`，内容完全不变

**理由**: 这是实际被调用的 digest 生成 skill，应使用最直接的包名

**替代方案**:
- 方案 B: 合并两个 skill → 拒绝，过度复杂且旧版已废弃

## Risks / Trade-offs

### Risk: 存量引用失效
**风险**: 如果外部系统或文档直接引用了旧 `literature-digest` 或 `literature-digest-lite` 路径，更名后这些引用会失效

**缓解**: 项目内所有引用已同步更新；外部引用需要手动更新
