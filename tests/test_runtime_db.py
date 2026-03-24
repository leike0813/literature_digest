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
                            "topic": "technical background",
                            "usage": "Used to establish the technical background of the method.",
                            "keywords": ["transformer", "background"],
                            "is_key_reference": True,
                            "confidence": 0.9,
                        }
                    ],
                )
                runtime_db.store_citation_timeline(
                    connection,
                    {
                        "early": {"summary": "early summary", "ref_indexes": [0]},
                        "mid": {"summary": "mid summary", "ref_indexes": []},
                        "recent": {"summary": "recent summary", "ref_indexes": []},
                    },
                )
                runtime_db.store_citation_summary(
                    connection,
                    "global citation summary",
                    {
                        "research_threads": [
                            "technical background leading into the method",
                            "comparison against neighboring routes",
                        ],
                        "argument_shape": [
                            "lay out the background",
                            "contrast neighboring routes",
                        ],
                        "key_ref_indexes": [0],
                    },
                )
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
                self.assertIn("timeline", payload)
                self.assertEqual(len(payload["items"]), 1)
                self.assertEqual(len(payload["unmapped_mentions"]), 1)
                self.assertEqual(payload["report_md"], "## Report\n")
                self.assertEqual(digest_context["language"], "zh-CN")
                self.assertEqual(digest_context["digest_slots"]["tldr"]["paragraphs"], ["digest body"])
                self.assertEqual(digest_context["section_summaries"][0]["source_heading"], "Introduction")
                self.assertEqual(references_context["items"][0]["title"], "Paper A")
                self.assertEqual(citation_context["citation_analysis"]["report_md"], "## Report\n")
                self.assertEqual(citation_context["citation_analysis"]["summary"], "global citation summary")
                self.assertEqual(citation_context["citation_analysis"]["items"][0]["topic"], "technical background")
                self.assertEqual(
                    citation_context["citation_analysis"]["items"][0]["usage"],
                    "Used to establish the technical background of the method.",
                )
                self.assertEqual(citation_context["citation_analysis"]["items"][0]["keywords"], ["transformer", "background"])
                self.assertTrue(citation_context["citation_analysis"]["items"][0]["is_key_reference"])
                self.assertEqual(citation_context["citation_analysis"]["items"][0]["citation_label"], "[1]")
                self.assertEqual(citation_context["citation_analysis"]["items"][0]["author_year_label"], "Smith, 2020")
                self.assertEqual(report_context["scope"]["section_title"], "Introduction")
                self.assertEqual(report_context["summary"], "global citation summary")
                self.assertEqual(report_context["grouped_items"][0]["function_label"], "Background")
                self.assertEqual(report_context["summary_basis"]["key_ref_indexes"], [0])
                self.assertEqual(report_context["key_references"][0]["citation_label"], "[1]")
                self.assertEqual(report_context["key_references"][0]["author_year_label"], "Smith, 2020")
                self.assertEqual(report_context["key_references"][0]["title"], "Paper A")
                self.assertEqual(report_context["timeline"]["early"]["ref_indexes"], [0])
                self.assertEqual(report_context["grouped_items"][0]["items"][0]["keywords"], ["transformer", "background"])

    def test_store_and_fetch_reference_parse_candidates(self):
        runtime_db = load_runtime_db_module()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / ".literature_digest_tmp" / "literature_digest.db"
            runtime_db.initialize_database(db_path)
            with runtime_db.connect_db(db_path) as connection:
                runtime_db.store_reference_parse_candidates(
                    connection,
                    [
                        {
                            "entry_index": 0,
                            "candidate_index": 0,
                            "pattern": "authors_colon_title_in_year",
                            "author_text": "Gu, J., Bradbury, J.",
                            "author_candidates": ["Gu, J.", "Bradbury, J."],
                            "title_candidate": "Non-autoregressive neural machine translation",
                            "container_candidate": "ICLR",
                            "year_candidate": 2018,
                            "confidence": 0.9,
                            "metadata": {"split_basis": "authors before colon"},
                        }
                    ],
                )
                fetched = runtime_db.fetch_reference_parse_candidates(connection)
                self.assertEqual(len(fetched), 1)
                self.assertEqual(fetched[0]["pattern"], "authors_colon_title_in_year")
                self.assertEqual(fetched[0]["author_candidates"], ["Gu, J.", "Bradbury, J."])
                self.assertEqual(fetched[0]["metadata"]["split_basis"], "authors before colon")

    def test_author_year_items_receive_stable_synthetic_labels(self):
        runtime_db = load_runtime_db_module()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / ".literature_digest_tmp" / "literature_digest.db"
            runtime_db.initialize_database(db_path)
            with runtime_db.connect_db(db_path) as connection:
                runtime_db.set_runtime_input(connection, "language", "en-US")
                runtime_db.store_section_scope(
                    connection,
                    scope_key="citation_scope",
                    section_title="Related Work",
                    line_start=1,
                    line_end=12,
                )
                runtime_db.store_citation_workset_items(
                    connection,
                    [
                        {
                            "ref_index": 1,
                            "ref_number": None,
                            "mention_count": 1,
                            "mentions": [{"mention_id": "m2", "marker": "(Brown, 2018)", "style": "author-year", "line_start": 5, "line_end": 5, "snippet": "snippet"}],
                            "reference": {"author": ["Brown"], "title": "Paper B", "year": 2018},
                            "batch_hint": 0,
                        },
                        {
                            "ref_index": 0,
                            "ref_number": None,
                            "mention_count": 1,
                            "mentions": [{"mention_id": "m1", "marker": "(Adams, 2016)", "style": "author-year", "line_start": 2, "line_end": 2, "snippet": "snippet"}],
                            "reference": {"author": ["Adams"], "title": "Paper A", "year": 2016},
                            "batch_hint": 0,
                        },
                    ],
                )
                runtime_db.store_citation_items(
                    connection,
                    [
                        {"ref_index": 0, "function": "historical", "summary": "summary a", "topic": "topic a", "usage": "usage a", "keywords": ["history"], "is_key_reference": False, "confidence": 0.9},
                        {"ref_index": 1, "function": "background", "summary": "summary b", "topic": "topic b", "usage": "usage b", "keywords": ["background"], "is_key_reference": False, "confidence": 0.9},
                    ],
                )
                runtime_db.store_citation_timeline(
                    connection,
                    {
                        "early": {"summary": "early summary", "ref_indexes": [0]},
                        "mid": {"summary": "mid summary", "ref_indexes": [1]},
                        "recent": {"summary": "recent summary", "ref_indexes": []},
                    },
                )
                runtime_db.store_citation_summary(
                    connection,
                    "summary",
                    {"research_threads": ["thread a", "thread b"], "argument_shape": ["shape a", "shape b"], "key_ref_indexes": [0]},
                )
                payload = runtime_db.fetch_citation_payload(connection)
                labels = {item["ref_index"]: item["citation_label"] for item in payload["items"]}
                self.assertEqual(labels[0], "[AY-1]")
                self.assertEqual(labels[1], "[AY-2]")


if __name__ == "__main__":
    unittest.main()
