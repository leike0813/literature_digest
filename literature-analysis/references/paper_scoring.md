# Paper Scoring

本文件补充 `persist_literature_score` 的语义判断方法。进入评分阶段、修复评分 payload，或需要判断 `not_applicable` 与置信度时读取；执行顺序、CLI 和最终 stdout 契约以 `SKILL.md` 为准。

## 评分目标

评分同时表达两件事：

- `overall_score`：论文文本所呈现的科学质量，范围 0–100。
- `confidence`：agent 对上述质量判断的把握，范围 0–1。

runtime 另行计算：

```text
confidence_adjusted_score = overall_score × confidence
```

不要用置信度代替质量分。论文可能方法设计良好，但原文缺页、OCR 质量差或关键附录不可见；此时质量分可以较高，置信度应降低。反过来，文本证据完整也不代表论文质量高：证据充分支持一个明显薄弱的设计时，质量分应低而置信度可以高。

评分只判断当前 `normalized_source` 能支持的内容。论文作者、机构、期刊、会议名气、引用量、搜索热度和外部评价都不是评分证据。

## Prepare 与 Submit

Prepare：

```bash
python scripts/run_analysis.py persist_literature_score --db-path "<db_path>"
```

读取 prepare stdout 中的：

- `scoring_context_path`
- `scoring_rubric_path`
- `allowed_payload_shape`
- `field_guidance`

`scoring_context_path` 指向本次运行的评分上下文，其中包含归一化原文路径、目标语言、当前 rubric 快照和证据策略。评分时以这个文件和它指向的 `normalized_source_path` 为准，不要从原始 PDF、网页或外部数据库拼接额外证据。

Submit：

```bash
python scripts/run_analysis.py persist_literature_score \
  --db-path "<db_path>" \
  --payload-file score.json
```

payload 必须完整覆盖 prepare 返回的全部 dimension 和 criterion key。agent 只提交论文类型、逐项判断、理由、证据和各维度置信度。下列字段由 runtime 从 rubric 与语义 payload 计算，禁止提交：

- rubric/schema 标识
- criterion maximum scores
- dimension configured/effective weights
- dimension raw/applicable totals
- dimension scores
- `overall_score`
- `confidence`
- `confidence_adjusted_score`

## 论文类型

先选最能描述主要论证方式的 `paper_type`：

- `empirical`：以实验、观测或量化分析检验主张。
- `review`：以系统整理、比较或综合已有研究为主。
- `theoretical`：以定理、证明、形式模型或理论推导为主。
- `qualitative`：以访谈、案例、田野材料或质性编码为主。
- `mixed_methods`：质性与量化证据共同承担主要论证。
- `other`：上述类别都不能稳定描述论文。

`paper_type_reason` 应简短说明判断依据。论文类型用于解释 criterion 是否适用，不会直接增加或降低分数。

## 六个维度

rubric JSON 是 key、权重和单项满分的唯一事实源。本节解释其语义，不替代 runtime 提供的 rubric 快照。

### Methodological Rigor（25%）

判断作者是否用可靠、合理且可审查的方法回答研究问题。

- `research_question_clarity`：研究目标、问题或假设是否清楚。
- `method_description_sufficiency`：方法信息是否足以理解其核心机制。
- `analysis_process_completeness`：实验、证明、分析或质性流程是否闭合。
- `baseline_or_control_adequacy`：是否使用与论文类型相称的 baseline、control、对照材料或替代解释检验。
- `parameter_transparency`：关键参数、阈值、选择规则或分析设定是否透明。

不要把“方法复杂”当作“方法严谨”。一个简单但与问题匹配、控制充分、决策透明的方法可以得到高分。

### Evidence Completeness（20%）

判断论文给出的证据是否足以支持其结论。

- `experiment_coverage`：证据是否覆盖主要主张和重要边界。
- `data_scale_adequacy`：样本、数据集、案例或证明范围是否与结论相称。
- `statistical_analysis`：需要统计或不确定性分析时，处理是否充分。
- `claim_evidence_alignment`：结论是否严格落在证据支持的范围内。

宽泛结论只由单一数据集、少量案例或一次运行支持时，应降低分数。作者明确收窄结论范围，则不应因研究范围窄而机械扣分。

### Reproducibility（15%）

判断仅根据论文文本，第三方能否重建研究材料与过程。

- `data_source_clarity`：数据、样本或材料来源是否明确。
- `code_availability`：是否提供代码、实现或可访问的等价工件。
- `parameter_availability`：关键参数和配置是否公开。
- `procedure_detail`：训练、实验、证明、编码或分析步骤是否详细。
- `environment_description`：软件、硬件、依赖或实验环境是否说明。

代码链接必须在归一化原文中可见；不要联网检查链接是否仍可访问。没有代码声明通常是低分或零分，而不是 `not_applicable`。若论文类型确实不产生代码，例如纯理论论文，才考虑该 criterion 不适用。

### Innovation Signals（15%）

判断文本是否给出创新行为及其依据，不直接宣判该工作在整个领域中是否首次出现。

- `new_method_or_framework`：是否提出清楚的新方法、框架或组合方式。
- `addresses_known_limitations`：是否针对已有方法的明确缺陷提出解决方案并给出验证。
- `new_theoretical_explanation`：是否提出新的机制解释、理论推导或概念关系。

作者自称 novel 只是声明。高分还需要方法差异、问题缺口、推导或实验结果等文本证据。缺少外部先验时，不要以“我不知道是否已有类似工作”为由把质量分压到零；降低 confidence，并按论文实际展示的创新信号评分。

### Research Impact Potential（15%）

判断论文是否具备产生影响的结构性条件，不预测真实引用量或市场结果。

- `problem_importance`：问题是否对应清楚且有意义的研究或应用需求。
- `method_transferability`：方法、结论或工具是否可能迁移到其他数据、任务或场景。
- `application_breadth`：潜在使用范围是否超出一个极窄的单点案例。

问题范围窄不必然低质量。若论文清楚解决高价值窄问题，`problem_importance` 可以高，而 `application_breadth` 较低。不要因为作者来自知名机构或发表在知名 venue 而加分。

### Writing Quality（10%）

判断表达是否帮助读者准确理解与审查研究。

- `structural_clarity`：章节组织和信息层级是否清楚。
- `terminology_consistency`：术语、符号和缩写是否一致。
- `logical_coherence`：论证是否连贯，前提、过程和结论能否衔接。
- `figure_table_effectiveness`：图表是否被有效说明并承担信息表达功能。
- `language_quality`：语言是否规范、准确且可读。

输入转换造成的零散乱码、断行或公式损坏应主要反映在 confidence；只有能判断问题来自论文表达本身时，才降低写作质量分。

## 分数使用

每个 criterion 使用 rubric 指定的整数范围。可按以下尺度校准，但最终上限以 prepare 返回的 `max_score` 为准：

- 0：没有支持，或文本直接显示严重缺失。
- 约 25%：有弱信号，但不足以承担该项要求。
- 约 50%：基本满足，仍有明显缺口。
- 约 75%：大部分满足，缺口有限。
- 100%：证据清楚、完整，且与该项要求高度一致。

不要为了让总分“看起来合理”反向调整 criterion。逐项依据文本评分，runtime 会完成归一化和聚合。

## `not_applicable` 的边界

`not_applicable` 表示该 criterion 对当前论文类型没有合理评价对象。它不表示：

- 作者没有报告相关信息
- 原文证据很弱
- agent 不确定
- 输入转换质量差
- 该项得分会拉低总分

这些情况仍应使用 `scored`，根据实际缺失给低分，并通过 reason 与 confidence 表达信息不足。

部分 criterion 不适用时，runtime 用该维度剩余 applicable maximum points 归一化，维度权重不变。整个维度都不适用时：

- 该维度的 score 和 confidence 为 null；
- effective weight 为 0；
- configured weight 按比例分配到其他 active dimensions；
- stdout warnings 记录该维度。

所有维度都不适用会被拒绝。

## Evidence 写法

证据项必须包含：

```json
{
  "line_start": 42,
  "line_end": 44,
  "quote": "The authors compare against three baseline methods."
}
```

行号是 `normalized_source_path` 中的 1-based 行号。`quote` 必须出现在声明的行范围内；runtime 会折叠空白后核对。引用应短而有辨识度，最长 500 字符。

一个 criterion 可以有多条证据。证据数组也可以为空，但 reason 必须清楚说明可观察到的缺失，例如“全文未报告代码地址或实现获取方式”。不要虚构一句“代码未公开”的原文引用。

证据只证明文本中出现了什么。对 `code_availability` 而言，代码链接是可见证据；链接实际可用性不在本 skill 的判断范围内。

## Confidence 校准

每个 active dimension 提交 0–1 的 confidence。建议综合考虑：

- 当前输入是否覆盖论文主体、附录和图表文字；
- 相关信息是否明确出现，还是依赖间接推断；
- OCR、公式、表格或版面转换是否损坏了关键证据；
- 多处文本是否相互一致；
- 论文类型是否让该维度容易从文本判断。

可用以下区间保持一致：

- 0.90–1.00：直接证据完整，几乎无需推断。
- 0.75–0.89：证据较充分，仅有小范围缺口。
- 0.55–0.74：有可用证据，但关键细节缺失或需要明显推断。
- 0.30–0.54：只能做初步判断，输入或信息缺口较大。
- 0.00–0.29：该维度虽有评价对象，但现有文本几乎不足以稳定判断。

整个维度 `not_applicable` 时 confidence 必须为 null 或省略。不要给 N/A 维度填写 0；0 表示有评价对象但判断把握极低。

## Payload 示例

下面只展示一个缩短的形状。正式 payload 必须覆盖 prepare 返回的全部六个维度与全部 criteria，不能省略其余项。

```json
{
  "paper_type": "empirical",
  "paper_type_reason": "论文以模型实验和消融分析检验主要主张。",
  "dimension_reviews": [
    {
      "dimension_key": "methodological_rigor",
      "confidence": 0.86,
      "summary": "研究问题明确，方法流程可追踪，但参数选择依据仍不充分。",
      "criteria": [
        {
          "criterion_key": "research_question_clarity",
          "status": "scored",
          "score": 5,
          "reason": "引言明确给出研究目标和约束。",
          "evidence": [
            {
              "line_start": 18,
              "line_end": 19,
              "quote": "We study how to reduce inference cost while preserving accuracy."
            }
          ]
        },
        {
          "criterion_key": "baseline_or_control_adequacy",
          "status": "scored",
          "score": 4,
          "reason": "比较了三个 baseline 并报告消融，但缺少一个强近期基线。",
          "evidence": []
        }
      ]
    }
  ]
}
```

合法 N/A item：

```json
{
  "criterion_key": "code_availability",
  "status": "not_applicable",
  "score": null,
  "reason": "该纯理论论文不包含需要实现或运行的算法与实验。",
  "evidence": []
}
```

若论文只是没有提供代码，应改为 `scored` 且给低分：

```json
{
  "criterion_key": "code_availability",
  "status": "scored",
  "score": 0,
  "reason": "全文未报告代码仓库、补充实现或可执行工件。",
  "evidence": []
}
```

## 常见失败与恢复

- `score_prerequisite_missing`：确认 `normalized_source` 已写入；full mode 还需先完成 `persist_digest`。
- `scoring_context_failed`：检查 runtime rubric/template snapshot 是否存在且为有效 JSON。
- `score_payload_invalid`：按 `error.details` 修复缺失、未知、重复 key，非法 enum、分数范围、N/A、confidence 或 evidence 行号问题，再提交完整 payload。
- `score_render_failed`：不要手改 `literature_score.json`；检查 DB 中的评分状态、runtime template 和 render schema 后重跑评分或 finalization。
- evidence quote 不匹配：重新从 `normalized_source_path` 复制短 quote，并核对 1-based 行号。
- whole-dimension N/A warning：确认所有 criterion 的确没有合理评价对象；如果只是未报告，应恢复为 scored 并给低分。

## 完成检查

提交成功后确认：

- `literature_score_path` 是绝对路径，文件名为 `literature_score.json`；
- 文件包含 `overall_score`、`confidence`、`confidence_adjusted_score`；
- 六个 canonical dimensions 均保留；
- 每个 criterion 均保留，N/A criterion 的 score 为 null；
- configured/effective weights 与 aggregate values 来自 runtime；
- score-only stdout 中其他公开产物路径为空字符串；
- result JSON mirror 与最终 stdout 内容一致。
