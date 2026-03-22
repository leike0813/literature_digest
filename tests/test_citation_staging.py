import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CITATION_STAGING = REPO_ROOT / "literature-digest" / "scripts" / "citation_staging.py"


def make_mapped_item(ref_index: int, mention_id: str) -> dict:
    return {
        "ref_index": ref_index,
        "ref_number": ref_index + 1,
        "reference": {"author": ["Smith"], "title": f"Ref {ref_index}", "year": 2020 + ref_index},
        "mentions": [
            {
                "mention_id": mention_id,
                "marker": f"[{ref_index + 1}]",
                "style": "numeric",
                "line_start": 2,
                "line_end": 2,
                "snippet": "snippet",
            }
        ],
        "function": "background",
        "summary": "summary",
        "confidence": 0.8,
    }


def make_unmapped(mention_id: str) -> dict:
    return {
        "mention_id": mention_id,
        "marker": "(Brown, 2020)",
        "style": "author-year",
        "line_start": 3,
        "line_end": 3,
        "snippet": "snippet",
        "reason": "ambiguous",
    }


class CitationStagingTests(unittest.TestCase):
    def run_merge(
        self,
        parts_dir: Path,
        preprocess_path: Path,
        merged_path: Path,
        *,
        publish_path: Path | None = None,
        report_md_path: Path | None = None,
        scope_file: Path | None = None,
    ) -> subprocess.CompletedProcess:
        args = [
            sys.executable,
            str(CITATION_STAGING),
            "--parts-dir",
            str(parts_dir),
            "--preprocess-path",
            str(preprocess_path),
            "--merged-path",
            str(merged_path),
            "--language",
            "zh-CN",
        ]
        if publish_path is not None:
            args += ["--publish-path", str(publish_path)]
        if report_md_path is not None:
            args += ["--report-md-path", str(report_md_path)]
        if scope_file is not None:
            args += ["--scope-file", str(scope_file)]
        return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

    def test_merge_validates_coverage_and_publishes(self):
        with tempfile.TemporaryDirectory() as td:
            parts_dir = Path(td) / "citation.parts"
            preprocess_path = Path(td) / "citation_preprocess.json"
            merged_path = Path(td) / ".literature_digest_tmp" / "citation_merged.json"
            publish_path = Path(td) / "citation_analysis.json"
            report_md_path = Path(td) / "citation_report.md"
            parts_dir.mkdir(parents=True, exist_ok=True)

            preprocess_path.write_text(
                json.dumps(
                    {
                        "meta": {"scope": {"section_title": "Introduction", "line_start": 1, "line_end": 8}},
                        "stats": {"total_mentions": 3},
                    }
                ),
                encoding="utf-8",
            )
            report_md_path.write_text("## Report\n", encoding="utf-8")
            (parts_dir / "part-002.json").write_text(
                json.dumps({"items": [make_mapped_item(1, "m00002")], "unmapped_mentions": [make_unmapped("m00003")]}),
                encoding="utf-8",
            )
            (parts_dir / "part-001.json").write_text(
                json.dumps({"items": [make_mapped_item(0, "m00001")], "unmapped_mentions": []}),
                encoding="utf-8",
            )

            result = self.run_merge(parts_dir, preprocess_path, merged_path, publish_path=publish_path, report_md_path=report_md_path)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(result.stdout.decode("utf-8"))
            merged = json.loads(merged_path.read_text(encoding="utf-8"))

            self.assertIsNone(payload["error"])
            self.assertEqual(len(merged["items"]), 2)
            self.assertEqual(len(merged["unmapped_mentions"]), 1)
            self.assertEqual(merged["report_md"], "## Report\n")
            self.assertTrue(publish_path.exists())

    def test_duplicate_mention_id_fails_without_publish(self):
        with tempfile.TemporaryDirectory() as td:
            parts_dir = Path(td) / "citation.parts"
            preprocess_path = Path(td) / "citation_preprocess.json"
            merged_path = Path(td) / ".literature_digest_tmp" / "citation_merged.json"
            publish_path = Path(td) / "citation_analysis.json"
            report_md_path = Path(td) / "citation_report.md"
            parts_dir.mkdir(parents=True, exist_ok=True)
            preprocess_path.write_text(
                json.dumps(
                    {
                        "meta": {"scope": {"section_title": "Introduction", "line_start": 1, "line_end": 8}},
                        "stats": {"total_mentions": 2},
                    }
                ),
                encoding="utf-8",
            )
            report_md_path.write_text("## Report\n", encoding="utf-8")
            (parts_dir / "part-001.json").write_text(
                json.dumps({"items": [make_mapped_item(0, "m00001")], "unmapped_mentions": [make_unmapped("m00001")]}),
                encoding="utf-8",
            )

            result = self.run_merge(parts_dir, preprocess_path, merged_path, publish_path=publish_path, report_md_path=report_md_path)
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(payload["error"]["code"], "citation_merge_failed")
            self.assertFalse(publish_path.exists())

    def test_duplicate_ref_index_fails(self):
        with tempfile.TemporaryDirectory() as td:
            parts_dir = Path(td) / "citation.parts"
            preprocess_path = Path(td) / "citation_preprocess.json"
            merged_path = Path(td) / ".literature_digest_tmp" / "citation_merged.json"
            report_md_path = Path(td) / "citation_report.md"
            parts_dir.mkdir(parents=True, exist_ok=True)
            preprocess_path.write_text(
                json.dumps(
                    {
                        "meta": {"scope": {"section_title": "Introduction", "line_start": 1, "line_end": 8}},
                        "stats": {"total_mentions": 2},
                    }
                ),
                encoding="utf-8",
            )
            report_md_path.write_text("## Report\n", encoding="utf-8")
            (parts_dir / "part-001.json").write_text(
                json.dumps({"items": [make_mapped_item(0, "m00001")], "unmapped_mentions": []}),
                encoding="utf-8",
            )
            (parts_dir / "part-002.json").write_text(
                json.dumps({"items": [make_mapped_item(0, "m00002")], "unmapped_mentions": []}),
                encoding="utf-8",
            )

            result = self.run_merge(parts_dir, preprocess_path, merged_path, report_md_path=report_md_path)
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(payload["error"]["code"], "citation_merge_failed")

    def test_report_stage_failure_blocks_publish(self):
        with tempfile.TemporaryDirectory() as td:
            parts_dir = Path(td) / "citation.parts"
            preprocess_path = Path(td) / "citation_preprocess.json"
            merged_path = Path(td) / ".literature_digest_tmp" / "citation_merged.json"
            publish_path = Path(td) / "citation_analysis.json"
            missing_report = Path(td) / "citation_report.md"
            parts_dir.mkdir(parents=True, exist_ok=True)
            preprocess_path.write_text(
                json.dumps(
                    {
                        "meta": {"scope": {"section_title": "Introduction", "line_start": 1, "line_end": 8}},
                        "stats": {"total_mentions": 1},
                    }
                ),
                encoding="utf-8",
            )
            (parts_dir / "part-001.json").write_text(
                json.dumps({"items": [make_mapped_item(0, "m00001")], "unmapped_mentions": []}),
                encoding="utf-8",
            )

            result = self.run_merge(parts_dir, preprocess_path, merged_path, publish_path=publish_path, report_md_path=missing_report)
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(payload["error"]["code"], "citation_report_failed")
            self.assertFalse(publish_path.exists())


if __name__ == "__main__":
    unittest.main()
