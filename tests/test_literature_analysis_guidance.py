import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class LiteratureAnalysisGuidanceTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (REPO_ROOT / relative_path).read_text(encoding="utf-8")

    def test_skill_md_contains_deep_execution_contract(self):
        skill_md = self.read("literature-analysis/SKILL.md")

        for marker in [
            "## 后台自动化约束",
            "## 输入输出硬契约",
            "## Subagent Delegation Contract",
            "## SQLite SSOT",
            "## LLM 与脚本职责边界",
            "## 参数词表（literature-analysis）",
            "## 最小执行主路径",
            "成功态 stdout 示例",
            "失败态 stdout 示例",
            "source_and_plan.md",
            "digest_generation.md",
            "reference_extraction.md",
            "citation_analysis.md",
            "finalization_and_recovery.md",
        ]:
            self.assertIn(marker, skill_md)

        for stage in [
            "### 1. `init_runtime`",
            "### 2. `persist_analysis_plan`",
            "### 3. `persist_digest`",
            "### 4. `persist_references`",
            "### 5. `persist_citation_analysis`",
            "### 6. `finalize_outputs`",
        ]:
            self.assertIn(stage, skill_md)

        for field in [
            "selected_parse_pattern",
            "allowed_parse_patterns_by_reference_key",
            "metadata_review_packages",
            "reference_review_packages",
            "file_quality_low",
            "suspect_blocks",
            "topic",
            "usage",
            "role_in_context",
            "citation_work_key",
            "timeline_summaries",
            "representative_image",
            "literature_matching_metadata",
            "reference_preprocess_quality",
            "citation_false_positive_filtered",
            "report_md",
            "citation_analysis.md",
        ]:
            self.assertIn(field, skill_md)

        self.assertIn("python scripts/run_analysis.py init_runtime", skill_md)
        self.assertIn("python scripts/run_analysis.py persist_references", skill_md)
        self.assertIn("python scripts/run_analysis.py persist_citation_analysis", skill_md)
        self.assertIn("python literature-analysis/scripts/run_analysis.py", skill_md)
        self.assertIn("PYTHONPATH=literature-analysis/scripts python -m run_analysis", skill_md)
        self.assertIn("payload_json_invalid", skill_md)
        self.assertIn("JSON encoder", skill_md)
        self.assertIn("Reference core review subagent prompt (short)", skill_md)
        self.assertIn("Metadata enrichment subagent prompt (short)", skill_md)
        self.assertIn("Citation semantic review subagent prompt (short)", skill_md)
        self.assertIn("Mandatory delegation points", skill_md)
        self.assertIn("Reference Core Review Delegation Point", skill_md)
        self.assertIn("Metadata Enrichment Delegation Point", skill_md)
        self.assertIn("Citation Semantic Review Delegation Point", skill_md)

    def test_skill_md_does_not_reintroduce_old_gate_main_path(self):
        skill_md = self.read("literature-analysis/SKILL.md")

        forbidden = [
            "每次正式写库后都必须重新运行 gate_runtime.py",
            "只能执行 gate 返回的 next_action",
            "python scripts/gate_runtime.py",
            "python scripts/stage_runtime.py",
            "literature-digest/scripts/",
        ]
        for marker in forbidden:
            self.assertNotIn(marker, skill_md)

    def test_reference_files_preserve_old_high_risk_rules(self):
        source = self.read("literature-analysis/references/source_and_plan.md")
        digest = self.read("literature-analysis/references/digest_generation.md")
        refs = self.read("literature-analysis/references/reference_extraction.md")
        citations = self.read("literature-analysis/references/citation_analysis.md")
        finalization = self.read("literature-analysis/references/finalization_and_recovery.md")

        for marker in [
            "LaTeX 工程目录",
            "```bibtex",
            "PDF signature",
            "source_documents.normalized_source",
            "parent-section selection",
            "bm25_text",
            "literature_matching_metadata",
            "literature_matching_metadata.v1",
            "representative_image",
        ]:
            self.assertIn(marker, source)

        for marker in [
            "## TL;DR",
            "## 研究问题与贡献",
            "representative_image",
            "markdown_image_ref",
            "pdf_figure_caption",
            "includegraphics",
            "digest_slots",
            "Section-by-Section Summary",
            "Segment 1",
            "Illegal Payload Examples",
            "Representative image without evidence",
        ]:
            self.assertIn(marker, digest)

        for marker in [
            "placeholder_title",
            "reference_author_refinement_invalid",
            "quality_directives",
            "metadata_context_text",
            "file_quality_low",
            "fallback_best_ratio",
            "cjk_type_marker_entry",
            "GB/T 7714",
            "Unicode-aware tokenizer",
            "reference_preprocess_quality",
            "reference_entry_splitting_failed",
            "reference_numbering_anomaly_detected",
            "reference_entries",
            "reference_parse_candidates",
            "token coverage",
            "missing_tokens_sample",
            "reference_boundary_suspicion_after_review",
            "conferenceName",
            "publicationTitle",
            "DOI",
            "selected_parse_pattern",
            "allowed_parse_patterns_by_reference_key",
            "Core review subagent prompt template",
            "Metadata enrichment subagent prompt template",
            "LNCS, vol.",
            "Example 1: Preprint",
            "Example 2: Conference",
            "Example 3: Short conference entry",
            "Example 4: Journal",
            "Example 5: Thesis",
            "Source text:",
            "Core review:",
            "Metadata review:",
        ]:
            self.assertIn(marker, refs)
        self.assertNotIn("accept_reviewed_entries", refs)

        for marker in [
            "\\cite{...}",
            "citation_false_positive_filtered",
            "references_abandoned_file_quality_low",
            "Waqas Zamir, S.",
            "duplicate `citation_work_key`",
            "background",
            "baseline",
            "contrast",
            "component",
            "dataset",
            "tooling",
            "historical",
            "uncategorized",
            "timeline_summaries",
            "citation_timeline_missing_year",
            "citation_work_key",
            "role_in_context",
            "Subagent prompt template",
            "report_md",
            "illegal scope override",
            "statistical summary without basis",
            "citation_merge_failed",
        ]:
            self.assertIn(marker, citations)

        for marker in [
            "absolute",
            "result_json_path",
            "artifact_registry",
            "scope_fallback_used",
            "reference_numbering_anomaly_detected",
            "reference_parse_low_confidence",
            "digest_undercoverage",
            "citation_analysis.md",
            "report_md",
            "不要手改 SQLite",
            "Safe-To-Regenerate Files",
            "Final Validation Checklist",
        ]:
            self.assertIn(marker, finalization)

    def test_analysis_reference_docs_do_not_reintroduce_old_main_path(self):
        forbidden = [
            "每次正式写库后都必须重新运行 gate_runtime.py",
            "只能执行 gate 返回的 next_action",
            "python scripts/gate_runtime.py",
            "python scripts/stage_runtime.py",
            "literature-digest/scripts/",
            "sql_playbook.md",
        ]
        for path in (REPO_ROOT / "literature-analysis" / "references").glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                self.assertNotIn(marker, text, path.name)

    def test_analysis_guidance_uses_current_payload_only(self):
        for relative_path in [
            "literature-analysis/SKILL.md",
            "literature-analysis/references/reference_extraction.md",
            "literature-analysis/references/citation_analysis.md",
            "literature-analysis/assets/core_instruction.md",
        ]:
            text = self.read(relative_path)
            for marker in [
                "兼容旧 payload",
                "旧 payload",
                "v1 fallback",
                "backward compatibility",
                "selected_pattern",
                "metadata_enrichment_items",
                "timeline.*.ref_indexes",
                "basis.research_threads",
                "basis.argument_shape",
                "validate_payload",
            ]:
                self.assertNotIn(marker, text, relative_path)

    def test_analysis_guidance_uses_portable_python_commands(self):
        for relative_path in [
            "literature-analysis/SKILL.md",
            "literature-analysis/references/reference_extraction.md",
            "literature-analysis/references/citation_analysis.md",
            "literature-analysis/assets/core_instruction.md",
            "literature-analysis/assets/runner.json",
        ]:
            text = self.read(relative_path)
            self.assertNotIn('uv run --project="$HOME/.ar"', text, relative_path)
            self.assertNotIn("$HOME/.ar", text, relative_path)

    def test_subagent_guidance_names_canonical_fields_and_warnings(self):
        skill_md = self.read("literature-analysis/SKILL.md")
        refs = self.read("literature-analysis/references/reference_extraction.md")
        citations = self.read("literature-analysis/references/citation_analysis.md")
        core_instruction = self.read("literature-analysis/assets/core_instruction.md")
        combined_refs = f"{skill_md}\n{refs}\n{core_instruction}"
        for marker in [
            "must delegate core reference review and metadata enrichment by batch",
            "## LLM And Script Responsibilities",
            "## Mandatory Subagent Delegation Points",
            "Reference Core Review Delegation Point",
            "Metadata Enrichment Delegation Point",
            "Canonical metadata fields",
            "metadata_review_packages",
            "instructions.allowed_metadata_fields",
            "instructions.locked_fields",
            "publicationTitle",
            "archiveID",
            "reference_metadata_alias_normalized",
            "reference_metadata_field_unrecognized",
            "arXiv:2004.10934",
            "reference_reviews[].metadata is forbidden",
            "status to enriched, confirmed_existing, or no_metadata_found",
            "main agent is the only DB writer",
            "Do not write DB",
            "modify stable keys",
            "final artifacts",
        ]:
            self.assertIn(marker, combined_refs)
        for marker in [
            "must delegate citation semantic review by batch",
            "## LLM And Script Responsibilities",
            "## Mandatory Subagent Delegation Point",
            "Citation Semantic Review Delegation Point",
            "timeline_summaries",
            "citation_timeline_missing_year",
            "Subagents do not decide timeline bucket membership",
            "Do not include internal indexes",
            "Do not write DB",
            "generate final artifacts",
        ]:
            self.assertIn(marker, citations)

    def test_guidance_prohibits_temporary_scripts_for_semantic_work(self):
        paths = [
            "literature-analysis/SKILL.md",
            "literature-analysis/references/source_and_plan.md",
            "literature-analysis/references/digest_generation.md",
            "literature-analysis/references/reference_extraction.md",
            "literature-analysis/references/citation_analysis.md",
            "literature-analysis/references/finalization_and_recovery.md",
            "literature-analysis/assets/core_instruction.md",
            "literature-analysis/assets/runner.json",
        ]
        combined = "\n".join(self.read(path) for path in paths)
        for marker in [
            "Do not use a temporary script",
            "临时脚本",
            "reference_reviews[]",
            "metadata_reviews[]",
            "citation_semantic_reviews[]",
            "semantic work",
            "JSON 语法",
            "stable key 覆盖",
            "already-returned drafts",
            "reviewed decisions",
        ]:
            self.assertIn(marker, combined)
        self.assertIn("脚本只能做 JSON 序列化、key 覆盖检查、draft 合并和 runtime 调用", combined)

    def test_analysis_assets_use_current_runtime_contract(self):
        runner = json.loads(self.read("literature-analysis/assets/runner.json"))
        self.assertEqual(runner["id"], "literature-analysis")
        prompt = runner["entrypoint"]["prompts"]["common"]
        core_instruction = self.read("literature-analysis/assets/core_instruction.md")
        combined = f"{prompt}\n{core_instruction}"
        self.assertIn("scripts/run_analysis.py", combined)
        self.assertIn("delegate by default", combined)
        self.assertIn("only the main agent submits payloads", combined)
        self.assertIn("Do not use temporary scripts", combined)
        self.assertIn("init_runtime", combined)
        self.assertIn("persist_analysis_plan", prompt)
        self.assertIn("persist_references", combined)
        self.assertIn("persist_citation_analysis", combined)
        for marker in [
            "literature-digest",
            "stage_runtime.py",
            "gate_runtime.py",
            ".literature_digest_tmp",
            "confirm_runtime_paths",
            "bootstrap_runtime_db",
            "persist_render_templates",
        ]:
            self.assertNotIn(marker, combined)

    def test_analysis_skill_package_excludes_python_bytecode(self):
        bytecode = list((REPO_ROOT / "literature-analysis").rglob("*.pyc"))
        pycache_dirs = [path for path in (REPO_ROOT / "literature-analysis").rglob("__pycache__") if path.is_dir()]
        self.assertEqual(bytecode, [])
        self.assertEqual(pycache_dirs, [])
