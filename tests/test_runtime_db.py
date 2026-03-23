import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DB_PATH = REPO_ROOT / "literature-digest" / "scripts" / "runtime_db.py"


def load_runtime_db_module():
    spec = importlib.util.spec_from_file_location("literature_digest_runtime_db", RUNTIME_DB_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeDbTests(unittest.TestCase):
    def test_initialize_database_seeds_workflow_state(self):
        runtime_db = load_runtime_db_module()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / ".literature_digest_tmp" / "literature_digest.db"
            runtime_db.initialize_database(db_path)
            self.assertTrue(db_path.exists())
            with runtime_db.connect_db(db_path) as connection:
                state = runtime_db.fetch_workflow_state(connection)
                self.assertEqual(state["current_stage"], "stage_1_normalize_source")
                self.assertEqual(state["next_action"], "normalize_source")

    def test_store_and_fetch_final_payload_data(self):
        runtime_db = load_runtime_db_module()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / ".literature_digest_tmp" / "literature_digest.db"
            runtime_db.initialize_database(db_path)
            with runtime_db.connect_db(db_path) as connection:
                runtime_db.set_runtime_input(connection, "language", "zh-CN")
                runtime_db.store_digest_slots(
                    connection,
                    {
                        "tldr": {"paragraphs": ["digest body"]},
                        "research_question_and_contributions": {
                            "research_question": "question",
                            "contributions": ["c1", "c2"],
                        },
                        "method_highlights": {"items": ["m1"]},
                        "key_results": {"items": ["r1"]},
                        "limitations_and_reproducibility": {"items": ["l1"]},
                    },
                )
                runtime_db.store_digest_section_summaries(
                    connection,
                    [
                        {
                            "position": 1,
                            "source_heading": "Introduction",
                            "items": ["summary point"],
                        }
                    ],
                )
                runtime_db.store_section_scope(
                    connection,
                    scope_key="citation_scope",
                    section_title="Introduction",
                    line_start=1,
                    line_end=8,
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
                            "confidence": 0.8,
                        }
                    ],
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
                runtime_db.store_citation_unmapped_mentions(
                    connection,
                    [
                        {
                            "mention_id": "m00002",
                            "marker": "(Brown, 2019)",
                            "style": "author-year",
                            "line_start": 3,
                            "line_end": 3,
                            "snippet": "snippet",
                            "reason": "ambiguous",
                        }
                    ],
                )
                payload = runtime_db.fetch_citation_payload(connection, report_md="## Report\n")
                digest_context = runtime_db.build_digest_render_context(connection)
                references_context = runtime_db.build_references_render_context(connection)
                citation_context = runtime_db.build_citation_render_context(connection, "## Report\n")
                report_context = runtime_db.build_citation_report_render_context(connection)
                self.assertEqual(payload["meta"]["scope"]["section_title"], "Introduction")
                self.assertEqual(payload["summary"], "global citation summary")
                self.assertEqual(len(payload["items"]), 1)
                self.assertEqual(len(payload["unmapped_mentions"]), 1)
                self.assertEqual(payload["report_md"], "## Report\n")
                self.assertEqual(digest_context["language"], "zh-CN")
                self.assertEqual(digest_context["digest_slots"]["tldr"]["paragraphs"], ["digest body"])
                self.assertEqual(digest_context["section_summaries"][0]["source_heading"], "Introduction")
                self.assertEqual(references_context["items"][0]["title"], "Paper A")
                self.assertEqual(citation_context["citation_analysis"]["report_md"], "## Report\n")
                self.assertEqual(citation_context["citation_analysis"]["summary"], "global citation summary")
                self.assertEqual(report_context["scope"]["section_title"], "Introduction")
                self.assertEqual(report_context["summary"], "global citation summary")
                self.assertEqual(report_context["grouped_items"][0]["function_label"], "Background")


if __name__ == "__main__":
    unittest.main()
