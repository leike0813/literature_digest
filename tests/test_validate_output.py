import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE = REPO_ROOT / "literature-digest" / "scripts" / "validate_output.py"


class ValidateOutputTests(unittest.TestCase):
    def run_validate(
        self,
        mode: str,
        payload: dict,
        md_path: Path | None = None,
        preprocess_artifact: Path | None = None,
    ) -> subprocess.CompletedProcess:
        args = ["python", str(VALIDATE), "--mode", mode]
        if md_path is not None:
            args += ["--md-path", str(md_path)]
        if preprocess_artifact is not None:
            args += ["--preprocess-artifact", str(preprocess_artifact)]
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
                    "items": [],
                    "unmapped_mentions": [],
                    "report_md": "## Introduction 引文综述线索\n",
                },
                "provenance": {"generated_at": "2026-01-17T12:34:56Z", "input_hash": "", "model": "gpt-5.2"},
                "warnings": [],
                "error": None,
            }

            p = self.run_validate("fix", old, md_path=md_path)
            self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8", errors="replace"))
            fixed = json.loads(p.stdout.decode("utf-8"))

            self.assertIsInstance(fixed["digest_path"], str)
            self.assertIsInstance(fixed["references_path"], str)
            self.assertIsInstance(fixed["citation_analysis_path"], str)
            self.assertTrue(Path(fixed["digest_path"]).exists())
            self.assertTrue(Path(fixed["references_path"]).exists())
            self.assertTrue(Path(fixed["citation_analysis_path"]).exists())
            self.assertEqual(Path(fixed["digest_path"]).name, "digest.md")
            self.assertEqual(Path(fixed["references_path"]).name, "references.json")
            self.assertEqual(Path(fixed["citation_analysis_path"]).name, "citation_analysis.json")
            self.assertEqual(Path(fixed["digest_path"]).parent, md_path.parent)
            self.assertEqual(Path(fixed["references_path"]).parent, md_path.parent)
            self.assertEqual(Path(fixed["citation_analysis_path"]).parent, md_path.parent)
            refs = json.loads(Path(fixed["references_path"]).read_text(encoding="utf-8"))
            self.assertEqual(refs[0]["DOI"], "10.1234/x")
            self.assertIn("warnings", fixed)
            self.assertIn("error", fixed)
            self.assertIsNone(fixed["error"])
            self.assertTrue(fixed["provenance"]["input_hash"].startswith("sha256:"))
            self.assertIsInstance(fixed["provenance"]["model"], str)

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
            self.assertFalse(report["ok"])
            self.assertTrue(any("mention_id must be unique" in e for e in report["errors"]))

    def test_check_rejects_mention_coverage_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            ca_path = Path(td) / "citation_analysis.json"
            preprocess_path = Path(td) / "citation_preprocess.json"
            ca_obj = {
                "meta": {"language": "zh-CN", "scope": {"section_title": "Introduction", "line_start": 1, "line_end": 6}},
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
            self.assertFalse(report["ok"])
            self.assertTrue(any("mention coverage mismatch" in e for e in report["errors"]))


if __name__ == "__main__":
    unittest.main()
