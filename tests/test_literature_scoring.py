import json
import os
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_SCRIPTS = REPO_ROOT / "literature-analysis" / "scripts"
RUN_ANALYSIS = ANALYSIS_SCRIPTS / "run_analysis.py"
if str(ANALYSIS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_SCRIPTS))

from analysis_runtime import deterministic_core, runtime, runtime_db, scoring, stages  # noqa: E402

sys.dont_write_bytecode = True


class LiteratureScoringTests(unittest.TestCase):
    def rubric(self) -> dict:
        return json.loads(
            (REPO_ROOT / "literature-analysis" / "assets" / "scoring_rubric.json").read_text(encoding="utf-8")
        )

    def payload(self, *, whole_na_dimension: str | None = None, partial_na: tuple[str, str] | None = None) -> dict:
        reviews = []
        for dimension in self.rubric()["dimensions"]:
            whole_na = dimension["dimension_key"] == whole_na_dimension
            criteria = []
            for criterion in dimension["criteria"]:
                is_na = whole_na or partial_na == (dimension["dimension_key"], criterion["criterion_key"])
                criteria.append(
                    {
                        "criterion_key": criterion["criterion_key"],
                        "status": "not_applicable" if is_na else "scored",
                        "score": None if is_na else criterion["max_score"],
                        "reason": "No evaluation object for this paper type." if is_na else "Assessed from the normalized source.",
                        "evidence": [],
                    }
                )
            reviews.append(
                {
                    "dimension_key": dimension["dimension_key"],
                    "confidence": None if whole_na else 0.8,
                    "summary": "Dimension-level assessment.",
                    "criteria": criteria,
                }
            )
        return {
            "paper_type": "empirical",
            "paper_type_reason": "The paper is organized around empirical evaluation.",
            "dimension_reviews": reviews,
        }

    def initialize(self, root: Path, *, score_only: bool) -> Path:
        source_path = root / "paper.md"
        source_path.write_text(
            "# Introduction\nWe evaluate a method against three baselines.\n# Results\nThe method improves accuracy.\n",
            encoding="utf-8",
        )
        db_path = runtime.default_db_path(root)
        paths = runtime.initialize_runtime(
            working_dir=root,
            db_path=db_path,
            output_dir=root,
            source_path=source_path,
            language="en-US",
            model="test-model",
            score_only=score_only,
        )
        runtime.persist_default_templates(db_path=db_path, runtime_paths=paths, language="en-US")
        _, code = stages.normalize_source(
            source_path=source_path,
            db_path=db_path,
            runtime_paths=paths,
            language="en-US",
            model="test-model",
        )
        self.assertEqual(code, 0)
        return db_path

    def test_score_only_renders_one_score_artifact_and_redistributes_whole_na_weight(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = self.initialize(root, score_only=True)

            prepared, prepare_code = scoring.prepare_scoring_context(db_path)
            self.assertEqual(prepare_code, 0)
            self.assertTrue(Path(prepared["scoring_context_path"]).exists())

            final, code = scoring.persist_literature_score(
                db_path,
                self.payload(whole_na_dimension="innovation_signals"),
            )
            self.assertEqual(code, 0)
            self.assertEqual(final["digest_path"], "")
            self.assertEqual(final["references_path"], "")
            self.assertEqual(final["citation_analysis_path"], "")
            self.assertEqual(final["literature_matching_metadata_path"], "")
            score_path = Path(final["literature_score_path"])
            self.assertTrue(score_path.is_absolute())
            self.assertTrue(score_path.exists())

            score = json.loads(score_path.read_text(encoding="utf-8"))
            self.assertEqual(score["overall_score"], 100.0)
            self.assertEqual(score["confidence"], 0.8)
            self.assertEqual(score["confidence_adjusted_score"], 80.0)
            innovation = next(item for item in score["dimensions"] if item["dimension_key"] == "innovation_signals")
            self.assertIsNone(innovation["score"])
            self.assertIsNone(innovation["confidence"])
            self.assertEqual(innovation["effective_weight"], 0.0)
            self.assertAlmostEqual(sum(item["effective_weight"] for item in score["dimensions"]), 1.0, places=5)
            self.assertTrue(any("innovation_signals" in warning for warning in final["warnings"]))

            mirror = json.loads((root / "literature-analysis.result.json").read_text(encoding="utf-8"))
            self.assertEqual(mirror, final)

    def test_score_only_cli_skips_non_scoring_actions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "paper.md"
            source.write_text("# Paper\nA short source.\n", encoding="utf-8")
            initialized = subprocess.run(
                [
                    sys.executable,
                    str(RUN_ANALYSIS),
                    "init_runtime",
                    "--source-path",
                    str(source),
                    "--working-dir",
                    str(root),
                    "--score-only",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr.decode("utf-8", errors="replace"))
            init_payload = json.loads(initialized.stdout.decode("utf-8"))
            self.assertEqual(init_payload["next_action"], "persist_literature_score")
            self.assertTrue(init_payload["source_profile"]["score_only"])

            plan_path = root / "plan.json"
            plan_path.write_text("{}\n", encoding="utf-8")
            rejected = subprocess.run(
                [
                    sys.executable,
                    str(RUN_ANALYSIS),
                    "persist_analysis_plan",
                    "--db-path",
                    init_payload["db_path"],
                    "--payload-file",
                    str(plan_path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            self.assertEqual(rejected.returncode, 2)
            error_payload = json.loads(rejected.stdout.decode("utf-8"))
            self.assertEqual(error_payload["error"]["code"], "score_only_action_forbidden")
            self.assertEqual(error_payload["next_action"], "persist_literature_score")

    def test_partial_na_renormalizes_inside_dimension_without_removing_dimension_weight(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = self.initialize(root, score_only=True)
            payload = self.payload(partial_na=("methodological_rigor", "baseline_or_control_adequacy"))
            final, code = scoring.persist_literature_score(db_path, payload)
            self.assertEqual(code, 0)
            score = json.loads(Path(final["literature_score_path"]).read_text(encoding="utf-8"))
            methodology = next(item for item in score["dimensions"] if item["dimension_key"] == "methodological_rigor")
            self.assertEqual(methodology["applicable_max_score"], 20)
            self.assertEqual(methodology["score"], 100.0)
            self.assertEqual(methodology["effective_weight"], 0.25)
            baseline = next(item for item in methodology["criteria"] if item["criterion_key"] == "baseline_or_control_adequacy")
            self.assertIsNone(baseline["score"])

    def test_runtime_rejects_aggregate_fields_and_unresolvable_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = self.initialize(root, score_only=True)
            aggregate_payload = self.payload()
            aggregate_payload["overall_score"] = 99
            result, code = scoring.persist_literature_score(db_path, aggregate_payload)
            self.assertEqual(code, 2)
            self.assertEqual(result["error"]["code"], "score_payload_invalid")
            self.assertTrue(any("runtime-owned" in item["message"] for item in result["error"]["details"]))

            evidence_payload = deepcopy(self.payload())
            evidence_payload["dimension_reviews"][0]["criteria"][0]["evidence"] = [
                {"line_start": 2, "line_end": 2, "quote": "This sentence is not in the source."}
            ]
            result, code = scoring.persist_literature_score(db_path, evidence_payload)
            self.assertEqual(code, 2)
            details = result["error"]["details"]
            self.assertTrue(any("quote does not occur" in item["message"] for item in details))

    def test_full_mode_requires_digest_and_advances_to_references_after_scoring(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = self.initialize(root, score_only=False)
            _, code = scoring.prepare_scoring_context(db_path)
            self.assertEqual(code, 2)

            with runtime_db.connect_db(db_path) as connection:
                runtime_db.store_action_receipt(connection, action_name="persist_digest", stage="stage_3_digest")
                repaired = deterministic_core._repair_state_from_receipts(connection)
                connection.commit()
            self.assertEqual(repaired[0], "stage_4_scoring")
            self.assertEqual(repaired[2], "persist_literature_score")

            result, code = scoring.persist_literature_score(db_path, self.payload())
            self.assertEqual(code, 0)
            self.assertEqual(result["next_action"], "prepare_references_workset")
            with runtime_db.connect_db(db_path) as connection:
                state = runtime_db.fetch_workflow_state(connection)
                self.assertIsNotNone(runtime_db.fetch_literature_score(connection))
                repaired = deterministic_core._repair_state_from_receipts(connection)
            assert state is not None
            self.assertEqual(state["current_stage"], "stage_5_references")
            self.assertEqual(state["next_action"], "prepare_references_workset")
            self.assertEqual(repaired[0], "stage_5_references")
            self.assertEqual(repaired[2], "prepare_references_workset")


if __name__ == "__main__":
    unittest.main()
