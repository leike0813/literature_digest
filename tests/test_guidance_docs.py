import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class GuidanceDocsTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (REPO_ROOT / relative_path).read_text(encoding="utf-8")

    def test_skill_md_stays_slim_but_indexes_full_guidance(self):
        skill_md = self.read("literature-digest/SKILL.md")
        self.assertIn("## 参数词表（全项目统一）", skill_md)
        self.assertIn("## 最小执行主路径", skill_md)
        self.assertIn("## 按需读取附录", skill_md)
        self.assertIn("gate_runtime_interface.md", skill_md)
        self.assertIn("stage_runtime_interface.md", skill_md)
        self.assertIn("step_05_citation_pipeline.md", skill_md)
        self.assertIn("stage_runtime.py", skill_md)
        self.assertIn("`execution_note`", skill_md)
        self.assertIn("prepare_references_workset", skill_md)
        self.assertIn("persist_reference_entry_splits", skill_md)
        self.assertIn("prepare_citation_workset", skill_md)
        self.assertIn("persist_citation_timeline", skill_md)
        self.assertIn("persist_citation_summary", skill_md)
        self.assertIn("failure_recovery.md", skill_md)
        self.assertIn("不得在开始阶段一次性读取全部 step 文档", skill_md)
        self.assertIn("`outline_nodes`", skill_md)
        self.assertIn("`digest_slots`", skill_md)
        self.assertIn("`items`", skill_md)
        self.assertIn("`summary`", skill_md)
        self.assertIn("`topic`", skill_md)
        self.assertIn("`usage`", skill_md)
        self.assertIn("`keywords`", skill_md)
        self.assertIn("`is_key_reference`", skill_md)
        self.assertIn("`selected_pattern`", skill_md)
        self.assertIn("### 1. `bootstrap_runtime_db`", skill_md)
        self.assertIn("### 12. `render_and_validate --mode render`", skill_md)
        self.assertIn("调用命令", skill_md)
        self.assertIn("必须提供的参数 / payload", skill_md)
        self.assertIn("各 payload 字段含义", skill_md)
        self.assertIn("最小合法示例", skill_md)
        self.assertIn("完成后应该看到的 gate 结果", skill_md)
        self.assertIn("本步最常见错误", skill_md)
        self.assertNotIn("#### 示例1（预印本）", skill_md)
        self.assertNotIn("## Citation Analysis（Dynamic Citation Scope）细则", skill_md)
        self.assertNotIn("runtime_playbook.md", skill_md)
        self.assertNotIn("rendering_contracts.md", skill_md)
        self.assertNotIn("它不是什么", skill_md)
        self.assertNotIn("写入的表", skill_md)
        self.assertNotIn("读取的 DB 真源", skill_md)
        self.assertNotIn("长版SKILL", skill_md)
        self.assertNotIn("旧长版", skill_md)
        self.assertNotIn("guidance_migration_map.md", skill_md)
        self.assertNotIn("dispatch_source.py", skill_md)
        self.assertNotIn("validate_output.py", skill_md)

    def test_runtime_docs_preserve_guidance_without_history_noise(self):
        gate_interface = self.read("literature-digest/references/gate_runtime_interface.md")
        stage_interface = self.read("literature-digest/references/stage_runtime_interface.md")
        step_02 = self.read("literature-digest/references/step_02_outline_and_scopes.md")
        step_03 = self.read("literature-digest/references/step_03_digest_generation.md")
        step_04 = self.read("literature-digest/references/step_04_references_extraction.md")
        step_05 = self.read("literature-digest/references/step_05_citation_pipeline.md")
        step_06 = self.read("literature-digest/references/step_06_render_and_validate.md")
        step_01 = self.read("literature-digest/references/step_01_bootstrap_and_source.md")

        self.assertIn("## stdout Payload", gate_interface)
        self.assertIn("## `next_action` 集合", gate_interface)
        self.assertIn("## `bootstrap_runtime_db`", stage_interface)
        self.assertIn("## `prepare_references_workset`", stage_interface)
        self.assertIn("## `persist_reference_entry_splits`", stage_interface)
        self.assertIn("## `render_and_validate`", stage_interface)
        self.assertIn("按 `SKILL.md` 的“参数词表（全项目统一）”理解", gate_interface)
        self.assertIn("按 `SKILL.md` 的“参数词表（全项目统一）”理解", stage_interface)
        self.assertIn("按 `SKILL.md` 的“参数词表（全项目统一）”定义", step_01)
        self.assertIn("按 `SKILL.md` 的“参数词表（全项目统一）”定义", step_04)
        self.assertIn("按 `SKILL.md` 的“参数词表（全项目统一）”定义", step_05)
        self.assertIn("gate 一旦确认某项前置状态已经存在于 DB", gate_interface)
        self.assertIn("`execution_note: string`", gate_interface)
        self.assertIn("## `execution_note` 约束", gate_interface)
        self.assertIn("failure_recovery.md", gate_interface)
        self.assertNotIn("references/runtime_playbook.md", gate_interface)
        self.assertNotIn("references/rendering_contracts.md", gate_interface)
        self.assertIn("## 分阶段执行与持久化（强制）", step_02)
        self.assertIn("## 文献 Digest 总结细则", step_03)
        self.assertIn("### References 抽取示例", step_04)
        self.assertIn("#### 示例5（学位论文）", step_04)
        self.assertIn("## Citation Analysis（Dynamic Citation Scope）细则", step_05)
        self.assertIn("### 边界情况判定与回退", step_05)
        self.assertIn("由 renderer 根据 DB 内容派生", step_05)
        self.assertIn("source_documents.normalized_source", step_01)
        self.assertIn("可选物化副产物", step_01)
        self.assertIn("bootstrap_runtime_db` 是唯一允许确定 `source_path`", step_01)
        self.assertNotIn("后续所有 Markdown 处理仅消费这个固定路径", step_01)
        self.assertIn("stage_6_render_and_validate", step_02)
        self.assertNotIn("digest.md` 可在 digest 阶段完成后渲染", step_02)
        self.assertIn("后续阶段唯一合法输入来源", step_02)
        self.assertIn("parent_node_id", step_02)
        self.assertIn("metadata", step_02)
        self.assertIn("digest_slots + section_summaries", step_03)
        self.assertIn("最终排版来源", step_03)
        self.assertNotIn("Digest 模版骨架", step_03)
        self.assertIn("非法旧 payload 示例", step_03)
        self.assertIn("`reference_entries`", step_04)
        self.assertIn("`reference_parse_candidates`", step_04)
        self.assertIn("persist_reference_entry_splits", step_04)
        self.assertIn("requires_split_review", step_04)
        self.assertIn("reference_entry_splitting_failed", step_04)
        self.assertIn("编号质量检查", step_04)
        self.assertIn("保守模式", step_04)
        self.assertIn("年份抽取优先级", step_04)
        self.assertIn("`prepare_citation_workset` 必须直接复用 `reference_items`", step_04)
        self.assertIn("selected_pattern", step_04)
        self.assertIn("authors_colon_title_in_year", step_04)
        self.assertIn("author_candidates", step_04)
        self.assertIn("reference_author_refinement_invalid", step_04)
        self.assertIn("不得再次拆成多个数组元素", step_04)
        self.assertIn("只允许读取 `section_scopes.citation_scope`", step_05)
        self.assertIn("export_citation_workset", step_05)
        self.assertIn("图片链接", step_05)
        self.assertIn("citation_false_positive_filtered", step_05)
        self.assertIn("citation_workset_items", step_05)
        self.assertIn("persist_citation_summary", step_05)
        self.assertIn("persist_citation_timeline", step_05)
        self.assertIn("topic", step_05)
        self.assertIn("usage", step_05)
        self.assertIn("keywords", step_05)
        self.assertIn("[AY-k]", step_05)
        self.assertIn("is_key_reference", step_05)
        self.assertIn("Function 级写作规则", step_05)
        self.assertIn("不能只给百分比", step_05)
        self.assertIn("条目级引文语义判断", step_05)
        self.assertIn("不是 agent 输出物", step_05)
        self.assertIn("关键文献", step_05)
        self.assertIn("citation_analysis.json.summary", step_06)
        self.assertIn("citation_summary + citation_items + citation_unmapped_mentions + citation_scope", step_06)
        self.assertIn("主发布路径", step_06)
        self.assertIn("辅助校验路径", step_06)
        self.assertIn("`--mode render` 可选接受 `--out-dir`", step_06)
        self.assertIn("scope_fallback_used", step_06)
        self.assertIn("digest_undercoverage", step_06)
        self.assertNotIn("--source-path PATH] [--out-md PATH] [--out-meta PATH] [--persist-db-only] [--language LANG]", stage_interface)
        self.assertNotIn("--md-path PATH", stage_interface)
        self.assertIn("不再接受 `--source-path`、`--language`", stage_interface)
        self.assertIn("## `prepare_references_workset`", stage_interface)
        self.assertIn("## `persist_reference_entry_splits`", stage_interface)
        self.assertIn("## `prepare_citation_workset`", stage_interface)
        self.assertIn("## `persist_citation_timeline`", stage_interface)
        self.assertIn("## `persist_citation_summary`", stage_interface)
        self.assertIn("`items[*].topic`", stage_interface)
        self.assertIn("`items[*].usage`", stage_interface)
        self.assertIn("`items[*].keywords`", stage_interface)
        self.assertIn("`items[*].is_key_reference`", stage_interface)
        self.assertIn("`basis.research_threads`", stage_interface)
        self.assertIn("`basis.argument_shape`", stage_interface)
        self.assertIn("`basis.key_ref_indexes`", stage_interface)
        self.assertIn("[AY-k]", stage_interface)
        self.assertIn("关键文献", stage_interface)
        self.assertIn("不再接受 `--md-path`、`--language`、`--scope-file`", stage_interface)
        self.assertIn("--mode render [--out-dir DIR]", stage_interface)
        self.assertIn("允许可选 `--out-dir`", stage_interface)
        self.assertIn("字段说明", stage_interface)
        self.assertIn("典型非法示例", stage_interface)
        self.assertIn("成功输出", stage_interface)
        self.assertIn("大 payload 默认通过 `--payload-file`", stage_interface)
        self.assertIn("stored_reference_candidates", stage_interface)
        self.assertIn("review_path", stage_interface)
        self.assertIn("grouping_suspect_count", stage_interface)
        self.assertIn("suspect_entries", stage_interface)
        self.assertIn("reference_author_refinement_invalid", stage_interface)
        self.assertIn("再次拆开单个作者", stage_interface)
        self.assertIn("## 默认行为协议（必须遵守）", step_01)
        for text in (step_01, step_02, step_03, step_04, step_05):
            self.assertNotIn("long-form SKILL", text)
            self.assertNotIn("旧长版", text)
            self.assertNotIn("旧 staged pipeline", text)

    def test_templates_preserve_original_intent(self):
        digest_zh = self.read("literature-digest/assets/templates/digest.zh-CN.md.j2")
        digest_en = self.read("literature-digest/assets/templates/digest.en-US.md.j2")
        citation_md = self.read("literature-digest/assets/templates/citation_analysis.md.j2")

        self.assertIn("## 研究问题与贡献", digest_zh)
        self.assertIn("## Research Question & Contributions", digest_en)
        self.assertIn("总体总结", citation_md)
        self.assertIn("关键文献", citation_md)
        self.assertIn("按功能归类", citation_md)
        self.assertIn("时间线分析", citation_md)
        self.assertIn("Keywords", citation_md)

    def test_runner_points_to_full_external_guidance(self):
        runner = self.read("literature-digest/assets/runner.json")
        self.assertNotIn("minimal runtime contract only", runner)
        self.assertIn("Do not preload the whole `references/` directory", runner)
        self.assertIn("Read only the detailed appendix docs named in `instruction_refs`", runner)
        self.assertIn("Also obey the short `execution_note` returned by gate", runner)
        self.assertIn("scripts/stage_runtime.py <next_action>", runner)
        self.assertIn("Any agent judgment content must be emitted as structured payloads", runner)
        self.assertNotIn("long-form `SKILL.md`", runner)
        self.assertNotIn("guidance_migration_map.md", runner)
        self.assertNotIn("runtime_playbook.md", runner)
        self.assertNotIn("rendering_contracts.md", runner)

    def test_skill_package_references_only_consolidated_runtime_scripts(self):
        docs_to_check = [
            "literature-digest/SKILL.md",
            "literature-digest/assets/runner.json",
            "literature-digest/references/step_01_bootstrap_and_source.md",
            "literature-digest/references/step_06_render_and_validate.md",
            "docs/dev_paper_digest_skill.md",
        ]
        for relative_path in docs_to_check:
            text = self.read(relative_path)
            self.assertNotIn("dispatch_source.py", text, relative_path)
            self.assertNotIn("citation_preprocess.py", text, relative_path)
            self.assertNotIn("render_final_artifacts.py", text, relative_path)
            self.assertNotIn("validate_output.py", text, relative_path)
            if relative_path.startswith("literature-digest/") or relative_path.startswith("docs/"):
                self.assertTrue(
                    "stage_runtime.py" in text or "gate_runtime.py" in text or "runtime_db.py" in text,
                    relative_path,
                )

    def test_glossary_becomes_shared_terminology_source(self):
        skill_md = self.read("literature-digest/SKILL.md")
        stage_interface = self.read("literature-digest/references/stage_runtime_interface.md")
        step_05 = self.read("literature-digest/references/step_05_citation_pipeline.md")
        sql_playbook = self.read("literature-digest/references/sql_playbook.md")

        self.assertIn("`outline_nodes`", skill_md)
        self.assertIn("`references_scope`", skill_md)
        self.assertIn("`citation_scope`", skill_md)
        self.assertIn("`digest_slots`", skill_md)
        self.assertIn("`section_summaries`", skill_md)
        self.assertIn("`selected_pattern`", skill_md)
        self.assertIn("`ref_index`", skill_md)
        self.assertIn("`function`", skill_md)
        self.assertIn("`topic`", skill_md)
        self.assertIn("`usage`", skill_md)
        self.assertIn("`is_key_reference`", skill_md)
        self.assertIn("`summary`", skill_md)
        self.assertIn("`basis`", skill_md)
        self.assertIn("`instruction_refs`", skill_md)
        self.assertIn("按 `SKILL.md` 的“参数词表（全项目统一）”理解", stage_interface)
        self.assertIn("按 `SKILL.md` 的“参数词表（全项目统一）”定义", step_05)
        self.assertIn("参数词表", step_05)
        self.assertIn("SQL", sql_playbook)
        self.assertNotIn("它不是什么", skill_md)

    def test_skill_package_no_long_form_or_deprecated_staged_names(self):
        banned = [
            "guidance_migration_map",
            "长版SKILL",
            "long-form SKILL",
            "旧长版",
            "旧 staged pipeline",
            "runtime_playbook.md",
            "rendering_contracts.md",
            "dispatch_source.py",
            "citation_preprocess.py",
            "render_final_artifacts.py",
            "validate_output.py",
            "outline.json",
            "references_scope.json",
            "references.parts/part-*.json",
            "references_merged.json",
            "citation_scope.json",
            "citation_preprocess.json",
            "citation.parts/part-",
            "citation_merged.json",
            "citation_report.md",
            "迁移自长版",
        ]
        skill_root = REPO_ROOT / "literature-digest"
        for path in skill_root.rglob("*"):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for needle in banned:
                self.assertNotIn(needle, text, f"{needle} leaked into {path}")

    def test_repo_level_traceability_docs_exist(self):
        migration = REPO_ROOT / "references" / "literature_digest_guidance_migration_map.md"
        legacy = REPO_ROOT / "references" / "literature_digest_SKILL_legacy_snapshot.md"
        failure_recovery = REPO_ROOT / "literature-digest" / "references" / "failure_recovery.md"
        self.assertTrue(migration.exists())
        self.assertTrue(legacy.exists())
        self.assertTrue(failure_recovery.exists())

        legacy_text = legacy.read_text(encoding="utf-8")
        self.assertTrue(legacy_text.startswith("---\nname: literature-digest"))
        self.assertIn("# literature-digest", legacy_text)


if __name__ == "__main__":
    unittest.main()
