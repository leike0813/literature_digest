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


class CitationPreprocessTests(unittest.TestCase):
    def seed_db(self, db_path: Path, *, markdown: str, citation_scope: dict | None) -> None:
        runtime_db = load_runtime_db_module()
        runtime_db.initialize_database(db_path)
        with runtime_db.connect_db(db_path) as connection:
            runtime_db.set_runtime_input(connection, "source_path", str(db_path.parent / "paper.md"))
            runtime_db.set_runtime_input(connection, "language", "zh-CN")
            runtime_db.store_source_document(
                connection,
                doc_key="normalized_source",
                content=markdown,
                metadata={"heading_reliability": "high", "reference_numbering_reliability": "unknown"},
            )
            if citation_scope is not None:
                runtime_db.store_section_scope(
                    connection,
                    scope_key="citation_scope",
                    section_title=str(citation_scope["section_title"]),
                    line_start=int(citation_scope["line_start"]),
                    line_end=int(citation_scope["line_end"]),
                    metadata=dict(citation_scope.get("metadata", {})),
                )
            connection.commit()

    def run_preprocess(
        self,
        db_path: Path,
        out_path: Path | None = None,
        *,
        input_obj: dict | None = None,
        extra_args: list[str] | None = None,
    ) -> subprocess.CompletedProcess:
        args = [
            sys.executable,
            str(STAGE_RUNTIME),
            "prepare_citation_workset",
            "--db-path",
            str(db_path),
        ]
        if out_path is not None:
            args += ["--out", str(out_path)]
        if extra_args:
            args += extra_args
        return subprocess.run(
            args,
            input=None if input_obj is None else json.dumps(input_obj, ensure_ascii=False).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_extracts_mentions_from_db_scope(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            db_path = td_path / ".literature_digest_tmp" / "literature_digest.db"
            out_path = td_path / "tmp" / "citation_workset_export.json"
            markdown = "\n".join(
                [
                    "# 1 Introduction",
                    "Prior work uses transformer backbones [5, 7-8].",
                    "As shown by Smith et al. (2020) and (Brown, 2019; Clark, 2021).",
                    "## 1.1 Overview",
                    "Additional references [10].",
                    "# 2 Method",
                    "Method details [30].",
                ]
            )
            self.seed_db(
                db_path,
                markdown=markdown,
                citation_scope={"section_title": "Introduction", "line_start": 1, "line_end": 5},
            )

            p = self.run_preprocess(db_path=db_path, out_path=out_path)
            self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8", errors="replace"))
            data = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertIsNone(data["error"])
            self.assertEqual(data["meta"]["scope"]["line_start"], 1)
            self.assertEqual(data["meta"]["scope"]["line_end"], 5)
            self.assertEqual(data["meta"]["scope_source"], "db")
            self.assertGreaterEqual(data["stats"]["numeric_mentions"], 4)
            self.assertGreaterEqual(data["stats"]["author_year_mentions"], 3)
            self.assertIn("workset_items", data)
            self.assertIn("mention_links", data)

    def test_returns_error_when_scope_missing_in_db(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            db_path = td_path / ".literature_digest_tmp" / "literature_digest.db"
            out_path = td_path / "tmp" / "citation_workset_export.json"
            markdown = "# 1 Background\nThis section has [1].\n# 2 Method\nNo introduction title appears.\n"
            self.seed_db(db_path, markdown=markdown, citation_scope=None)

            p = self.run_preprocess(db_path=db_path, out_path=out_path)
            self.assertEqual(p.returncode, 2)
            data = json.loads(p.stdout.decode("utf-8"))
            self.assertEqual(data["error"]["code"], "citation_scope_failed")

    def test_rejects_scope_override_interfaces(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            db_path = td_path / ".literature_digest_tmp" / "literature_digest.db"
            markdown = "# 1 Introduction\nOnly one citation [1].\n"
            self.seed_db(
                db_path,
                markdown=markdown,
                citation_scope={"section_title": "Introduction", "line_start": 1, "line_end": 2},
            )

            p = self.run_preprocess(db_path=db_path, input_obj={"scope": {"section_title": "X", "line_start": 1, "line_end": 1}})
            self.assertEqual(p.returncode, 2)
            data = json.loads(p.stdout.decode("utf-8"))
            self.assertEqual(data["error"]["code"], "citation_scope_failed")

            cli_override = self.run_preprocess(db_path=db_path, extra_args=["--scope-file", "x.json"])
            self.assertEqual(cli_override.returncode, 2)


if __name__ == "__main__":
    unittest.main()
