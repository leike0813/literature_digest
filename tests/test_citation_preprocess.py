import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PREPROCESS = REPO_ROOT / "literature-digest" / "scripts" / "citation_preprocess.py"


class CitationPreprocessTests(unittest.TestCase):
    def run_preprocess(
        self,
        md_path: Path,
        out_path: Path | None = None,
        references_path: Path | None = None,
        scope_file: Path | None = None,
        scope_start: int | None = None,
        scope_end: int | None = None,
        scope_title: str | None = None,
    ) -> subprocess.CompletedProcess:
        args = ["python", str(PREPROCESS), "--md-path", str(md_path)]
        if out_path is not None:
            args += ["--out", str(out_path)]
        if references_path is not None:
            args += ["--references-path", str(references_path)]
        if scope_file is not None:
            args += ["--scope-file", str(scope_file)]
        if scope_start is not None:
            args += ["--scope-start", str(scope_start)]
        if scope_end is not None:
            args += ["--scope-end", str(scope_end)]
        if scope_title is not None:
            args += ["--scope-title", scope_title]
        return subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_extracts_intro_scope_numeric_and_author_year(self):
        with tempfile.TemporaryDirectory() as td:
            md_path = Path(td) / "paper.md"
            out_path = Path(td) / "tmp" / "citation_preprocess.json"
            md_path.write_text(
                "\n".join(
                    [
                        "# 1 Introduction",
                        "Prior work uses transformer backbones [5, 7-8].",
                        "As shown by Smith et al. (2020) and (Brown, 2019; Clark, 2021).",
                        "## 1.1 Overview",
                        "Additional references [10].",
                        "# 2 Method",
                        "Method details [30].",
                    ]
                ),
                encoding="utf-8",
            )

            p = self.run_preprocess(md_path=md_path, out_path=out_path)
            self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8", errors="replace"))
            self.assertTrue(out_path.exists())

            data = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertIsNone(data["error"])
            self.assertEqual(data["meta"]["scope"]["line_start"], 1)
            self.assertEqual(data["meta"]["scope"]["line_end"], 5)
            self.assertGreaterEqual(data["stats"]["numeric_mentions"], 4)
            self.assertGreaterEqual(data["stats"]["author_year_mentions"], 3)
            self.assertEqual(data["stats"]["total_mentions"], len(data["mentions"]))

            lines = [mention["line_start"] for mention in data["mentions"]]
            self.assertTrue(all(1 <= line <= 5 for line in lines))
            self.assertTrue(any(mention["marker"] == "[7]" for mention in data["mentions"]))
            self.assertTrue(any(mention["marker"] == "[8]" for mention in data["mentions"]))

    def test_returns_error_when_introduction_missing(self):
        with tempfile.TemporaryDirectory() as td:
            md_path = Path(td) / "paper.md"
            out_path = Path(td) / "tmp" / "citation_preprocess.json"
            md_path.write_text(
                "\n".join(
                    [
                        "# 1 Background",
                        "This section has [1].",
                        "# 2 Method",
                        "No introduction title appears.",
                    ]
                ),
                encoding="utf-8",
            )

            p = self.run_preprocess(md_path=md_path, out_path=out_path)
            self.assertEqual(p.returncode, 2)
            data = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertIsNotNone(data["error"])
            self.assertEqual(data["error"]["code"], "SCOPE_NOT_FOUND")
            self.assertEqual(data["stats"]["total_mentions"], 0)

    def test_uses_agent_scope_file_for_related_works(self):
        with tempfile.TemporaryDirectory() as td:
            md_path = Path(td) / "paper.md"
            scope_path = Path(td) / "scope.json"
            out_path = Path(td) / "tmp" / "citation_preprocess.json"
            md_path.write_text(
                "\n".join(
                    [
                        "# 1 Introduction",
                        "Only one citation [1].",
                        "# 2 Related Works",
                        "Prior methods [3, 4] are competitive.",
                        "Smith et al. (2020) improves robustness.",
                        "# 3 Method",
                        "No citation to include [9].",
                    ]
                ),
                encoding="utf-8",
            )
            scope_obj = {"analysis_scope": {"section_title": "Related Works", "line_start": 3, "line_end": 5}}
            scope_path.write_text(json.dumps(scope_obj, ensure_ascii=False), encoding="utf-8")

            p = self.run_preprocess(md_path=md_path, out_path=out_path, scope_file=scope_path)
            self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8", errors="replace"))
            data = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(data["meta"]["scope"]["section_title"], "Related Works")
            self.assertEqual(data["meta"]["scope_source"], "agent")
            self.assertGreaterEqual(data["stats"]["total_mentions"], 3)
            self.assertTrue(all(3 <= m["line_start"] <= 5 for m in data["mentions"]))


if __name__ == "__main__":
    unittest.main()
