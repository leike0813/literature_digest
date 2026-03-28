import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_RUNTIME = REPO_ROOT / "literature-digest" / "scripts" / "gate_runtime.py"
RUNTIME_DB_PATH = REPO_ROOT / "literature-digest" / "scripts" / "runtime_db.py"


def load_runtime_db_module():
    spec = importlib.util.spec_from_file_location("literature_digest_runtime_db", RUNTIME_DB_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GateRuntimeTests(unittest.TestCase):
    def run_gate(self, db_path: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(GATE_RUNTIME), "--db-path", str(db_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_missing_db_requests_bootstrap(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / ".literature_digest_tmp" / "literature_digest.db"
            result = self.run_gate(db_path)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(payload["next_action"], "bootstrap_runtime_db")
            self.assertEqual(payload["current_stage"], "stage_0_bootstrap")
            self.assertTrue(payload["instruction_refs"])
            self.assertTrue(payload["execution_note"])
            self.assertTrue(payload["sql_examples"])
            self.assertEqual(payload["instruction_refs"][0]["path"], "references/step_01_bootstrap_and_source.md")
            self.assertEqual(payload["instruction_refs"][1]["path"], "references/stage_runtime_interface.md")
            self.assertIn("runtime_inputs", payload["sql_examples"][1]["sql"])

    def test_initialized_db_allows_stage_1_entry(self):
        runtime_db = load_runtime_db_module()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / ".literature_digest_tmp" / "literature_digest.db"
            runtime_db.initialize_database(db_path)
            with runtime_db.connect_db(db_path) as connection:
                runtime_db.set_runtime_input(connection, "source_path", str(Path(td) / "paper.md"))
                connection.commit()

            result = self.run_gate(db_path)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(payload["stage_gate"], "ready")
            self.assertEqual(payload["next_action"], "normalize_source")
            self.assertIn("source_path", payload["execution_note"])
            self.assertEqual(payload["instruction_refs"][0]["path"], "references/step_01_bootstrap_and_source.md")
            self.assertEqual(payload["instruction_refs"][1]["path"], "references/stage_runtime_interface.md")
            self.assertIn("source_documents", payload["sql_examples"][1]["sql"])

    def test_missing_stage_prerequisite_blocks(self):
        runtime_db = load_runtime_db_module()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / ".literature_digest_tmp" / "literature_digest.db"
            runtime_db.initialize_database(db_path)
            with runtime_db.connect_db(db_path) as connection:
                runtime_db.set_workflow_state(
                    connection,
                    current_stage="stage_2_outline_and_scopes",
                    current_substep="persist_outline_and_scopes",
                    stage_gate="ready",
                    next_action="persist_outline_and_scopes",
                    status_summary="try stage 2",
                )
                connection.commit()

            result = self.run_gate(db_path)
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(payload["stage_gate"], "blocked")
            self.assertEqual(payload["next_action"], "repair_db_state")
            self.assertTrue(payload["execution_note"])
            instruction_paths = [item["path"] for item in payload["instruction_refs"]]
            self.assertEqual(instruction_paths[0], "references/step_02_outline_and_scopes.md")
            self.assertIn("references/failure_recovery.md", instruction_paths)
            self.assertIn("references/sql_playbook.md", instruction_paths)
            self.assertTrue(any("workflow_state" in item["sql"] for item in payload["sql_examples"]))

    def test_stage_6_gate_note_requests_direct_render_stdout_reuse(self):
        runtime_db = load_runtime_db_module()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / ".literature_digest_tmp" / "literature_digest.db"
            runtime_db.initialize_database(db_path)
            with runtime_db.connect_db(db_path) as connection:
                runtime_db.set_workflow_state(
                    connection,
                    current_stage="stage_6_render_and_validate",
                    current_substep="render_and_validate",
                    stage_gate="ready",
                    next_action="render_and_validate",
                    status_summary="ready to render",
                )
                runtime_db.store_digest_slots(
                    connection,
                    {
                        "tldr": {"paragraphs": ["x"]},
                        "research_question_and_contributions": {"research_question": "q", "contributions": ["c"]},
                        "method_highlights": {"items": ["m"]},
                        "key_results": {"items": ["r"]},
                        "limitations_and_reproducibility": {"items": ["l"]},
                    },
                )
                runtime_db.store_digest_section_summaries(connection, [{"source_heading": "Intro", "items": ["x"]}])
                runtime_db.store_reference_items(
                    connection,
                    [{"ref_index": 0, "author": ["Smith"], "title": "Paper", "year": 2020, "raw": "raw", "confidence": 0.9, "metadata": {}}],
                )
                runtime_db.store_section_scope(
                    connection,
                    scope_key="citation_scope",
                    section_title="Introduction",
                    line_start=1,
                    line_end=3,
                    metadata={},
                )
                runtime_db.store_citation_workset_items(
                    connection,
                    [{"ref_index": 0, "ref_number": 1, "mention_count": 1, "mentions": [], "reference_snapshot": {}, "batch_hint": 0, "workset_metadata": {}}],
                )
                runtime_db.store_citation_items(
                    connection,
                    [{"ref_index": 0, "function": "background", "summary": "s", "confidence": 0.9, "metadata": {}}],
                )
                runtime_db.store_citation_timeline(
                    connection,
                    {"early": {"summary": "e", "ref_indexes": [0]}, "mid": {"summary": "m", "ref_indexes": []}, "recent": {"summary": "r", "ref_indexes": []}},
                )
                runtime_db.store_citation_summary(
                    connection,
                    summary_text="summary",
                    basis={"research_threads": ["a", "b"], "argument_shape": ["x", "y"], "key_ref_indexes": [0]},
                )
                runtime_db.store_citation_unmapped_mentions(
                    connection,
                    [
                        {
                            "mention_id": "u1",
                            "marker": "[x]",
                            "style": "numeric",
                            "line_start": 1,
                            "line_end": 1,
                            "snippet": "snippet",
                            "reason": "unmapped",
                            "batch_index": 0,
                        }
                    ],
                )
                connection.commit()

            result = self.run_gate(db_path)
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(payload["next_action"], "render_and_validate")
            self.assertIn("render_and_validate --mode render", payload["execution_note"])
            self.assertIn("stdout JSON", payload["execution_note"])


if __name__ == "__main__":
    unittest.main()
