import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE_RUNTIME = REPO_ROOT / "literature-digest" / "scripts" / "stage_runtime.py"
GATE_RUNTIME = REPO_ROOT / "literature-digest" / "scripts" / "gate_runtime.py"


class StageRuntimeTests(unittest.TestCase):
    def run_cmd(self, args: list[str], *, input_obj: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(STAGE_RUNTIME), *args],
            input=None if input_obj is None else json.dumps(input_obj, ensure_ascii=False).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def run_gate(self, db_path: Path) -> dict:
        result = subprocess.run(
            [sys.executable, str(GATE_RUNTIME), "--db-path", str(db_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
        return json.loads(result.stdout.decode("utf-8"))

    def _outline_payload(self, lines: list[str], *, citation_title: str = "Introduction", citation_line_end: int | None = None) -> dict:
        outline_nodes: list[dict] = []
        references_line = None
        for line_no, line in enumerate(lines, start=1):
            if line.startswith("# "):
                title = line[2:].strip()
                outline_nodes.append(
                    {
                        "node_id": f"n{len(outline_nodes) + 1}",
                        "heading_level": 1,
                        "title": title,
                        "line_start": line_no,
                        "line_end": line_no,
                        "parent_node_id": None,
                        "metadata": {},
                    }
                )
                if title.lower() == "references":
                    references_line = line_no
        if references_line is None:
            raise AssertionError("fixture must include a References heading")
        citation_end = citation_line_end if citation_line_end is not None else max(1, references_line - 1)
        return {
            "outline_nodes": outline_nodes,
            "references_scope": {
                "section_title": "References",
                "line_start": references_line,
                "line_end": len(lines),
                "metadata": {},
            },
            "citation_scope": {
                "section_title": citation_title,
                "line_start": 1,
                "line_end": citation_end,
                "metadata": {"selection_reason": "fixture scope", "covered_sections": [citation_title]},
            },
        }

    def _digest_payload(self) -> dict:
        return {
            "digest_slots": {
                "tldr": {"paragraphs": ["digest body", "second paragraph"]},
                "research_question_and_contributions": {
                    "research_question": "How to summarize the paper?",
                    "contributions": ["Contribution A", "Contribution B"],
                },
                "method_highlights": {"items": ["Method point"]},
                "key_results": {"items": ["Result point"]},
                "limitations_and_reproducibility": {"items": ["Limitation point"]},
            },
            "section_summaries": [
                {"source_heading": "Introduction", "items": ["Intro summary"]},
                {"source_heading": "References", "items": ["Reference appendix summary"]},
            ],
        }

    def _reference_payload(self, raw: str, *, year: int = 2020, author: list[str] | None = None, confidence: float = 0.9) -> dict:
        return {
            "entries": [{"entry_index": 0, "raw": raw}],
            "batches": [{"batch_index": 0, "entry_start": 0, "entry_end": 0}],
            "items": [
                {
                    "ref_index": 0,
                    "author": author or ["Smith"],
                    "title": "Paper A",
                    "year": year,
                    "raw": raw,
                    "confidence": confidence,
                }
            ],
        }

    def test_stage_runtime_can_drive_minimal_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            source_path = td_path / "paper.md"
            db_path = td_path / ".literature_digest_tmp" / "literature_digest.db"
            source_path.write_text(
                "\n".join(
                    [
                        "# 1 Introduction",
                        "Prior work [1].",
                        "# 2 References",
                        "[1] Smith. Paper A. 2020.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            bootstrap = self.run_cmd(
                [
                    "bootstrap_runtime_db",
                    "--db-path",
                    str(db_path),
                    "--source-path",
                    str(source_path),
                    "--language",
                    "zh-CN",
                    "--model",
                    "test-model",
                ]
            )
            self.assertEqual(bootstrap.returncode, 0, bootstrap.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(self.run_gate(db_path)["next_action"], "normalize_source")

            normalize = self.run_cmd(["normalize_source", "--db-path", str(db_path)])
            self.assertEqual(normalize.returncode, 0, normalize.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(self.run_gate(db_path)["next_action"], "persist_outline_and_scopes")

            outline_payload = {
                "outline_nodes": [
                    {"node_id": "n1", "heading_level": 1, "title": "Introduction", "line_start": 1, "line_end": 2, "parent_node_id": None, "metadata": {}},
                    {"node_id": "n2", "heading_level": 1, "title": "References", "line_start": 3, "line_end": 4, "parent_node_id": None, "metadata": {}},
                ],
                "references_scope": {"section_title": "References", "line_start": 3, "line_end": 4, "metadata": {}},
                "citation_scope": {
                    "section_title": "Introduction",
                    "line_start": 1,
                    "line_end": 2,
                    "metadata": {"selection_reason": "review signals concentrated in the introduction"},
                },
            }
            outline = self.run_cmd(["persist_outline_and_scopes", "--db-path", str(db_path)], input_obj=outline_payload)
            self.assertEqual(outline.returncode, 0, outline.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(self.run_gate(db_path)["next_action"], "persist_digest")

            digest = self.run_cmd(
                ["persist_digest", "--db-path", str(db_path)],
                input_obj={
                    "digest_slots": {
                        "tldr": {"paragraphs": ["digest body", "second paragraph"]},
                        "research_question_and_contributions": {
                            "research_question": "How to summarize the paper?",
                            "contributions": ["Contribution A", "Contribution B"],
                        },
                        "method_highlights": {"items": ["Method point"]},
                        "key_results": {"items": ["Result point"]},
                        "limitations_and_reproducibility": {"items": ["Limitation point"]},
                    },
                    "section_summaries": [
                        {"source_heading": "Introduction", "items": ["Intro summary"]},
                        {"source_heading": "References", "items": ["Reference appendix summary"]},
                    ],
                },
            )
            self.assertEqual(digest.returncode, 0, digest.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(self.run_gate(db_path)["next_action"], "persist_references")

            references = self.run_cmd(
                ["persist_references", "--db-path", str(db_path)],
                input_obj={
                    "entries": [{"entry_index": 0, "raw": "[1] Smith. Paper A. 2020."}],
                    "batches": [{"batch_index": 0, "entry_start": 0, "entry_end": 0}],
                    "items": [{"ref_index": 0, "author": ["Smith"], "title": "Paper A", "year": 2020, "raw": "[1] Smith. Paper A. 2020.", "confidence": 0.9}],
                },
            )
            self.assertEqual(references.returncode, 0, references.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(self.run_gate(db_path)["next_action"], "prepare_citation_workset")

            mentions = self.run_cmd(["prepare_citation_workset", "--db-path", str(db_path)])
            self.assertEqual(mentions.returncode, 0, mentions.stderr.decode("utf-8", errors="replace"))
            mention_payload = json.loads(mentions.stdout.decode("utf-8"))
            self.assertTrue(Path(mention_payload["review_path"]).exists())
            self.assertEqual(self.run_gate(db_path)["next_action"], "persist_citation_semantics")

            semantics = self.run_cmd(
                ["persist_citation_semantics", "--db-path", str(db_path)],
                input_obj={
                    "items": [
                        {
                            "ref_index": 0,
                            "function": "background",
                            "summary": "Used as background.",
                            "confidence": 0.9,
                        }
                    ]
                },
            )
            self.assertEqual(semantics.returncode, 0, semantics.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(self.run_gate(db_path)["next_action"], "persist_citation_summary")

            citation_summary = self.run_cmd(
                ["persist_citation_summary", "--db-path", str(db_path)],
                input_obj={"summary": "The introduction groups prior work as background literature."},
            )
            self.assertEqual(citation_summary.returncode, 0, citation_summary.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(self.run_gate(db_path)["next_action"], "render_and_validate")

            render = self.run_cmd(["render_and_validate", "--db-path", str(db_path), "--mode", "render"])
            self.assertEqual(render.returncode, 0, render.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(render.stdout.decode("utf-8"))
            self.assertTrue(Path(payload["digest_path"]).exists())
            self.assertTrue(Path(payload["references_path"]).exists())
            self.assertTrue(Path(payload["citation_analysis_path"]).exists())
            self.assertTrue(Path(payload["citation_analysis_report_path"]).exists())
            digest_text = Path(payload["digest_path"]).read_text(encoding="utf-8")
            self.assertIn("## TL;DR", digest_text)
            self.assertIn("Contribution A", digest_text)
            citation_text = Path(payload["citation_analysis_report_path"]).read_text(encoding="utf-8")
            citation_json = json.loads(Path(payload["citation_analysis_path"]).read_text(encoding="utf-8"))
            self.assertIn("按功能归类", citation_text)
            self.assertEqual(citation_json["summary"], "The introduction groups prior work as background literature.")

    def test_main_path_no_longer_accepts_late_override_arguments(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            source_path = td_path / "paper.md"
            db_path = td_path / ".literature_digest_tmp" / "literature_digest.db"
            source_path.write_text("# 1 Introduction\n[1]\n", encoding="utf-8")

            bootstrap = self.run_cmd(
                [
                    "bootstrap_runtime_db",
                    "--db-path",
                    str(db_path),
                    "--source-path",
                    str(source_path),
                    "--language",
                    "zh-CN",
                ]
            )
            self.assertEqual(bootstrap.returncode, 0)

            normalize_override = self.run_cmd(["normalize_source", "--db-path", str(db_path), "--source-path", str(source_path)])
            self.assertEqual(normalize_override.returncode, 2)

            citation_override = self.run_cmd(["prepare_citation_workset", "--db-path", str(db_path), "--scope-start", "1", "--scope-end", "2"])
            self.assertEqual(citation_override.returncode, 2)

    def test_persist_outline_and_scopes_requires_runtime_shape(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            source_path = td_path / "paper.md"
            db_path = td_path / ".literature_digest_tmp" / "literature_digest.db"
            source_path.write_text("# 1 Introduction\nText.\n", encoding="utf-8")
            self.assertEqual(
                self.run_cmd(
                    ["bootstrap_runtime_db", "--db-path", str(db_path), "--source-path", str(source_path), "--language", "zh-CN"]
                ).returncode,
                0,
            )
            self.assertEqual(self.run_cmd(["normalize_source", "--db-path", str(db_path)]).returncode, 0)
            invalid = self.run_cmd(
                ["persist_outline_and_scopes", "--db-path", str(db_path)],
                input_obj={
                    "outline_nodes": [{"node_id": "n1", "heading_level": 1, "title": "Introduction", "line_start": 1, "line_end": 2}],
                    "references_scope": {"section_title": "References", "line_start": 3, "line_end": 4},
                    "citation_scope": {"section_title": "Introduction", "line_start": 1, "line_end": 2, "metadata": {}},
                },
            )
            self.assertEqual(invalid.returncode, 2)
            payload = json.loads(invalid.stdout.decode("utf-8"))
            self.assertIn("parent_node_id", payload["error"]["message"])

    def test_prepare_citation_workset_filters_noise_and_writes_review_view(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            source_path = td_path / "paper.md"
            db_path = td_path / ".literature_digest_tmp" / "literature_digest.db"
            source_path.write_text(
                "\n".join(
                    [
                        "# Introduction",
                        "![figure](assets/figure.png)",
                        "See https://example.com/report.pdf for details.",
                        "Updated 2024-03-01.",
                        "Prior work [1].",
                        "# References",
                        "[1] Smith. Paper A. 2020.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(self.run_cmd(["bootstrap_runtime_db", "--db-path", str(db_path), "--source-path", str(source_path)]).returncode, 0)
            self.assertEqual(self.run_cmd(["normalize_source", "--db-path", str(db_path)]).returncode, 0)
            lines = source_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(self.run_cmd(["persist_outline_and_scopes", "--db-path", str(db_path)], input_obj=self._outline_payload(lines, citation_line_end=5)).returncode, 0)
            self.assertEqual(self.run_cmd(["persist_digest", "--db-path", str(db_path)], input_obj=self._digest_payload()).returncode, 0)
            self.assertEqual(self.run_cmd(["persist_references", "--db-path", str(db_path)], input_obj=self._reference_payload("[1] Smith. Paper A. 2020.")).returncode, 0)
            workset = self.run_cmd(["prepare_citation_workset", "--db-path", str(db_path)])
            self.assertEqual(workset.returncode, 0, workset.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(workset.stdout.decode("utf-8"))
            self.assertEqual(payload["resolved_items"], 1)
            self.assertGreater(payload["filtered_false_positive_mentions"], 0)
            review = json.loads(Path(payload["review_path"]).read_text(encoding="utf-8"))
            self.assertEqual(review["items"][0]["ref_index"], 0)
            self.assertEqual(review["items"][0]["mention_count"], 1)
            self.assertEqual(
                self.run_cmd(
                    ["persist_citation_semantics", "--db-path", str(db_path)],
                    input_obj={"items": [{"ref_index": 0, "function": "background", "summary": "Used as background.", "confidence": 0.9}]},
                ).returncode,
                0,
            )
            self.assertEqual(
                self.run_cmd(
                    ["persist_citation_summary", "--db-path", str(db_path)],
                    input_obj={"summary": "The review section mainly cites one background work."},
                ).returncode,
                0,
            )
            render = self.run_cmd(["render_and_validate", "--db-path", str(db_path), "--mode", "render"])
            self.assertEqual(render.returncode, 0, render.stderr.decode("utf-8", errors="replace"))
            render_payload = json.loads(render.stdout.decode("utf-8"))
            self.assertIn("citation_false_positive_filtered", render_payload["warnings"])

    def test_persist_references_normalizes_trailing_year_and_low_confidence_warning(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            source_path = td_path / "paper.md"
            db_path = td_path / ".literature_digest_tmp" / "literature_digest.db"
            source_path.write_text("# Introduction\nText\n", encoding="utf-8")
            self.assertEqual(self.run_cmd(["bootstrap_runtime_db", "--db-path", str(db_path), "--source-path", str(source_path)]).returncode, 0)
            self.assertEqual(self.run_cmd(["normalize_source", "--db-path", str(db_path)]).returncode, 0)
            self.assertEqual(
                self.run_cmd(
                    ["persist_outline_and_scopes", "--db-path", str(db_path)],
                    input_obj={
                        "outline_nodes": [{"node_id": "n1", "heading_level": 1, "title": "Introduction", "line_start": 1, "line_end": 2, "parent_node_id": None, "metadata": {}}],
                        "references_scope": {"section_title": "Introduction", "line_start": 1, "line_end": 2, "metadata": {}},
                        "citation_scope": {"section_title": "Introduction", "line_start": 1, "line_end": 2, "metadata": {}},
                    },
                ).returncode,
                0,
            )
            self.assertEqual(self.run_cmd(["persist_digest", "--db-path", str(db_path)], input_obj=self._digest_payload()).returncode, 0)
            references = self.run_cmd(
                ["persist_references", "--db-path", str(db_path)],
                input_obj=self._reference_payload(
                    "Smith, J. Something useful. arXiv:1704.04861. 2017.",
                    year=1704,
                    author=["Smith, J.; Doe, K."],
                    confidence=0.3,
                ),
            )
            self.assertEqual(references.returncode, 0, references.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(references.stdout.decode("utf-8"))
            self.assertIn("reference_parse_low_confidence", payload["warnings"])
            export = self.run_cmd(["render_and_validate", "--db-path", str(db_path), "--mode", "render"])
            self.assertEqual(export.returncode, 2)

    def test_export_citation_workset_reads_db_only(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            source_path = td_path / "paper.md"
            db_path = td_path / ".literature_digest_tmp" / "literature_digest.db"
            source_path.write_text("# 1 Introduction\nPrior work [1].\n# 2 References\n[1] Smith. Paper A. 2020.\n", encoding="utf-8")

            self.assertEqual(
                self.run_cmd(
                    [
                        "bootstrap_runtime_db",
                        "--db-path",
                        str(db_path),
                        "--source-path",
                        str(source_path),
                        "--language",
                        "zh-CN",
                    ]
                ).returncode,
                0,
            )
            self.assertEqual(self.run_cmd(["normalize_source", "--db-path", str(db_path)]).returncode, 0)
            self.assertEqual(
                self.run_cmd(
                    ["persist_outline_and_scopes", "--db-path", str(db_path)],
                    input_obj={
                        "outline_nodes": [
                            {"node_id": "n1", "heading_level": 1, "title": "Introduction", "line_start": 1, "line_end": 2, "parent_node_id": None, "metadata": {}},
                            {"node_id": "n2", "heading_level": 1, "title": "References", "line_start": 3, "line_end": 4, "parent_node_id": None, "metadata": {}},
                        ],
                        "references_scope": {"section_title": "References", "line_start": 3, "line_end": 4, "metadata": {}},
                        "citation_scope": {"section_title": "Introduction", "line_start": 1, "line_end": 2, "metadata": {}},
                    },
                ).returncode,
                0,
            )
            self.assertEqual(
                self.run_cmd(
                    ["persist_references", "--db-path", str(db_path)],
                    input_obj={
                        "entries": [{"entry_index": 0, "raw": "[1] Smith. Paper A. 2020."}],
                        "batches": [{"batch_index": 0, "entry_start": 0, "entry_end": 0}],
                        "items": [{"ref_index": 0, "author": ["Smith"], "title": "Paper A", "year": 2020, "raw": "[1] Smith. Paper A. 2020.", "confidence": 0.9}],
                    },
                ).returncode,
                0,
            )
            self.assertEqual(self.run_cmd(["prepare_citation_workset", "--db-path", str(db_path)]).returncode, 0)

            workset = self.run_cmd(["export_citation_workset", "--db-path", str(db_path)])
            self.assertEqual(workset.returncode, 0, workset.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(workset.stdout.decode("utf-8"))
            self.assertEqual(payload["meta"]["scope"]["section_title"], "Introduction")
            self.assertEqual(payload["meta"]["total_mentions"], len(payload["mentions"]))
            self.assertIn("reference_index", payload)
            self.assertIn("workset_items", payload)
            self.assertIn("review_items", payload)

    def test_small_regression_corpus_can_reach_render(self):
        fixture_dir = REPO_ROOT / "tests" / "fixtures" / "literature_digest_small"
        fixtures = [
            ("numeric.md", "[1] Smith. Paper A. 2020.", ["Smith"], 2020),
            ("author_year.md", "Smith, J. Paper A. 2020.", ["Smith, J."], 2020),
            ("image_noise.md", "[1] Smith. Paper A. 2020.", ["Smith"], 2020),
            ("appendix_references.md", "[1] Smith. Paper A. 2020.", ["Smith"], 2020),
        ]
        for fixture_name, ref_raw, authors, year in fixtures:
            with self.subTest(fixture=fixture_name), tempfile.TemporaryDirectory() as td:
                td_path = Path(td)
                source_path = td_path / fixture_name
                source_path.write_text((fixture_dir / fixture_name).read_text(encoding="utf-8"), encoding="utf-8")
                db_path = td_path / ".literature_digest_tmp" / "literature_digest.db"
                self.assertEqual(self.run_cmd(["bootstrap_runtime_db", "--db-path", str(db_path), "--source-path", str(source_path), "--language", "zh-CN"]).returncode, 0)
                self.assertEqual(self.run_cmd(["normalize_source", "--db-path", str(db_path)]).returncode, 0)
                lines = source_path.read_text(encoding="utf-8").splitlines()
                citation_end = next(i for i, line in enumerate(lines, start=1) if line.startswith("# References")) - 1
                self.assertEqual(self.run_cmd(["persist_outline_and_scopes", "--db-path", str(db_path)], input_obj=self._outline_payload(lines, citation_line_end=citation_end)).returncode, 0)
                self.assertEqual(self.run_cmd(["persist_digest", "--db-path", str(db_path)], input_obj=self._digest_payload()).returncode, 0)
                self.assertEqual(self.run_cmd(["persist_references", "--db-path", str(db_path)], input_obj=self._reference_payload(ref_raw, year=year, author=authors)).returncode, 0)
                self.assertEqual(self.run_cmd(["prepare_citation_workset", "--db-path", str(db_path)]).returncode, 0)
                self.assertEqual(
                    self.run_cmd(
                        ["persist_citation_semantics", "--db-path", str(db_path)],
                        input_obj={"items": [{"ref_index": 0, "function": "background", "summary": "Used as background.", "confidence": 0.9}]},
                    ).returncode,
                    0,
                )
                self.assertEqual(
                    self.run_cmd(
                        ["persist_citation_summary", "--db-path", str(db_path)],
                        input_obj={"summary": "Prior work is used as background literature."},
                    ).returncode,
                    0,
                )
                render = self.run_cmd(["render_and_validate", "--db-path", str(db_path), "--mode", "render"])
                self.assertEqual(render.returncode, 0, render.stderr.decode("utf-8", errors="replace"))


if __name__ == "__main__":
    unittest.main()
