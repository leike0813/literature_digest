## 1. 目录结构创建

- [x] 1.1 创建 literature-digest-lite 目录结构（assets/templates, scripts）
- [x] 1.2 复制主 skill 的 digest 模板文件（digest.zh-CN.md.j2, digest.en-US.md.j2）

## 2. SKILL.md 编写

- [x] 2.1 编写 SKILL.md 头部（name, description, compatibility）
- [x] 2.2 编写核心执行指令（6 个步骤）
- [x] 2.3 编写 LLM 与脚本职责边界
- [x] 2.4 编写输入输出硬契约
- [x] 2.5 编写参数词表
- [x] 2.6 编写执行主路径（4 个步骤）
- [x] 2.7 编写 Digest 生成细则（与主 skill 完全一致）
  - [x] 2.7.1 Digest 输出结构（zh-CN 和 en-US）
  - [x] 2.7.2 结构化 payload 契约
  - [x] 2.7.3 LLM 提交内容与最终 Markdown 的映射关系
  - [x] 2.7.4 失败语义
  - [x] 2.7.5 合法 payload 示例
  - [x] 2.7.6 非法 payload 示例
  - [x] 2.7.7 最终排版来源
- [x] 2.8 编写默认行为协议
- [x] 2.9 编写脚本 CLI 说明

## 3. run_digest.py 编写

- [x] 3.1 实现输入标准化逻辑（normalize_source 函数）
  - [x] 3.1.1 PDF 处理（pymupdf4llm）
  - [x] 3.1.2 LaTeX 单文件处理
  - [x] 3.1.3 LaTeX 工程目录处理（展平\input / \include）
  - [x] 3.1.4 Markdown/文本处理
- [x] 3.2 实现模板选择逻辑（_repo_digest_template_path 函数）
- [x] 3.3 实现模板渲染逻辑（render_digest 函数）
- [x] 3.4 实现 payload 验证逻辑（validate_digest_payload 函数）
- [x] 3.5 实现 normalize 模式（mode_normalize 函数）
- [x] 3.6 实现 render 模式（mode_render 函数）
- [x] 3.7 实现 CLI 参数解析（argparse）
- [x] 3.8 添加类型注解和错误处理

## 4. 测试与验证

- [x] 4.1 测试 normalize 模式（Markdown 输入）
- [x] 4.2 测试 normalize 模式（错误处理：文件不存在）
- [x] 4.3 测试 render 模式（en-US 语言）
- [x] 4.4 测试 render 模式（zh-CN 语言）
- [x] 4.5 验证输出 JSON schema
- [x] 4.6 验证 digest.md 输出结构
- [x] 4.7 清理临时文件和__pycache__

## 5. 文档完善

- [x] 5.1 补充 SKILL.md 中的 Digest 生成细则（篇幅要求、章节要求）
- [x] 5.2 验证 SKILL.md 与主 skill 的 step_03_digest_generation.md 完全一致
- [x] 5.3 最终代码审查和清理

## 6. Openspec Change 补录

- [x] 6.1 创建 openspec change（create-literature-digest-lite）
- [x] 6.2 创建 proposal.md
- [x] 6.3 创建 specs/lite-skill/spec.md
- [x] 6.4 创建 design.md
- [x] 6.5 创建 tasks.md（本文件）
