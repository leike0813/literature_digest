import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE = REPO_ROOT / "literature-digest" / "scripts" / "validate_output.py"


class ValidateOutputTests(unittest.TestCase):
    def run_validate(self, mode: str, payload: dict, md_path: Path | None = None) -> subprocess.CompletedProcess:
        args = ["python", str(VALIDATE), "--mode", mode]
        if md_path is not None:
            args += ["--md-path", str(md_path)]
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
                "schema_version": "paper_digest_v1",
                "parent_itemKey": "ABCD1234",
                "md_attachment_key": "EFGH5678",
                "digest": {"md": "## TL;DR\n..."},
                "references": {"items": [{"raw": "x", "doi": "10.1234/x"}]},
                "provenance": {"generated_at": "2026-01-17T12:34:56Z", "input_hash": ""},
            }

            p = self.run_validate("fix", old, md_path=md_path)
            self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8", errors="replace"))
            fixed = json.loads(p.stdout.decode("utf-8"))

            self.assertEqual(fixed["schema_version"], "literature_digest_v1")
            self.assertIsInstance(fixed["digest_path"], str)
            self.assertIsInstance(fixed["references_path"], str)
            self.assertTrue(Path(fixed["digest_path"]).exists())
            self.assertTrue(Path(fixed["references_path"]).exists())
            self.assertEqual(Path(fixed["digest_path"]).name, "digest.md")
            self.assertEqual(Path(fixed["references_path"]).name, "references.json")
            self.assertEqual(Path(fixed["digest_path"]).parent, md_path.parent)
            self.assertEqual(Path(fixed["references_path"]).parent, md_path.parent)
            refs = json.loads(Path(fixed["references_path"]).read_text(encoding="utf-8"))
            self.assertEqual(refs[0]["DOI"], "10.1234/x")
            self.assertIn("warnings", fixed)
            self.assertIn("error", fixed)
            self.assertIsNone(fixed["error"])
            self.assertTrue(fixed["provenance"]["input_hash"].startswith("sha256:"))

    def test_check_reports_invalid(self):
        bad = {"schema_version": "literature_digest_v1"}
        p = self.run_validate("check", bad)
        self.assertEqual(p.returncode, 2)
        report = json.loads(p.stdout.decode("utf-8"))
        self.assertFalse(report["ok"])
        self.assertTrue(any("missing required key" in e for e in report["errors"]))


if __name__ == "__main__":
    unittest.main()
