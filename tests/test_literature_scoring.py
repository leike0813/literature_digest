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

    def review(
        self,
        db_path: Path,
        *,
        whole_na_dimension: str | None = None,
        partial_na: tuple[str, str] | None = None,
    ) -> tuple[dict, dict]:
        prepared, code = scoring.prepare_scoring_context(db_path)
        self.assertEqual(code, 0)
        payload = json.loads(Path(prepared["scoring_review_draft_path"]).read_text(encoding="utf-8"))
        payload["paper_type_choices"][0]["selected"] = True
        payload["paper_type_reason"] = "The paper is organized around empirical evaluation."
        for dimension in payload["dimension_reviews"]:
            whole_na = dimension["dimension_key"] == whole_na_dimension
            dimension["confidence"] = None if whole_na else 0.8
            dimension["summary"] = "Dimension-level assessment."
        for criterion in payload["criterion_reviews"]:
            is_na = whole_na_dimension == criterion["dimension_key"] or partial_na == (
                criterion["dimension_key"],
                criterion["criterion_key"],
            )
            criterion["applicable"] = not is_na
            criterion["score"] = None if is_na else criterion["max_score"]
            criterion["reason"] = (
                "No evaluation object for this paper type."
                if is_na
                else "Assessed from the normalized source."
            )
        return payload, prepared

    def test_prepare_generates_rubric_driven_form_and_preserves_existing_draft(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = self.initialize(root, score_only=True)
            prepared, code = scoring.prepare_scoring_context(db_path)
            self.assertEqual(code, 0)
            self.assertNotIn("allowed_payload_shape", prepared)
            self.assertNotIn("scoring_context_path", prepared)
            form_path = Path(prepared["scoring_review_form_path"])
            draft_path = Path(prepared["scoring_review_draft_path"])
            self.assertNotEqual(form_path, draft_path)
            self.assertTrue(form_path.exists())
            self.assertTrue(draft_path.exists())
            form = json.loads(form_path.read_text(encoding="utf-8"))
            rubric = self.rubric()
            self.assertTrue(form["form_id"].startswith("sha256:"))
            self.assertEqual(
                [{key: item[key] for key in ("paper_type", "description")} for item in form["paper_type_choices"]],
                rubric["paper_type_choices"],
            )
            self.assertEqual(
                [item["dimension_key"] for item in form["dimension_reviews"]],
                [item["dimension_key"] for item in rubric["dimensions"]],
            )
            rubric_criteria = [criterion for dimension in rubric["dimensions"] for criterion in dimension["criteria"]]
            self.assertEqual(
                [item["criterion_key"] for item in form["criterion_reviews"]],
                [item["criterion_key"] for item in rubric_criteria],
            )
            self.assertEqual(
                [item["prompt"] for item in form["criterion_reviews"]],
                [item["prompt"] for item in rubric_criteria],
            )

            draft = deepcopy(form)
            draft["paper_type_reason"] = "Partially completed answer that must survive prepare."
            draft_path.write_text(json.dumps(draft, ensure_ascii=False), encoding="utf-8")
            prepared_again, second_code = scoring.prepare_scoring_context(db_path)
            self.assertEqual(second_code, 0)
            self.assertEqual(prepared_again["scoring_review_draft_path"], str(draft_path))
            self.assertEqual(json.loads(draft_path.read_text(encoding="utf-8")), draft)

    def test_score_only_renders_one_score_artifact_and_redistributes_whole_na_weight(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = self.initialize(root, score_only=True)
            review, _ = self.review(db_path, whole_na_dimension="innovation_signals")
            final, code = scoring.persist_literature_score(db_path, review)
            self.assertEqual(code, 0)
            self.assertEqual(final["digest_path"], "")
            self.assertEqual(final["references_path"], "")
            self.assertEqual(final["citation_analysis_path"], "")
            self.assertEqual(final["literature_matching_metadata_path"], "")
            score_path = Path(final["literature_score_path"])
            self.assertTrue(score_path.is_absolute())
            self.assertTrue(score_path.exists())

            score = json.loads(score_path.read_text(encoding="utf-8"))
            self.assertEqual(score["schema"], "literature_score.v1")
            self.assertEqual(score["overall_score"], 100.0)
            self.assertEqual(score["confidence"], 0.8)
            self.assertEqual(score["confidence_adjusted_score"], 80.0)
            innovation = next(item for item in score["dimensions"] if item["dimension_key"] == "innovation_signals")
            self.assertIsNone(innovation["score"])
            self.assertIsNone(innovation["confidence"])
            self.assertEqual(innovation["effective_weight"], 0.0)
            self.assertAlmostEqual(sum(item["effective_weight"] for item in score["dimensions"]), 1.0, places=5)
            self.assertTrue(any("innovation_signals" in warning for warning in final["warnings"]))
            self.assertEqual(json.loads((root / "literature-analysis.result.json").read_text(encoding="utf-8")), final)

    def test_partial_na_renormalizes_inside_dimension_without_removing_dimension_weight(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = self.initialize(root, score_only=True)
            review, _ = self.review(
                db_path,
                partial_na=("methodological_rigor", "baseline_or_control_adequacy"),
            )
            final, code = scoring.persist_literature_score(db_path, review)
            self.assertEqual(code, 0)
            score = json.loads(Path(final["literature_score_path"]).read_text(encoding="utf-8"))
            methodology = next(item for item in score["dimensions"] if item["dimension_key"] == "methodological_rigor")
            self.assertEqual(methodology["applicable_max_score"], 20)
            self.assertEqual(methodology["score"], 100.0)
            self.assertEqual(methodology["effective_weight"], 0.25)
            baseline = next(item for item in methodology["criteria"] if item["criterion_key"] == "baseline_or_control_adequacy")
            self.assertIsNone(baseline["score"])

    def test_review_validation_reports_selection_locked_and_incomplete_reason_codes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = self.initialize(root, score_only=True)
            valid, _ = self.review(db_path)
            cases = []

            no_selection = deepcopy(valid)
            no_selection["paper_type_choices"][0]["selected"] = False
            cases.append(("zero selection", no_selection, "invalid_selection"))

            two_selections = deepcopy(valid)
            two_selections["paper_type_choices"][1]["selected"] = True
            cases.append(("two selections", two_selections, "invalid_selection"))

            changed_locked_field = deepcopy(valid)
            changed_locked_field["criterion_reviews"][0]["max_score"] += 1
            cases.append(("locked maximum", changed_locked_field, "locked_field_changed"))

            missing_score = deepcopy(valid)
            missing_score["criterion_reviews"][0]["score"] = None
            cases.append(("missing applicable score", missing_score, "incomplete_answer"))

            scored_na = deepcopy(valid)
            scored_na["criterion_reviews"][0]["applicable"] = False
            cases.append(("score supplied for n/a", scored_na, "incomplete_answer"))

            incomplete_dimension = deepcopy(valid)
            incomplete_dimension["dimension_reviews"][0]["summary"] = ""
            cases.append(("missing summary", incomplete_dimension, "incomplete_answer"))

            missing_criterion = deepcopy(valid)
            missing_criterion["criterion_reviews"].pop()
            cases.append(("missing criterion", missing_criterion, "incomplete_answer"))

            for label, payload, expected_reason in cases:
                with self.subTest(label=label):
                    result, code = scoring.persist_literature_score(db_path, payload)
                    self.assertEqual(code, 2)
                    self.assertEqual(result["error"]["code"], "score_review_invalid")
                    self.assertIn(expected_reason, {item["reason"] for item in result["error"]["details"]})

            manual_payload = {
                "paper_type": "empirical",
                "paper_type_reason": "Manually constructed payload.",
                "dimension_reviews": [],
            }
            result, code = scoring.persist_literature_score(db_path, manual_payload)
            self.assertEqual(code, 2)
            self.assertEqual(result["error"]["details"][0]["reason"], "stale_form")

    def test_source_or_rubric_change_invalidates_prepared_review(self):
        for change_kind in ("source", "rubric"):
            with self.subTest(change_kind=change_kind), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                db_path = self.initialize(root, score_only=True)
                review, old_prepared = self.review(db_path)
                with runtime_db.connect_db(db_path) as connection:
                    if change_kind == "source":
                        source_doc = runtime_db.fetch_source_document(connection, "normalized_source")
                        assert source_doc is not None
                        runtime_db.store_source_document(
                            connection,
                            doc_key="normalized_source",
                            content=str(source_doc["content"]) + "A newly normalized line.\n",
                            metadata=dict(source_doc["metadata"]),
                        )
                    else:
                        inputs = runtime_db.fetch_runtime_inputs(connection)
                        rubric_path = Path(inputs["scoring_rubric_path"])
                        rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
                        rubric["dimensions"][0]["prompt"] += " Updated."
                        rubric_path.write_text(json.dumps(rubric, ensure_ascii=False), encoding="utf-8")
                    connection.commit()
                new_prepared, prepare_code = scoring.prepare_scoring_context(db_path)
                self.assertEqual(prepare_code, 0)
                self.assertNotEqual(
                    new_prepared["scoring_review_form_path"],
                    old_prepared["scoring_review_form_path"],
                )
                self.assertNotEqual(
                    new_prepared["scoring_review_draft_path"],
                    old_prepared["scoring_review_draft_path"],
                )
                result, code = scoring.persist_literature_score(db_path, review)
                self.assertEqual(code, 2)
                self.assertEqual(result["error"]["code"], "score_review_invalid")
                self.assertEqual(result["error"]["details"][0]["reason"], "stale_form")

    def test_evidence_location_accepts_normalized_and_fuzzy_matches_and_rejects_low_similarity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_path = self.initialize(root, score_only=True)
            review, _ = self.review(db_path)
            review["criterion_reviews"][0]["evidence_quotes"] = [
                "WE EVALUATE A METHOD—AGAINST THREE BASELINES!",
                "introducton",
            ]
            result, code = scoring.persist_literature_score(db_path, review)
            self.assertEqual(code, 0)
            score = json.loads(Path(result["literature_score_path"]).read_text(encoding="utf-8"))
            evidence = score["dimensions"][0]["criteria"][0]["evidence"][0]
            self.assertEqual((evidence["line_start"], evidence["line_end"]), (2, 2))
            short_fuzzy_evidence = score["dimensions"][0]["criteria"][0]["evidence"][1]
            self.assertEqual((short_fuzzy_evidence["line_start"], short_fuzzy_evidence["line_end"]), (1, 1))

            fuzzy = deepcopy(review)
            fuzzy["criterion_reviews"][0]["evidence_quotes"] = [
                "We evaluate a method against several baseline systems."
            ]
            result, code = scoring.persist_literature_score(db_path, fuzzy)
            self.assertEqual(code, 0)
            score = json.loads(Path(result["literature_score_path"]).read_text(encoding="utf-8"))
            evidence = score["dimensions"][0]["criteria"][0]["evidence"][0]
            self.assertEqual((evidence["line_start"], evidence["line_end"]), (2, 2))

            rejected = deepcopy(review)
            rejected["criterion_reviews"][0]["evidence_quotes"] = [
                "Unrelated discussion of marine biology taxonomy."
            ]
            result, code = scoring.persist_literature_score(db_path, rejected)
            self.assertEqual(code, 2)
            detail = next(item for item in result["error"]["details"] if item["reason"] == "evidence_not_found")
            self.assertEqual(detail["criterion_key"], "research_question_clarity")
            self.assertEqual(detail["evidence_index"], 0)
            self.assertLess(detail["best_similarity"], 0.45)
            self.assertIsNotNone(detail["candidate_line_start"])

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

            review, _ = self.review(db_path)
            result, code = scoring.persist_literature_score(db_path, review)
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
