import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE_RUNTIME = REPO_ROOT / "literature-digest" / "scripts" / "stage_runtime.py"
RUNTIME_DB_PATH = REPO_ROOT / "literature-digest" / "scripts" / "runtime_db.py"


def load_runtime_db_module():
    spec = importlib.util.spec_from_file_location("literature_digest_runtime_db", RUNTIME_DB_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateOutputTests(unittest.TestCase):
    def run_validate(
        self,
        mode: str,
        payload: dict,
        *,
        source_path: Path | None = None,
        preprocess_artifact: Path | None = None,
        db_path: Path | None = None,
    ) -> subprocess.CompletedProcess:
        args = [sys.executable, str(STAGE_RUNTIME), "render_and_validate", "--mode", mode]
        if source_path is not None:
            args += ["--source-path", str(source_path)]
        if preprocess_artifact is not None:
            args += ["--preprocess-artifact", str(preprocess_artifact)]
        if db_path is not None:
            args += ["--db-path", str(db_path)]
        return subprocess.run(
            args,
            input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_fix_migrates_old_fields_and_fills_required(self):
        with tempfile.TemporaryDirectory() as td:
            md_path = Path(td) / "paper.md"
            md_path.write_text("# Title\n\nReferences\n[1] Smith, 2020.\n", encoding="utf-8")

            old = {
                "digest": {"md": "## TL;DR\n..."},
                "references": {"items": [{"raw": "x", "doi": "10.1234/x"}]},
                "citation_analysis": {
                    "meta": {
                        "language": "zh-CN",
                        "scope": {"section_title": "Introduction", "line_start": 1, "line_end": 2},
                    },
                    "summary": "global citation summary",
                    "items": [],
                    "unmapped_mentions": [],
                    "report_md": "## Introduction 引文综述线索\n",
                },
                "provenance": {"generated_at": "2026-01-17T12:34:56Z", "input_hash": "", "model": "gpt-5.2"},
                "warnings": [],
                "error": None,
            }

            p = self.run_validate("fix", old, source_path=md_path)
            self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8", errors="replace"))
            fixed = json.loads(p.stdout.decode("utf-8"))

            self.assertTrue(Path(fixed["digest_path"]).exists())
            self.assertTrue(Path(fixed["references_path"]).exists())
            self.assertTrue(Path(fixed["citation_analysis_path"]).exists())
            self.assertTrue(Path(fixed["citation_analysis_report_path"]).exists())
            refs = json.loads(Path(fixed["references_path"]).read_text(encoding="utf-8"))
            self.assertEqual(refs[0]["DOI"], "10.1234/x")
            self.assertIsNone(fixed["error"])
            self.assertTrue(fixed["provenance"]["input_hash"].startswith("sha256:"))

    def test_check_reports_invalid(self):
        bad = {"digest_path": "", "references_path": "", "citation_analysis_path": ""}
        p = self.run_validate("check", bad)
        self.assertEqual(p.returncode, 2)
        report = json.loads(p.stdout.decode("utf-8"))
        self.assertFalse(report["ok"])
        self.assertTrue(any("missing required key" in e for e in report["errors"]))

    def test_check_rejects_invalid_citation_analysis_file(self):
        with tempfile.TemporaryDirectory() as td:
            ca_path = Path(td) / "citation_analysis.json"
            ca_path.write_text(json.dumps({"meta": {}}, ensure_ascii=False), encoding="utf-8")
            payload = {
                "digest_path": "",
                "references_path": "",
                "citation_analysis_path": str(ca_path),
                "provenance": {"generated_at": "2026-01-17T12:34:56Z", "input_hash": "sha256:abc", "model": "x"},
                "warnings": [],
                "error": None,
            }
            p = self.run_validate("check", payload)
            self.assertEqual(p.returncode, 2)
            report = json.loads(p.stdout.decode("utf-8"))
            self.assertFalse(report["ok"])
            self.assertTrue(any("citation_analysis" in e for e in report["errors"]))

    def test_check_rejects_duplicate_mention_ids(self):
        with tempfile.TemporaryDirectory() as td:
            ca_path = Path(td) / "citation_analysis.json"
            ca_obj = {
                "meta": {"language": "zh-CN", "scope": {"section_title": "Introduction", "line_start": 1, "line_end": 5}},
                "summary": "global citation summary",
                "items": [
                    {
                        "ref_index": 0,
                        "ref_number": 1,
                        "reference": {"author": ["Smith"], "title": "A", "year": 2020},
                        "mentions": [
                            {
                                "mention_id": "m00001",
                                "marker": "[1]",
                                "style": "numeric",
                                "line_start": 2,
                                "line_end": 2,
                                "snippet": "x [1]",
                            }
                        ],
                        "function": "background",
                        "summary": "x",
                        "confidence": 0.9,
                    }
                ],
                "unmapped_mentions": [
                    {
                        "mention_id": "m00001",
                        "marker": "(Smith, 2020)",
                        "style": "author-year",
                        "line_start": 3,
                        "line_end": 3,
                        "snippet": "y",
                    }
                ],
                "report_md": "ok",
            }
            ca_path.write_text(json.dumps(ca_obj, ensure_ascii=False), encoding="utf-8")
            payload = {
                "digest_path": "",
                "references_path": "",
                "citation_analysis_path": str(ca_path),
                "provenance": {"generated_at": "2026-01-17T12:34:56Z", "input_hash": "sha256:abc", "model": "x"},
                "warnings": [],
                "error": None,
            }
            p = self.run_validate("check", payload)
            self.assertEqual(p.returncode, 2)
            report = json.loads(p.stdout.decode("utf-8"))
            self.assertTrue(any("mention_id must be unique" in e for e in report["errors"]))

    def test_check_rejects_mention_coverage_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            ca_path = Path(td) / "citation_analysis.json"
            preprocess_path = Path(td) / "citation_mentions_export.json"
            ca_obj = {
                "meta": {"language": "zh-CN", "scope": {"section_title": "Introduction", "line_start": 1, "line_end": 6}},
                "summary": "global citation summary",
                "items": [
                    {
                        "ref_index": 0,
                        "ref_number": 1,
                        "reference": {"author": ["Smith"], "title": "A", "year": 2020},
                        "mentions": [
                            {
                                "mention_id": "m00001",
                                "marker": "[1]",
                                "style": "numeric",
                                "line_start": 2,
                                "line_end": 2,
                                "snippet": "x [1]",
                            }
                        ],
                        "function": "background",
                        "summary": "x",
                        "confidence": 0.8,
                    }
                ],
                "unmapped_mentions": [],
                "report_md": "ok",
            }
            preprocess_obj = {"stats": {"total_mentions": 2}}
            ca_path.write_text(json.dumps(ca_obj, ensure_ascii=False), encoding="utf-8")
            preprocess_path.write_text(json.dumps(preprocess_obj, ensure_ascii=False), encoding="utf-8")
            payload = {
                "digest_path": "",
                "references_path": "",
                "citation_analysis_path": str(ca_path),
                "provenance": {"generated_at": "2026-01-17T12:34:56Z", "input_hash": "sha256:abc", "model": "x"},
                "warnings": [],
                "error": None,
            }
            p = self.run_validate("check", payload, preprocess_artifact=preprocess_path)
            self.assertEqual(p.returncode, 2)
            report = json.loads(p.stdout.decode("utf-8"))
            self.assertTrue(any("mention coverage mismatch" in e for e in report["errors"]))

    def test_check_accepts_stage_error_code_shape(self):
        payload = {
            "digest_path": "",
            "references_path": "",
            "citation_analysis_path": "",
            "provenance": {"generated_at": "2026-01-17T12:34:56Z", "input_hash": "sha256:abc", "model": "x"},
            "warnings": [],
            "error": {"code": "citation_merge_failed", "message": "coverage mismatch"},
        }
        p = self.run_validate("check", payload)
        self.assertEqual(p.returncode, 0, p.stdout.decode("utf-8"))

    def test_render_mode_rejects_explicit_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            source_path = Path(td) / "paper.md"
            source_path.write_text("# Title\n", encoding="utf-8")
            p = subprocess.run(
                [
                    sys.executable,
                    str(STAGE_RUNTIME),
                    "render_and_validate",
                    "--mode",
                    "render",
                    "--source-path",
                    str(source_path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(p.returncode, 2)
            payload = json.loads(p.stdout.decode("utf-8"))
            self.assertEqual(payload["error"]["code"], "citation_report_failed")

    def test_check_rejects_db_registry_mismatch(self):
        runtime_db = load_runtime_db_module()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / ".literature_digest_tmp" / "literature_digest.db"
            runtime_db.initialize_database(db_path)
            digest_path = Path(td) / "digest.md"
            references_path = Path(td) / "references.json"
            citation_path = Path(td) / "citation_analysis.json"
            digest_path.write_text("x\n", encoding="utf-8")
            references_path.write_text("[]", encoding="utf-8")
            citation_path.write_text(
                json.dumps(
                    {
                        "meta": {"language": "zh-CN", "scope": {"section_title": "Introduction", "line_start": 1, "line_end": 1}},
                        "summary": "global citation summary",
                        "items": [],
                        "unmapped_mentions": [],
                        "report_md": "",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with runtime_db.connect_db(db_path) as connection:
                runtime_db.set_runtime_input(connection, "generated_at", "2026-01-17T12:34:56Z")
                runtime_db.set_runtime_input(connection, "input_hash", "sha256:abc")
                runtime_db.set_runtime_input(connection, "model", "x")
                runtime_db.register_artifact(
                    connection,
                    artifact_key="digest_path",
                    path=Path(td) / "other_digest.md",
                    is_required=True,
                    media_type="text/markdown",
                    source_table="digest_slots",
                )
                runtime_db.register_artifact(
                    connection,
                    artifact_key="references_path",
                    path=references_path,
                    is_required=True,
                    media_type="application/json",
                    source_table="reference_items",
                )
                runtime_db.register_artifact(
                    connection,
                    artifact_key="citation_analysis_path",
                    path=citation_path,
                    is_required=True,
                    media_type="application/json",
                    source_table="citation_summary",
                )
                connection.commit()
            payload = {
                "digest_path": str(digest_path),
                "references_path": str(references_path),
                "citation_analysis_path": str(citation_path),
                "provenance": {"generated_at": "2026-01-17T12:34:56Z", "input_hash": "sha256:abc", "model": "x"},
                "warnings": [],
                "error": None,
            }
            p = self.run_validate("check", payload, db_path=db_path)
            self.assertEqual(p.returncode, 2)
            report = json.loads(p.stdout.decode("utf-8"))
            self.assertTrue(any("artifact registry" in e for e in report["errors"]))


if __name__ == "__main__":
    unittest.main()
