import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_STAGING = REPO_ROOT / "literature-digest" / "scripts" / "references_staging.py"


class ReferencesStagingTests(unittest.TestCase):
    def run_stage(self, md_path: Path, tmp_dir: Path, batch_size: int = 15) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(REFERENCES_STAGING),
                "stage",
                "--md-path",
                str(md_path),
                "--tmp-dir",
                str(tmp_dir),
                "--batch-size",
                str(batch_size),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def run_merge(self, parts_dir: Path, merged_path: Path, publish_path: Path | None = None) -> subprocess.CompletedProcess:
        args = [
            sys.executable,
            str(REFERENCES_STAGING),
            "merge",
            "--parts-dir",
            str(parts_dir),
            "--merged-path",
            str(merged_path),
        ]
        if publish_path is not None:
            args += ["--publish-path", str(publish_path)]
        return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

    def test_stage_splits_references_into_fixed_batches(self):
        with tempfile.TemporaryDirectory() as td:
            md_path = Path(td) / "paper.md"
            tmp_dir = Path(td) / ".literature_digest_tmp"
            lines = ["# Title", "Intro", "## References"]
            for idx in range(1, 18):
                lines.append(f"[{idx}] Author {idx}. Reference title {idx}. Journal, 2024.")
            md_path.write_text("\n".join(lines), encoding="utf-8")

            result = self.run_stage(md_path, tmp_dir)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(result.stdout.decode("utf-8"))

            self.assertEqual(payload["part_count"], 2)
            self.assertEqual(payload["entry_count"], 17)
            part_001 = json.loads((tmp_dir / "references.parts" / "part-001.json").read_text(encoding="utf-8"))
            part_002 = json.loads((tmp_dir / "references.parts" / "part-002.json").read_text(encoding="utf-8"))
            self.assertEqual(len(part_001), 15)
            self.assertEqual(len(part_002), 2)
            self.assertEqual(part_001[0]["raw"], "[1] Author 1. Reference title 1. Journal, 2024.")
            self.assertEqual(part_002[-1]["raw"], "[17] Author 17. Reference title 17. Journal, 2024.")

    def test_merge_sorts_parts_and_publishes_atomically(self):
        with tempfile.TemporaryDirectory() as td:
            parts_dir = Path(td) / "references.parts"
            merged_path = Path(td) / ".literature_digest_tmp" / "references_merged.json"
            publish_path = Path(td) / "references.json"
            parts_dir.mkdir(parents=True, exist_ok=True)

            (parts_dir / "part-002.json").write_text(
                json.dumps([{"author": [], "title": "", "year": 2023, "raw": "[2] Ref two", "confidence": 0.1}]),
                encoding="utf-8",
            )
            (parts_dir / "part-001.json").write_text(
                json.dumps([{"author": [], "title": "", "year": 2022, "raw": "[1] Ref one", "confidence": 0.1}]),
                encoding="utf-8",
            )
            publish_path.write_text("old", encoding="utf-8")

            result = self.run_merge(parts_dir, merged_path, publish_path)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(result.stdout.decode("utf-8"))
            merged = json.loads(merged_path.read_text(encoding="utf-8"))
            published = json.loads(publish_path.read_text(encoding="utf-8"))

            self.assertIsNone(payload["error"])
            self.assertEqual([item["raw"] for item in merged], ["[1] Ref one", "[2] Ref two"])
            self.assertEqual(merged, published)

    def test_merge_failure_does_not_publish_final_file(self):
        with tempfile.TemporaryDirectory() as td:
            parts_dir = Path(td) / "references.parts"
            merged_path = Path(td) / ".literature_digest_tmp" / "references_merged.json"
            publish_path = Path(td) / "references.json"
            parts_dir.mkdir(parents=True, exist_ok=True)
            (parts_dir / "part-001.json").write_text(json.dumps({"bad": "shape"}), encoding="utf-8")

            result = self.run_merge(parts_dir, merged_path, publish_path)
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout.decode("utf-8"))

            self.assertEqual(payload["error"]["code"], "references_merge_failed")
            self.assertFalse(publish_path.exists())


if __name__ == "__main__":
    unittest.main()
