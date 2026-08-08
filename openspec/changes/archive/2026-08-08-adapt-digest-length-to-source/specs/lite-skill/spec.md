## REMOVED Requirements

### Requirement: 输入契约

**Reason**: The current digest-only skill is named `literature-digest`; keeping the same contract under `lite-skill` leaves two capabilities for one implementation.
**Migration**: Use the `literature-digest` capability.

### Requirement: 输出契约

**Reason**: The output contract belongs to the current `literature-digest` capability.
**Migration**: Use the `literature-digest` capability.

### Requirement: 输入标准化

**Reason**: Input normalization belongs to the current `literature-digest` capability.
**Migration**: Use the `literature-digest` capability.

### Requirement: Digest 生成

**Reason**: Digest generation belongs to the current `literature-digest` capability.
**Migration**: Use the `literature-digest` capability.

### Requirement: Digest 输出结构（zh-CN）

**Reason**: Chinese digest structure belongs to the current `literature-digest` capability.
**Migration**: Use the `literature-digest` capability.

### Requirement: Digest 输出结构（en-US）

**Reason**: English digest structure belongs to the current `literature-digest` capability.
**Migration**: Use the `literature-digest` capability.

### Requirement: 模板翻译

**Reason**: Template translation belongs to the current `literature-digest` capability.
**Migration**: Use the `literature-digest` capability.

### Requirement: 模板渲染

**Reason**: Template rendering belongs to the current `literature-digest` capability.
**Migration**: Use the `literature-digest` capability.

### Requirement: LLM 与脚本职责边界

**Reason**: The responsibility boundary belongs to the current `literature-digest` capability.
**Migration**: Use the `literature-digest` capability.

### Requirement: 分章节总结细则

**Reason**: Section-summary behavior belongs to the current `literature-digest` capability.
**Migration**: Use the `literature-digest` capability.
