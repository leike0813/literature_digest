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
            instruction_paths = [item["path"] for item in payload["instruction_refs"]]
            self.assertEqual(instruction_paths[0], "references/step_02_outline_and_scopes.md")
            self.assertIn("references/failure_recovery.md", instruction_paths)
            self.assertIn("references/sql_playbook.md", instruction_paths)
            self.assertTrue(any("workflow_state" in item["sql"] for item in payload["sql_examples"]))


if __name__ == "__main__":
    unittest.main()
