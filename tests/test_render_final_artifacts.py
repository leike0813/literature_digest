import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DB_PATH = REPO_ROOT / "literature-digest" / "scripts" / "runtime_db.py"
STAGE_RUNTIME = REPO_ROOT / "literature-digest" / "scripts" / "stage_runtime.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RenderFinalArtifactsTests(unittest.TestCase):
    def test_render_outputs_include_optional_report_path(self):
        runtime_db = load_module(RUNTIME_DB_PATH, "literature_digest_runtime_db")

        with tempfile.TemporaryDirectory() as td:
            source_path = Path(td) / "paper.md"
            source_path.write_text("# Title\n", encoding="utf-8")
            db_path = Path(td) / ".literature_digest_tmp" / "literature_digest.db"
            runtime_db.initialize_database(db_path)

            with runtime_db.connect_db(db_path) as connection:
                runtime_db.set_runtime_input(connection, "source_path", str(source_path))
                runtime_db.set_runtime_input(connection, "generated_at", "2026-03-23T00:00:00Z")
                runtime_db.set_runtime_input(connection, "input_hash", "sha256:abc")
                runtime_db.set_runtime_input(connection, "model", "x")
                runtime_db.set_runtime_input(connection, "language", "zh-CN")
                runtime_db.store_digest_slots(
                    connection,
                    {
                        "tldr": {"paragraphs": ["digest body"]},
                        "research_question_and_contributions": {
                            "research_question": "question",
                            "contributions": ["c1"],
                        },
                        "method_highlights": {"items": ["m1"]},
                        "key_results": {"items": ["r1"]},
                        "limitations_and_reproducibility": {"items": ["l1"]},
                    },
                )
                runtime_db.store_digest_section_summaries(
                    connection,
                    [{"position": 1, "source_heading": "Title", "items": ["section summary"]}],
                )
                runtime_db.store_reference_items(
                    connection,
                    [
                        {
                            "ref_index": 0,
                            "author": ["Smith"],
                            "title": "Paper A",
                            "year": 2020,
                            "raw": "[1] Smith",
                            "confidence": 0.9,
                        }
                    ],
                )
                runtime_db.store_section_scope(
                    connection,
                    scope_key="citation_scope",
                    section_title="Introduction",
                    line_start=1,
                    line_end=4,
                )
                runtime_db.store_citation_workset_items(
                    connection,
                    [
                        {
                            "ref_index": 0,
                            "ref_number": 1,
                            "mention_count": 1,
                            "mentions": [
                                {
                                    "mention_id": "m00001",
                                    "marker": "[1]",
                                    "style": "numeric",
                                    "line_start": 2,
                                    "line_end": 2,
                                    "snippet": "snippet",
                                }
                            ],
                            "reference": {"author": ["Smith"], "title": "Paper A", "year": 2020},
                            "batch_hint": 0,
                        }
                    ],
                )
                runtime_db.store_citation_items(
                    connection,
                    [
                        {
                            "ref_index": 0,
                            "function": "background",
                            "summary": "summary",
                            "confidence": 0.9,
                        }
                    ],
                )
                runtime_db.store_citation_summary(connection, "global citation summary")
                connection.commit()

            result = subprocess.run(
                [
                    sys.executable,
                    str(STAGE_RUNTIME),
                    "render_and_validate",
                    "--db-path",
                    str(db_path),
                    "--mode",
                    "render",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertIn("citation_analysis_report_path", payload)
            report_path = Path(str(payload["citation_analysis_report_path"]))
            digest_path = Path(str(payload["digest_path"]))
            citation_json = json.loads(Path(str(payload["citation_analysis_path"])).read_text(encoding="utf-8"))
            self.assertTrue(report_path.exists())
            self.assertTrue(digest_path.exists())
            digest_text = digest_path.read_text(encoding="utf-8")
            self.assertIn("## TL;DR", digest_text)
            self.assertIn("digest body", digest_text)
            self.assertIn("## 研究问题与贡献", digest_text)
            self.assertEqual(citation_json["summary"], "global citation summary")
            self.assertEqual(report_path.read_text(encoding="utf-8"), citation_json["report_md"])
            self.assertIn("summary", citation_json["report_md"])


if __name__ == "__main__":
    unittest.main()
