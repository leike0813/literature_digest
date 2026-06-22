import json
import importlib.util
import io
import contextlib
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_ANALYSIS = REPO_ROOT / "literature-analysis" / "scripts" / "run_analysis.py"
ANALYSIS_SCRIPTS = REPO_ROOT / "literature-analysis" / "scripts"
sys.dont_write_bytecode = True


def load_run_analysis_module():
    spec = importlib.util.spec_from_file_location("literature_analysis_run_analysis", RUN_ANALYSIS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LiteratureAnalysisRuntimeTests(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(RUN_ANALYSIS), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def outline_payload(self, lines: list[str]) -> dict:
        references_line = lines.index("# References") + 1
        return {
            "outline_nodes": [
                {
                    "node_id": "n1",
                    "heading_level": 1,
                    "title": "Introduction",
                    "line_start": 1,
                    "line_end": references_line - 1,
                    "parent_node_id": None,
                    "metadata": {},
                },
                {
                    "node_id": "n2",
                    "heading_level": 1,
                    "title": "References",
                    "line_start": references_line,
                    "line_end": len(lines),
                    "parent_node_id": None,
                    "metadata": {},
                },
            ],
            "references_scope": {
                "section_title": "References",
                "line_start": references_line,
                "line_end": len(lines),
                "metadata": {},
            },
            "citation_scope": {
                "section_title": "Introduction",
                "line_start": 1,
                "line_end": references_line - 1,
                "metadata": {"selection_reason": "fixture", "covered_sections": ["Introduction"]},
            },
            "literature_matching_metadata": {
                "schema": "literature_matching_metadata.v1",
                "key_terms": ["literature analysis"],
                "methods": ["runtime wrapper"],
                "problems": ["paper analysis"],
                "datasets": [],
                "exclude_terms": [],
            },
        }

    def digest_payload(self) -> dict:
        return {
            "digest_slots": {
                "tldr": {"paragraphs": ["This paper is summarized for testing."]},
                "research_question_and_contributions": {
                    "research_question": "How can the runtime be simplified?",
                    "contributions": ["Adds a decision-oriented wrapper."],
                },
                "method_highlights": {"items": ["Reuse the mature runtime."]},
                "key_results": {"items": ["The skeleton renders compatible artifacts."]},
                "limitations_and_reproducibility": {"items": ["This is a first-phase skeleton."]},
            },
            "section_summaries": [
                {"source_heading": "Introduction", "items": ["Introduces the wrapper."]},
                {"source_heading": "References", "items": ["Contains the cited work."]},
            ],
        }

    def metadata_payload_from_packages(self, packages: list[dict], metadata_by_key: dict[str, dict] | None = None) -> dict:
        metadata_by_key = metadata_by_key or {}
        reviews = []
        for package in packages:
            reference_key = package["reference_key"]
            if reference_key in metadata_by_key:
                reviews.append(
                    {
                        "reference_key": reference_key,
                        "status": "fields_extracted",
                        "metadata": metadata_by_key[reference_key],
                        "evidence_note": "Metadata is supported by the test fixture.",
                    }
                )
            elif package.get("existing_metadata"):
                reviews.append(
                    {
                        "reference_key": reference_key,
                        "status": "existing_fields_confirmed",
                        "evidence_note": "Existing metadata retained.",
                    }
                )
            else:
                reviews.append(
                    {
                        "reference_key": reference_key,
                        "status": "no_local_evidence",
                        "evidence_note": "No additional metadata in fixture.",
                    }
                )
        return {"metadata_evidence_reviews": reviews}

    def read_json(self, path_value: str) -> dict:
        return json.loads(Path(path_value).read_text(encoding="utf-8"))

    def reference_packages_from_payload(self, payload: dict) -> list[dict]:
        packages: list[dict] = []
        for batch_path in payload.get("reference_core_batch_paths", []):
            packages.extend(self.read_json(batch_path)["reference_review_packages"])
        return packages

    def metadata_packages_from_payload(self, payload: dict) -> list[dict]:
        packages: list[dict] = []
        for batch_path in payload.get("metadata_evidence_batch_paths", []):
            packages.extend(self.read_json(batch_path)["metadata_evidence_packages"])
        return packages

    def citation_packages_from_payload(self, payload: dict) -> list[dict]:
        packages: list[dict] = []
        for batch_path in payload.get("citation_batch_paths", []):
            packages.extend(self.read_json(batch_path)["citation_work_packages"])
        return packages

    def split_packages_from_payload(self, payload: dict) -> list[dict]:
        path = payload.get("split_review_packages_path")
        if not path:
            return []
        return list(self.read_json(path).get("split_review_packages", []))

    def test_init_runtime_normalizes_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            source.write_text("# Introduction\nText.\n# References\n[1] Smith. Useful Runtime Paper. 2020.\n", encoding="utf-8")
            result = self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)])
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(payload["next_action"], "persist_analysis_plan")
            self.assertTrue(Path(payload["db_path"]).exists())
            self.assertEqual(payload["source_profile"]["source_type"], "markdown")
            self.assertGreater(payload["source_profile"]["normalized_source_chars"], 0)

    def test_invalid_json_payload_returns_structured_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bad_payload = root / "bad_digest.json"
            bad_payload.write_text('{"digest_slots": {"tldr": {"paragraphs": ["含有未转义 "无对象" 引号"]}}}', encoding="utf-8")
            result = self.run_cmd([
                "persist_digest",
                "--db-path",
                str(root / "literature_analysis.db"),
                "--payload-file",
                str(bad_payload),
            ])
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stderr.decode("utf-8", errors="replace"), "")
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(payload["error"]["code"], "payload_json_invalid")
            self.assertEqual(payload["error"]["stage"], "persist_digest")
            self.assertIn("line", payload["error"])
            self.assertIn("column", payload["error"])
            self.assertIn("repair_hint", payload["error"])

    def test_references_prepare_does_not_require_digest_payload(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            lines = [
                "# Introduction",
                "Prior work [1] is relevant.",
                "# References",
                "[1] Smith. Useful Runtime Paper. 2020.",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")
            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            plan = self.run_cmd(["persist_analysis_plan", "--db-path", init["db_path"], "--payload-file", str(plan_path)])
            self.assertEqual(plan.returncode, 0, plan.stderr.decode("utf-8", errors="replace"))

            prepared = self.run_cmd(["persist_references", "--db-path", init["db_path"]])
            self.assertEqual(prepared.returncode, 0, prepared.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(prepared.stdout.decode("utf-8"))
            self.assertEqual(payload["next_action"], "persist_references")
            self.assertTrue(Path(payload["workset_path"]).exists())
            self.assertNotIn("reference_review_packages", payload)
            self.assertNotIn("allowed_parse_patterns_by_reference_key", payload)
            self.assertNotIn("batch_work_packages", payload)
            self.assertIn("reference_core_review_manifest_path", payload)
            self.assertIn("reference_core_batch_paths", payload)
            self.assertTrue(Path(payload["reference_core_review_manifest_path"]).exists())
            self.assertGreaterEqual(payload["reference_core_package_count"], 1)
            self.assertGreaterEqual(payload["reference_core_batch_count"], 1)
            self.assertIn("subagent_prompt_template", payload)
            self.assertIn("allowed_payload_shape", payload)
            self.assertIn("Default to delegating reference core review", payload["subagent_policy"])
            self.assertEqual(payload["merge_contract"]["single_writer"], "main_agent")
            self.assertIn("single DB writer", payload["merge_contract"]["merge_notes"])
            batch = self.read_json(payload["reference_core_batch_paths"][0])
            self.assertIn("batch_id", batch)
            self.assertEqual(batch["batch_kind"], "reference_core_review")
            self.assertTrue(Path(batch["input_package_path"]).exists())
            self.assertTrue(batch["suggested_draft_output_path"].endswith(".draft.json"))
            self.assertLessEqual(len(batch["reference_review_packages"]), 10)
            self.assertIn("allowed_parse_patterns_by_reference_key", batch)
            self.assertIn("required_return_shape", batch)
            self.assertIn("forbidden_fields", batch)
            self.assertIn("metadata", batch["forbidden_fields"])
            self.assertIn("minimal_valid_example", batch)
            self.assertIn("merge_notes", batch)
            self.assertIn("subagent_prompt", batch)
            self.assertIn("Default to delegating", batch["merge_notes"])
            self.assertIn("Do not write DB", batch["subagent_prompt"])
            self.assertEqual(payload["runtime_backend"], "analysis_runtime.references")

    def test_large_prepare_outputs_are_path_first_and_prebatched(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            citation_line = "Prior work " + ", ".join(f"[{index}]" for index in range(1, 22)) + " is relevant."
            reference_lines = [
                f"[{index}] Author {index}. Runtime Paper {index}. {2000 + index}."
                for index in range(1, 26)
            ]
            lines = ["# Introduction", citation_line, "# References", *reference_lines]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")

            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            db_path = init["db_path"]
            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            self.assertEqual(self.run_cmd(["persist_analysis_plan", "--db-path", db_path, "--payload-file", str(plan_path)]).returncode, 0)
            digest_path = root / "digest_payload.json"
            self.write_json(digest_path, self.digest_payload())
            self.assertEqual(self.run_cmd(["persist_digest", "--db-path", db_path, "--payload-file", str(digest_path)]).returncode, 0)

            refs_prepared_result = self.run_cmd(["persist_references", "--db-path", db_path])
            self.assertLess(len(refs_prepared_result.stdout), 51200)
            refs_prepared = json.loads(refs_prepared_result.stdout.decode("utf-8"))
            self.assertNotIn("reference_review_packages", refs_prepared)
            self.assertNotIn("batch_work_packages", refs_prepared)
            self.assertEqual(refs_prepared["reference_core_package_count"], 25)
            self.assertEqual(refs_prepared["reference_core_batch_count"], 3)
            manifest = self.read_json(refs_prepared["reference_core_review_manifest_path"])
            self.assertEqual(len(manifest["required_coverage_keys"]), 25)
            for batch_path in refs_prepared["reference_core_batch_paths"]:
                batch = self.read_json(batch_path)
                self.assertLessEqual(len(batch["reference_review_packages"]), 10)
                self.assertEqual(batch["input_package_path"], batch_path)
                self.assertTrue(batch["suggested_draft_output_path"].endswith(".draft.json"))

            reference_reviews = []
            for package in self.reference_packages_from_payload(refs_prepared):
                source_number = int(package["source_reference_number"])
                reference_reviews.append(
                    {
                        "reference_key": package["reference_key"],
                        "selected_parse_pattern": package["recommended_parse_pattern"],
                        "authors": [f"Author {source_number}"],
                        "title": f"Runtime Paper {source_number}",
                        "publication_year": 2000 + source_number,
                    }
                )
            refs_path = root / "refs_payload.json"
            self.write_json(refs_path, {"reference_reviews": reference_reviews})
            core = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(refs_path)])
            self.assertLess(len(core.stdout), 51200)
            self.assertEqual(core.returncode, 0, core.stderr.decode("utf-8", errors="replace"))
            core_payload = json.loads(core.stdout.decode("utf-8"))
            self.assertNotIn("metadata_evidence_packages", core_payload)
            self.assertNotIn("batch_work_packages", core_payload)
            self.assertEqual(core_payload["metadata_evidence_package_count"], 25)
            self.assertEqual(core_payload["metadata_evidence_batch_count"], 3)
            for batch_path in core_payload["metadata_evidence_batch_paths"]:
                batch = self.read_json(batch_path)
                self.assertLessEqual(len(batch["metadata_evidence_packages"]), 10)
                self.assertFalse(batch["external_lookup_allowed"])
                self.assertIn("web search", batch["forbidden_actions"])

            metadata_path = root / "metadata_payload.json"
            self.write_json(metadata_path, self.metadata_payload_from_packages(self.metadata_packages_from_payload(core_payload)))
            self.assertEqual(self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(metadata_path)]).returncode, 0)

            citation_result = self.run_cmd(["persist_citation_analysis", "--db-path", db_path])
            self.assertLess(len(citation_result.stdout), 51200)
            self.assertEqual(citation_result.returncode, 0, citation_result.stderr.decode("utf-8", errors="replace"))
            citation_payload = json.loads(citation_result.stdout.decode("utf-8"))
            self.assertNotIn("citation_work_packages", citation_payload)
            self.assertNotIn("batch_work_packages", citation_payload)
            self.assertEqual(citation_payload["citation_package_count"], 21)
            self.assertEqual(citation_payload["citation_batch_count"], 3)
            citation_manifest = self.read_json(citation_payload["citation_semantic_review_manifest_path"])
            self.assertEqual(len(citation_manifest["required_coverage_keys"]), 21)
            for batch_path in citation_payload["citation_batch_paths"]:
                batch = self.read_json(batch_path)
                self.assertLessEqual(len(batch["citation_work_packages"]), 10)

    def test_full_wrapper_outputs_compatible_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            lines = [
                "# Introduction",
                "Prior work [1] is relevant to this runtime.",
                "# References",
                "[1] Smith. Useful Runtime Paper. 2020.",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")

            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            db_path = init["db_path"]

            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            self.assertEqual(self.run_cmd(["persist_analysis_plan", "--db-path", db_path, "--payload-file", str(plan_path)]).returncode, 0)

            digest_path = root / "digest_payload.json"
            self.write_json(digest_path, self.digest_payload())
            self.assertEqual(self.run_cmd(["persist_digest", "--db-path", db_path, "--payload-file", str(digest_path)]).returncode, 0)

            prepared = json.loads(self.run_cmd(["persist_references", "--db-path", db_path]).stdout.decode("utf-8"))
            ref_package = self.reference_packages_from_payload(prepared)[0]
            refs_path = root / "refs_payload.json"
            self.write_json(
                refs_path,
                {
                    "reference_reviews": [
                        {
                            "reference_key": ref_package["reference_key"],
                            "selected_parse_pattern": ref_package["recommended_parse_pattern"],
                            "authors": ["Smith"],
                            "title": "Useful Runtime Paper",
                            "publication_year": 2020,
                            "review_notes": "Fixture reference parsed from numeric bibliography entry.",
                        }
                    ]
                },
            )
            refs = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(refs_path)])
            self.assertEqual(refs.returncode, 0, refs.stderr.decode("utf-8", errors="replace"))
            refs_response = json.loads(refs.stdout.decode("utf-8"))
            self.assertEqual(refs_response["next_action"], "persist_references")
            metadata_path = root / "metadata_payload.json"
            self.write_json(metadata_path, self.metadata_payload_from_packages(self.metadata_packages_from_payload(refs_response)))
            metadata = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(metadata_path)])
            self.assertEqual(metadata.returncode, 0, metadata.stderr.decode("utf-8", errors="replace"))

            citation_prepared = self.run_cmd(["persist_citation_analysis", "--db-path", db_path])
            self.assertEqual(citation_prepared.returncode, 0, citation_prepared.stderr.decode("utf-8", errors="replace"))
            citation_workset_payload = json.loads(citation_prepared.stdout.decode("utf-8"))
            self.assertNotIn("citation_work_packages", citation_workset_payload)
            self.assertNotIn("batch_work_packages", citation_workset_payload)
            self.assertIn("citation_semantic_review_manifest_path", citation_workset_payload)
            self.assertIn("citation_batch_paths", citation_workset_payload)
            self.assertTrue(Path(citation_workset_payload["citation_semantic_review_manifest_path"]).exists())
            self.assertIn("subagent_prompt_template", citation_workset_payload)
            self.assertIn("Default to delegating citation semantic review", citation_workset_payload["subagent_policy"])
            self.assertEqual(citation_workset_payload["merge_contract"]["single_writer"], "main_agent")
            citation_batch = self.read_json(citation_workset_payload["citation_batch_paths"][0])
            self.assertIn("batch_id", citation_batch)
            self.assertEqual(citation_batch["batch_kind"], "citation_semantic_review")
            self.assertLessEqual(len(citation_batch["citation_work_packages"]), 10)
            self.assertIn("required_return_shape", citation_batch)
            self.assertIn("forbidden_fields", citation_batch)
            self.assertIn("minimal_valid_example", citation_batch)
            self.assertIn("merge_notes", citation_batch)
            self.assertIn("subagent_prompt", citation_batch)
            self.assertIn("Default to delegating", citation_batch["merge_notes"])
            self.assertIn("Do not write DB", citation_batch["subagent_prompt"])
            self.assertIn("timeline_summaries", citation_workset_payload["merge_contract"]["merge_notes"])
            citation_reviews = []
            for package in self.citation_packages_from_payload(citation_workset_payload):
                citation_reviews.append(
                    {
                        "citation_work_key": package["citation_work_key"],
                        "topic": "runtime design",
                        "usage": "Used as background evidence in the fixture.",
                        "role_in_context": "background motivation for runtime design",
                        "keywords": ["runtime"],
                        "summary": "The cited work motivates the runtime wrapper.",
                        "key_reference_reason": "It is the only citation in the fixture scope.",
                    }
                )
            citation_path = root / "citation_payload.json"
            self.write_json(
                citation_path,
                {
                    "citation_semantic_reviews": citation_reviews,
                    "timeline_summaries": {
                        "early": "Earlier work motivates the runtime.",
                        "middle": "Middle-period work is not present in this fixture.",
                        "recent": "Recent work is not present in this fixture.",
                    },
                    "summary": "Citation analysis summary.",
                },
            )
            final = self.run_cmd(["persist_citation_analysis", "--db-path", db_path, "--payload-file", str(citation_path)])
            self.assertEqual(final.returncode, 0, final.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(final.stdout.decode("utf-8"))
            for key in (
                "digest_path",
                "references_path",
                "citation_analysis_path",
                "literature_matching_metadata_path",
                "citation_analysis_report_path",
            ):
                self.assertIn(key, payload)
                self.assertTrue(Path(payload[key]).exists(), key)
            self.assertIsNone(payload["error"])
            public_refs = json.loads(Path(payload["references_path"]).read_text(encoding="utf-8"))
            self.assertNotIn("selected_pattern", public_refs[0])
            self.assertNotIn("pattern_candidate", public_refs[0])
            self.assertNotIn("entry_index", public_refs[0])
            audit_path = Path(db_path).parent / "reference_parse_audit.json"
            self.assertTrue(audit_path.exists())
            audit_payload = json.loads(audit_path.read_text(encoding="utf-8"))
            self.assertEqual(audit_payload["items"][0]["selected_parse_pattern"], ref_package["recommended_parse_pattern"])

    def test_prepare_paths_do_not_call_legacy_subprocess_wrapper(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            lines = [
                "# Introduction",
                "Prior work [1] is relevant.",
                "# References",
                "[1] Smith. Useful Runtime Paper. 2020.",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")
            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            db_path = init["db_path"]
            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            self.assertEqual(self.run_cmd(["persist_analysis_plan", "--db-path", db_path, "--payload-file", str(plan_path)]).returncode, 0)

            module = load_run_analysis_module()
            self.assertFalse(hasattr(module, "_run_legacy"))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = module.handle_persist_references(Namespace(db_path=db_path, payload_file=""))
            self.assertEqual(code, 0)
            refs_payload = json.loads(stdout.getvalue())
            self.assertEqual(refs_payload["runtime_backend"], "analysis_runtime.references")

            package = self.reference_packages_from_payload(refs_payload)[0]
            refs_path = root / "refs_payload.json"
            self.write_json(
                refs_path,
                {
                    "reference_reviews": [
                        {
                            "reference_key": package["reference_key"],
                            "selected_parse_pattern": package["recommended_parse_pattern"],
                            "authors": ["Smith"],
                            "title": "Useful Runtime Paper",
                            "publication_year": 2020,
                            "review_notes": "Fixture reference parsed from numeric bibliography entry.",
                        }
                    ]
                },
            )
            core_refs = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(refs_path)])
            self.assertEqual(core_refs.returncode, 0)
            core_payload = json.loads(core_refs.stdout.decode("utf-8"))
            metadata_path = root / "metadata_payload.json"
            self.write_json(metadata_path, self.metadata_payload_from_packages(self.metadata_packages_from_payload(core_payload)))
            self.assertEqual(self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(metadata_path)]).returncode, 0)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = module.handle_persist_citation_analysis(Namespace(db_path=db_path, payload_file=""))
            self.assertEqual(code, 0)
            citation_payload = json.loads(stdout.getvalue())
            self.assertEqual(citation_payload["runtime_backend"], "analysis_runtime.citations")

    def test_reference_payload_rejects_old_fields_and_invalid_patterns_together(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            lines = [
                "# Introduction",
                "Prior work [1] is relevant.",
                "# References",
                "[1] Smith. Useful Runtime Paper. 2020.",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")
            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            db_path = init["db_path"]
            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            self.assertEqual(self.run_cmd(["persist_analysis_plan", "--db-path", db_path, "--payload-file", str(plan_path)]).returncode, 0)

            prepared = json.loads(self.run_cmd(["persist_references", "--db-path", db_path]).stdout.decode("utf-8"))
            package = self.reference_packages_from_payload(prepared)[0]
            payload_path = root / "bad_refs.json"
            self.write_json(
                payload_path,
                {
                    "items": [],
                    "selected_pattern": "fallback_raw_split",
                    "reference_reviews": [
                        {
                            "reference_key": package["reference_key"],
                            "selected_parse_pattern": "not_allowed",
                            "authors": ["Smith"],
                            "title": "Useful Runtime Paper",
                            "publication_year": 2020,
                        }
                    ],
                },
            )
            result = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(payload_path)])
            self.assertEqual(result.returncode, 2)
            response = json.loads(result.stdout.decode("utf-8"))
            details = "\n".join(response["error"]["details"])
            self.assertEqual(response["error"]["code"], "reference_payload_invalid")
            self.assertIn("forbidden top-level keys", details)
            self.assertIn("selected_parse_pattern must be one of", details)
            self.assertIn(package["reference_key"], response["allowed_parse_patterns_by_reference_key"])

    def test_reference_core_rejects_metadata_and_metadata_round_normalizes_aliases(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            lines = [
                "# Introduction",
                "Prior work [1] is relevant.",
                "# References",
                "[1] Smith. Useful Runtime Paper. Journal of Runtime Studies. arXiv:2004.10934. doi:10.1000/example. 2020.",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")
            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            db_path = init["db_path"]
            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            self.assertEqual(self.run_cmd(["persist_analysis_plan", "--db-path", db_path, "--payload-file", str(plan_path)]).returncode, 0)

            prepared = json.loads(self.run_cmd(["persist_references", "--db-path", db_path]).stdout.decode("utf-8"))
            package = self.reference_packages_from_payload(prepared)[0]
            bad_core_path = root / "refs_with_metadata.json"
            self.write_json(
                bad_core_path,
                {
                    "reference_reviews": [
                        {
                            "reference_key": package["reference_key"],
                            "selected_parse_pattern": package["recommended_parse_pattern"],
                            "authors": ["Smith"],
                            "title": "Useful Runtime Paper",
                            "publication_year": 2020,
                            "metadata": {"journal": "Journal of Runtime Studies"},
                        }
                    ],
                },
            )
            bad_core = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(bad_core_path)])
            self.assertEqual(bad_core.returncode, 2)
            bad_response = json.loads(bad_core.stdout.decode("utf-8"))
            bad_details = "\n".join(bad_response["error"]["details"])
            self.assertIn("metadata must be submitted through metadata_evidence_reviews", bad_details)

            core_path = root / "refs_core.json"
            self.write_json(
                core_path,
                {
                    "reference_reviews": [
                        {
                            "reference_key": package["reference_key"],
                            "selected_parse_pattern": package["recommended_parse_pattern"],
                            "authors": ["Smith"],
                            "title": "Useful Runtime Paper",
                            "publication_year": 2020,
                        }
                    ],
                },
            )
            core = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(core_path)])
            self.assertEqual(core.returncode, 0, core.stderr.decode("utf-8", errors="replace"))
            core_response = json.loads(core.stdout.decode("utf-8"))
            self.assertEqual(core_response["next_action"], "persist_references")
            self.assertNotIn("metadata_evidence_packages", core_response)
            self.assertIn("metadata_evidence_review_manifest_path", core_response)
            self.assertIn("metadata_evidence_batch_paths", core_response)
            self.assertIn("Default to delegating reference metadata evidence review", core_response["subagent_policy"])
            self.assertFalse(core_response["external_lookup_allowed"])
            self.assertEqual(core_response["merge_contract"]["single_writer"], "main_agent")
            self.assertIn("allowed_metadata_fields", core_response["instructions"])
            self.assertIn("locked_fields", core_response["instructions"])
            metadata_batch = self.read_json(core_response["metadata_evidence_batch_paths"][0])
            self.assertEqual(metadata_batch["batch_kind"], "reference_metadata_evidence_review")
            self.assertLessEqual(len(metadata_batch["metadata_evidence_packages"]), 10)
            self.assertIn("canonical_metadata_fields", metadata_batch)
            self.assertIn("forbidden_fields", metadata_batch)
            self.assertIn("subagent_prompt", metadata_batch)
            self.assertFalse(metadata_batch["external_lookup_allowed"])
            self.assertIn("This is not a metadata discovery task", metadata_batch["subagent_prompt"])
            self.assertTrue(any("Crossref" in action for action in metadata_batch["forbidden_actions"]))
            self.assertIn("Do not write DB", metadata_batch["subagent_prompt"])
            self.assertIn("author", metadata_batch["forbidden_fields"])
            self.assertIn("ref_index", metadata_batch["forbidden_fields"])

            metadata_path = root / "metadata_payload.json"
            metadata_package = self.metadata_packages_from_payload(core_response)[0]

            old_metadata_path = root / "old_metadata_payload.json"
            self.write_json(
                old_metadata_path,
                {
                    "metadata_reviews": [
                        {
                            "reference_key": metadata_package["reference_key"],
                            "status": "enriched",
                            "metadata": {"DOI": "10.1000/example"},
                        }
                    ]
                },
            )
            old_result = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(old_metadata_path)])
            self.assertEqual(old_result.returncode, 2)
            old_response = json.loads(old_result.stdout.decode("utf-8"))
            self.assertIn("metadata_reviews[] is not accepted", old_response["error"]["message"])

            unsupported_metadata_path = root / "unsupported_metadata_payload.json"
            self.write_json(
                unsupported_metadata_path,
                {
                    "metadata_evidence_reviews": [
                        {
                            "reference_key": metadata_package["reference_key"],
                            "status": "fields_extracted",
                            "metadata": {"DOI": "10.9999/not-in-source"},
                            "evidence_note": "This value is not visible in the batch JSON evidence.",
                        }
                    ]
                },
            )
            unsupported_result = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(unsupported_metadata_path)])
            self.assertEqual(unsupported_result.returncode, 2)
            unsupported_response = json.loads(unsupported_result.stdout.decode("utf-8"))
            self.assertEqual(unsupported_response["error"]["code"], "reference_metadata_payload_invalid")
            self.assertIn("metadata_without_local_evidence", "\n".join(unsupported_response["error"]["details"]))

            self.write_json(
                metadata_path,
                {
                    "metadata_evidence_reviews": [
                        {
                            "reference_key": metadata_package["reference_key"],
                            "status": "fields_extracted",
                            "metadata": {
                                "journal": "Journal of Runtime Studies",
                                "archiveID": "2004.10934",
                                "doi": "10.1000/example",
                                "unknownField": "ignored",
                            },
                            "evidence_note": "Metadata is present in metadata context.",
                        }
                    ]
                },
            )
            result = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(metadata_path)])
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            response = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(response["next_action"], "persist_citation_analysis")
            warnings = "\n".join(response["warnings"])
            self.assertIn("reference_metadata_alias_normalized", warnings)
            self.assertIn("reference_metadata_field_unrecognized", warnings)

            with sqlite3.connect(db_path) as connection:
                metadata_json = connection.execute("SELECT metadata_json FROM reference_items WHERE ref_index = 0").fetchone()[0]
            metadata = json.loads(metadata_json)
            self.assertEqual(metadata["publicationTitle"], "Journal of Runtime Studies")
            self.assertEqual(metadata["archiveID"], "arXiv:2004.10934")
            self.assertEqual(metadata["DOI"], "10.1000/example")
            self.assertNotIn("unknownField", metadata)

    def test_reference_split_reviews_regenerate_packages_before_reference_review(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            lines = [
                "# Introduction",
                "Prior work [1] and [2] are relevant.",
                "# References",
                "Smith, J. Paper A. 2020 Jones, M. Paper B. 2021.",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")
            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            db_path = init["db_path"]
            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            self.assertEqual(self.run_cmd(["persist_analysis_plan", "--db-path", db_path, "--payload-file", str(plan_path)]).returncode, 0)
            digest_path = root / "digest_payload.json"
            self.write_json(digest_path, self.digest_payload())
            self.assertEqual(self.run_cmd(["persist_digest", "--db-path", db_path, "--payload-file", str(digest_path)]).returncode, 0)

            prepared = json.loads(self.run_cmd(["persist_references", "--db-path", db_path]).stdout.decode("utf-8"))
            self.assertTrue(prepared["requires_split_review"])
            split_package = self.split_packages_from_payload(prepared)[0]

            split_path = root / "split_payload.json"
            self.write_json(
                split_path,
                {
                    "split_reviews": [
                        {
                            "block_key": split_package["block_key"],
                            "action": "replace_with_corrected_reference_texts",
                            "corrected_reference_texts": [
                                "Smith， J. Paper A. 2020",
                                "Jones, M. Paper B. 2021.",
                            ],
                        }
                    ]
                },
            )
            split_result = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(split_path)])
            self.assertEqual(split_result.returncode, 0, split_result.stderr.decode("utf-8", errors="replace"))
            regenerated = json.loads(split_result.stdout.decode("utf-8"))
            self.assertFalse(regenerated["requires_split_review"])
            regenerated_packages = self.reference_packages_from_payload(regenerated)
            self.assertEqual(len(regenerated_packages), 2)
            self.assertEqual(regenerated["next_action"], "persist_references")

            refs_path = root / "refs_payload.json"
            reviews = []
            for package, author, title, year in [
                (regenerated_packages[0], ["Smith, J."], "Paper A", 2020),
                (regenerated_packages[1], ["Jones, M."], "Paper B", 2021),
            ]:
                reviews.append(
                    {
                        "reference_key": package["reference_key"],
                        "selected_parse_pattern": package["recommended_parse_pattern"],
                        "authors": author,
                        "title": title,
                        "publication_year": year,
                    }
                )
            self.write_json(refs_path, {"reference_reviews": reviews})
            refs = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(refs_path)])
            self.assertEqual(refs.returncode, 0, refs.stderr.decode("utf-8", errors="replace"))
            refs_payload = json.loads(refs.stdout.decode("utf-8"))
            self.assertEqual(refs_payload["stored_reference_items"], 2)

    def test_reference_split_review_missing_tokens_returns_diagnostics(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            lines = [
                "# Introduction",
                "Prior work [1] and [2] are relevant.",
                "# References",
                "Smith, J. Paper A. 2020 Jones, M. Paper B. 2021.",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")
            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            db_path = init["db_path"]
            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            self.assertEqual(self.run_cmd(["persist_analysis_plan", "--db-path", db_path, "--payload-file", str(plan_path)]).returncode, 0)
            digest_path = root / "digest_payload.json"
            self.write_json(digest_path, self.digest_payload())
            self.assertEqual(self.run_cmd(["persist_digest", "--db-path", db_path, "--payload-file", str(digest_path)]).returncode, 0)

            prepared = json.loads(self.run_cmd(["persist_references", "--db-path", db_path]).stdout.decode("utf-8"))
            split_package = self.split_packages_from_payload(prepared)[0]
            split_path = root / "bad_conservation_split.json"
            self.write_json(
                split_path,
                {
                    "split_reviews": [
                        {
                            "block_key": split_package["block_key"],
                            "action": "replace_with_corrected_reference_texts",
                            "corrected_reference_texts": [
                                "Smith, J. Paper A. 2020",
                                "Jones, M. 2021.",
                            ],
                        }
                    ]
                },
            )
            result = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(split_path)])
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(payload["error"]["code"], "reference_entry_splitting_failed")
            diagnostics = payload["error"]["diagnostics"]
            self.assertLess(diagnostics["coverage_ratio"], 1.0)
            self.assertIn("missing_tokens_sample", diagnostics)
            self.assertGreater(diagnostics["missing_token_count"], 0)

    def test_reference_split_review_remaining_suspicion_warns_and_continues(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            lines = [
                "# Introduction",
                "Prior web resources [1] are relevant.",
                "# References",
                "YOLO-v8.",
                "In https://github.com/ultralytics/ultralytics.",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")
            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            db_path = init["db_path"]
            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            self.assertEqual(self.run_cmd(["persist_analysis_plan", "--db-path", db_path, "--payload-file", str(plan_path)]).returncode, 0)
            digest_path = root / "digest_payload.json"
            self.write_json(digest_path, self.digest_payload())
            self.assertEqual(self.run_cmd(["persist_digest", "--db-path", db_path, "--payload-file", str(digest_path)]).returncode, 0)

            prepared = json.loads(self.run_cmd(["persist_references", "--db-path", db_path]).stdout.decode("utf-8"))
            self.assertTrue(prepared["requires_split_review"])
            split_package = self.split_packages_from_payload(prepared)[0]
            split_path = root / "web_split_payload.json"
            self.write_json(
                split_path,
                {
                    "split_reviews": [
                        {
                            "block_key": split_package["block_key"],
                            "action": "replace_with_corrected_reference_texts",
                            "corrected_reference_texts": [
                                "YOLO-v8.",
                                "In https://github.com/ultralytics/ultralytics.",
                            ],
                        }
                    ]
                },
            )
            result = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(split_path)])
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertFalse(payload["requires_split_review"])
            self.assertIn("reference_core_review_manifest_path", payload)
            self.assertNotIn("reference_review_packages", payload)
            self.assertTrue(any("reference_boundary_suspicion_after_review" in warning for warning in payload["warnings"]))
            audit_path = Path(db_path).parent / "reference_split_review_audit.json"
            self.assertTrue(audit_path.exists())
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            self.assertTrue(audit["downgraded_suspect_blocks"])

    def test_reference_split_review_validation_errors_are_aggregated(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            lines = [
                "# Introduction",
                "Prior work [1], [2], [3], and [4] are relevant.",
                "# References",
                "Smith, J. Paper A. 2020 Jones, M. Paper B. 2021.",
                "Brown, C. Paper C. 2022 White, D. Paper D. 2023.",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")
            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            db_path = init["db_path"]
            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            self.assertEqual(self.run_cmd(["persist_analysis_plan", "--db-path", db_path, "--payload-file", str(plan_path)]).returncode, 0)
            digest_path = root / "digest_payload.json"
            self.write_json(digest_path, self.digest_payload())
            self.assertEqual(self.run_cmd(["persist_digest", "--db-path", db_path, "--payload-file", str(digest_path)]).returncode, 0)

            prepared = json.loads(self.run_cmd(["persist_references", "--db-path", db_path]).stdout.decode("utf-8"))
            split_packages = self.split_packages_from_payload(prepared)
            self.assertGreaterEqual(len(split_packages), 2)
            first = split_packages[0]["block_key"]
            second = split_packages[1]["block_key"]

            bad_path = root / "bad_split_payload.json"
            self.write_json(
                bad_path,
                {
                    "split_reviews": [
                        {"block_key": "block-999", "action": "keep"},
                        {"block_key": first, "action": "explode"},
                        {
                            "block_key": second,
                            "action": "replace_with_corrected_reference_texts",
                            "corrected_reference_texts": [],
                        },
                    ]
                },
            )
            bad = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(bad_path)])
            self.assertEqual(bad.returncode, 2)
            response = json.loads(bad.stdout.decode("utf-8"))
            details = "\n".join(response["error"]["details"])
            self.assertEqual(response["error"]["code"], "reference_split_review_invalid")
            self.assertIn("unknown block_key: block-999", details)
            self.assertIn(".action must be one of", details)
            self.assertIn(".corrected_reference_texts must be a non-empty string array", details)

    def test_citation_payload_uses_work_keys_and_runtime_derives_timeline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            lines = [
                "# Introduction",
                "Prior work [1] is relevant.",
                "# References",
                "[1] Smith. Useful Runtime Paper. 2020.",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")
            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            db_path = init["db_path"]
            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            self.assertEqual(self.run_cmd(["persist_analysis_plan", "--db-path", db_path, "--payload-file", str(plan_path)]).returncode, 0)
            digest_path = root / "digest_payload.json"
            self.write_json(digest_path, self.digest_payload())
            self.assertEqual(self.run_cmd(["persist_digest", "--db-path", db_path, "--payload-file", str(digest_path)]).returncode, 0)

            refs_prepared = json.loads(self.run_cmd(["persist_references", "--db-path", db_path]).stdout.decode("utf-8"))
            ref_package = self.reference_packages_from_payload(refs_prepared)[0]
            refs_path = root / "refs_payload.json"
            self.write_json(
                refs_path,
                {
                    "reference_reviews": [
                        {
                            "reference_key": ref_package["reference_key"],
                            "selected_parse_pattern": ref_package["recommended_parse_pattern"],
                            "authors": ["Smith"],
                            "title": "Useful Runtime Paper",
                            "publication_year": 2020,
                        }
                    ]
                },
            )
            core_refs = self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(refs_path)])
            self.assertEqual(core_refs.returncode, 0)
            core_payload = json.loads(core_refs.stdout.decode("utf-8"))
            metadata_path = root / "metadata_payload.json"
            self.write_json(metadata_path, self.metadata_payload_from_packages(self.metadata_packages_from_payload(core_payload)))
            self.assertEqual(self.run_cmd(["persist_references", "--db-path", db_path, "--payload-file", str(metadata_path)]).returncode, 0)

            citation_prepared = json.loads(self.run_cmd(["persist_citation_analysis", "--db-path", db_path]).stdout.decode("utf-8"))
            package = self.citation_packages_from_payload(citation_prepared)[0]
            self.assertIn("Default to delegating citation semantic review", citation_prepared["subagent_policy"])
            self.assertEqual(citation_prepared["merge_contract"]["single_writer"], "main_agent")
            citation_batch = self.read_json(citation_prepared["citation_batch_paths"][0])
            self.assertIn("subagent_prompt", citation_batch)
            self.assertIn("Do not write DB", citation_batch["subagent_prompt"])
            self.assertIn("timeline_summaries", citation_batch["subagent_prompt"])
            self.assertIn("global summary", citation_batch["subagent_prompt"])
            self.assertIn("ref_index", citation_batch["subagent_prompt"])

            bad_path = root / "bad_citation.json"
            self.write_json(
                bad_path,
                {
                    "items": [],
                    "citation_semantic_reviews": [
                        {
                            "citation_work_key": package["citation_work_key"],
                            "ref_index": 0,
                            "function": "background",
                            "topic": "runtime design",
                            "usage": "Used as background evidence.",
                            "role_in_context": "background motivation",
                            "keywords": ["runtime"],
                            "summary": "The cited work motivates the runtime wrapper.",
                        }
                    ],
                    "timeline_summaries": {"early": "Early.", "middle": "Middle.", "recent": "Recent."},
                    "summary": "Citation summary.",
                },
            )
            bad = self.run_cmd(["persist_citation_analysis", "--db-path", db_path, "--payload-file", str(bad_path)])
            self.assertEqual(bad.returncode, 2)
            bad_response = json.loads(bad.stdout.decode("utf-8"))
            bad_details = "\n".join(bad_response["error"]["details"])
            self.assertIn("forbidden top-level keys", bad_details)
            self.assertIn("contains forbidden internal fields", bad_details)

            good_path = root / "citation_payload.json"
            self.write_json(
                good_path,
                {
                    "citation_semantic_reviews": [
                        {
                            "citation_work_key": package["citation_work_key"],
                            "topic": "runtime design",
                            "usage": "Used as background evidence.",
                            "role_in_context": "background motivation",
                            "keywords": ["runtime"],
                            "summary": "The cited work motivates the runtime wrapper.",
                            "key_reference_reason": "It is the fixture's only mapped citation.",
                        }
                    ],
                    "timeline_summaries": {"early": "Early.", "middle": "Middle.", "recent": "Recent."},
                    "summary": "Citation summary.",
                },
            )
            final = self.run_cmd(["persist_citation_analysis", "--db-path", db_path, "--payload-file", str(good_path)])
            self.assertEqual(final.returncode, 0, final.stderr.decode("utf-8", errors="replace"))
            response = json.loads(final.stdout.decode("utf-8"))
            citation_json = json.loads(Path(response["citation_analysis_path"]).read_text(encoding="utf-8"))
            self.assertEqual(citation_json["timeline"]["early"]["ref_indexes"], [0])
            self.assertEqual(citation_json["timeline"]["mid"]["ref_indexes"], [])
            self.assertEqual(citation_json["timeline"]["recent"]["ref_indexes"], [])

    def test_run_analysis_owns_normal_runtime_orchestration(self):
        text = RUN_ANALYSIS.read_text(encoding="utf-8")
        self.assertNotIn("def _run_legacy", text)
        self.assertNotIn("subprocess.run", text)
        self.assertNotIn("LEGACY_STAGE_RUNTIME", text)
        self.assertNotIn("LEGACY_RUNTIME_DB", text)
        self.assertIn("stages.persist_analysis_plan", text)
        self.assertIn("stages.persist_digest", text)
        self.assertIn("references.persist_references", text)
        self.assertIn("citations.persist_citation_analysis", text)

    def test_analysis_runtime_package_shape_is_tidy(self):
        runtime_dir = ANALYSIS_SCRIPTS / "analysis_runtime"
        expected_files = {
            "agent_work.py",
            "algorithm_adapter.py",
            "citations.py",
            "deterministic_core.py",
            "gate_contract.py",
            "payload_normalization.py",
            "references.py",
            "runtime.py",
            "runtime_db.py",
            "stages.py",
        }
        obsolete_files = {
            "algorithm_core.py",
            "db.py",
            "digest.py",
            "local_handlers.py",
            "plan.py",
            "rendering.py",
            "source.py",
        }
        for filename in expected_files:
            self.assertTrue((runtime_dir / filename).exists(), filename)
        for filename in obsolete_files:
            self.assertFalse((runtime_dir / filename).exists(), filename)

    def test_analysis_runtime_has_no_cross_skill_runtime_dependency(self):
        forbidden_snippets = (
            "literature-digest/scripts",
            "literature-digest/assets",
            "LITERATURE_DIGEST_",
            "LITERATURE_ANALYSIS_OUTPUT_DIR",
            "LITERATURE_ANALYSIS_DISABLE_PYMUPDF4LLM",
            "LEGACY_",
            "from .legacy",
            "analysis_runtime.legacy",
            "from .stage_adapter",
            "call_stage_handler",
            "stage_adapter",
            "spec_from_file_location(",
        )
        self.assertFalse((ANALYSIS_SCRIPTS / "analysis_runtime" / "legacy.py").exists())
        self.assertFalse((ANALYSIS_SCRIPTS / "analysis_runtime" / "stage_adapter.py").exists())
        for path in ANALYSIS_SCRIPTS.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for snippet in forbidden_snippets:
                self.assertNotIn(snippet, text, str(path.relative_to(REPO_ROOT)))

    def test_analysis_runtime_assets_are_local(self):
        assets = REPO_ROOT / "literature-analysis" / "assets"
        for relative_path in (
            "templates/digest.zh-CN.md.j2",
            "templates/digest.en-US.md.j2",
            "templates/citation_analysis.zh-CN.md.j2",
            "templates/citation_analysis.en-US.md.j2",
            "templates/references.json.j2",
            "templates/citation_analysis.json.j2",
            "templates/literature_matching_metadata.json.j2",
            "render_schemas/digest.schema.json",
            "render_schemas/references.schema.json",
            "render_schemas/citation_analysis.schema.json",
        ):
            self.assertTrue((assets / relative_path).exists(), relative_path)

    def test_status_returns_local_gate_contract(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            lines = [
                "# Introduction",
                "Prior work [1] is relevant.",
                "# References",
                "[1] Smith. Useful Runtime Paper. 2020.",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")
            init = json.loads(
                self.run_cmd(["init_runtime", "--source-path", str(source), "--working-dir", str(root)]).stdout.decode("utf-8")
            )
            plan_path = root / "plan.json"
            self.write_json(plan_path, self.outline_payload(lines))
            self.assertEqual(self.run_cmd(["persist_analysis_plan", "--db-path", init["db_path"], "--payload-file", str(plan_path)]).returncode, 0)
            digest_path = root / "digest_payload.json"
            self.write_json(digest_path, self.digest_payload())
            self.assertEqual(self.run_cmd(["persist_digest", "--db-path", init["db_path"], "--payload-file", str(digest_path)]).returncode, 0)
            status = self.run_cmd(["status", "--db-path", init["db_path"]])
            self.assertEqual(status.returncode, 0, status.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(status.stdout.decode("utf-8"))
            self.assertIn("next_action", payload)
            self.assertEqual(payload["next_action"], "persist_references")
            self.assertIn("missing_prerequisites", payload)
            self.assertIn("execution_note", payload)
            self.assertIn("instruction_refs", payload)
            self.assertIn("quality_directives", payload)
            self.assertIn("allowed_payload_shape", payload)
            self.assertIn("field_guidance", payload)
            self.assertIn("Default to subagent delegation", payload["field_guidance"]["subagents"])
            self.assertIn("single DB writer", payload["field_guidance"]["subagents"])
            self.assertEqual(payload["runtime_backend"], "analysis_runtime.gate_contract")
            for ref in payload["instruction_refs"]:
                self.assertTrue(ref["path"].startswith("references/"))
                self.assertNotIn("gate_runtime_interface.md", ref["path"])
                self.assertNotIn("sql_playbook.md", ref["path"])


class LiteratureAnalysisGuidanceTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (REPO_ROOT / relative_path).read_text(encoding="utf-8")

    def test_skill_indexes_owned_reference_docs(self):
        skill_md = self.read("literature-analysis/SKILL.md")
        for name in (
            "source_and_plan.md",
            "digest_generation.md",
            "reference_extraction.md",
            "citation_analysis.md",
            "finalization_and_recovery.md",
        ):
            self.assertIn(f"references/{name}", skill_md)
        self.assertIn("正常执行只读取本 skill 的阶段指南和 runtime 返回的 JIT 指令", skill_md)

    def test_analysis_references_avoid_old_script_commands(self):
        for path in (REPO_ROOT / "literature-analysis" / "references").glob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("literature-digest/scripts", text, path.name)
            self.assertNotIn("gate_runtime.py", text, path.name)
            self.assertNotIn("sql_playbook.md", text, path.name)
        reference_doc = self.read("literature-analysis/references/reference_extraction.md")
        citation_doc = self.read("literature-analysis/references/citation_analysis.md")
        self.assertIn("Subagent prompt template", reference_doc)
        self.assertIn("selected_parse_pattern", reference_doc)
        self.assertIn("allowed_parse_patterns_by_reference_key", reference_doc)
        self.assertIn("Subagent prompt template", citation_doc)
        self.assertIn("citation_work_key", citation_doc)
        self.assertIn("timeline_summaries", citation_doc)


if __name__ == "__main__":
    unittest.main()
