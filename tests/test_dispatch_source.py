import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE_RUNTIME = REPO_ROOT / "literature-digest" / "scripts" / "stage_runtime.py"


def build_simple_pdf(text: str) -> bytes:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin-1")
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            b"3 0 obj\n"
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\n"
            b"endobj\n"
        ),
        (
            f"4 0 obj\n<< /Length {len(content)} >>\nstream\n".encode("latin-1")
            + content
            + b"\nendstream\nendobj\n"
        ),
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]

    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    pdf_parts = [header]
    offsets: list[int] = []
    cursor = len(header)
    for obj in objects:
        offsets.append(cursor)
        pdf_parts.append(obj)
        cursor += len(obj)

    xref_offset = cursor
    xref = [b"xref\n0 6\n0000000000 65535 f \n"]
    for offset in offsets:
        xref.append(f"{offset:010d} 00000 n \n".encode("latin-1"))
    trailer = (
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(xref_offset).encode("latin-1")
        + b"\n%%EOF\n"
    )

    return b"".join(pdf_parts + xref + [trailer])


class NormalizeSourceTests(unittest.TestCase):
    def run_normalize(
        self,
        source_path: Path,
        out_md: Path,
        out_meta: Path,
        *,
        disable_pymupdf4llm: bool = False,
    ) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        if disable_pymupdf4llm:
            env["LITERATURE_DIGEST_DISABLE_PYMUPDF4LLM"] = "1"
        db_path = source_path.parent / ".literature_digest_tmp" / "literature_digest.db"
        bootstrap = subprocess.run(
            [
                sys.executable,
                str(STAGE_RUNTIME),
                "bootstrap_runtime_db",
                "--db-path",
                str(db_path),
                "--source-path",
                str(source_path),
                "--language",
                "zh-CN",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
        )
        self.assertEqual(bootstrap.returncode, 0, bootstrap.stderr.decode("utf-8", errors="replace"))
        return subprocess.run(
            [
                sys.executable,
                str(STAGE_RUNTIME),
                "normalize_source",
                "--db-path",
                str(db_path),
                "--out-md",
                str(out_md),
                "--out-meta",
                str(out_meta),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
        )

    def test_extensionless_markdown_is_copied_to_normalized_source(self):
        with tempfile.TemporaryDirectory() as td:
            source_path = Path(td) / "payload"
            out_md = Path(td) / ".literature_digest_tmp" / "source.md"
            out_meta = Path(td) / ".literature_digest_tmp" / "source_meta.json"
            markdown = "# Title\n\n## References\n- Ref\n"
            source_path.write_text(markdown, encoding="utf-8")

            result = self.run_normalize(source_path, out_md, out_meta)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(result.stdout.decode("utf-8"))
            meta = json.loads(out_meta.read_text(encoding="utf-8"))

            self.assertIsNone(payload["error"])
            self.assertEqual(out_md.read_text(encoding="utf-8"), markdown)
            self.assertEqual(meta["source_type"], "markdown")
            self.assertEqual(meta["detection_method"], "utf8_text")
            self.assertEqual(meta["conversion_backend"], "direct_copy")

    def test_pdf_signature_wins_even_when_extension_is_md(self):
        with tempfile.TemporaryDirectory() as td:
            source_path = Path(td) / "paper.md"
            out_md = Path(td) / ".literature_digest_tmp" / "source.md"
            out_meta = Path(td) / ".literature_digest_tmp" / "source_meta.json"
            source_path.write_bytes(build_simple_pdf("Introduction References Baseline"))

            result = self.run_normalize(source_path, out_md, out_meta, disable_pymupdf4llm=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(result.stdout.decode("utf-8"))
            meta = json.loads(out_meta.read_text(encoding="utf-8"))

            self.assertIsNone(payload["error"])
            self.assertEqual(meta["source_type"], "pdf")
            self.assertEqual(meta["detection_method"], "pdf_signature")
            self.assertEqual(meta["conversion_backend"], "stdlib_fallback")
            self.assertTrue(any("ignored; content detected as PDF" in warning for warning in payload["warnings"]))
            self.assertTrue(any("fell back to stdlib" in warning for warning in payload["warnings"]))
            self.assertIn("Introduction", out_md.read_text(encoding="utf-8"))

    def test_unsupported_binary_returns_schema_compatible_error(self):
        with tempfile.TemporaryDirectory() as td:
            source_path = Path(td) / "payload"
            out_md = Path(td) / ".literature_digest_tmp" / "source.md"
            out_meta = Path(td) / ".literature_digest_tmp" / "source_meta.json"
            source_path.write_bytes(b"\xff\x00\x81\x82")

            result = self.run_normalize(source_path, out_md, out_meta)
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout.decode("utf-8"))
            meta = json.loads(out_meta.read_text(encoding="utf-8"))

            self.assertEqual(payload["error"]["code"], "UNSUPPORTED_INPUT")
            self.assertEqual(meta["error"]["code"], "UNSUPPORTED_INPUT")

    def test_single_tex_is_normalized_as_fenced_raw_latex(self):
        with tempfile.TemporaryDirectory() as td:
            source_path = Path(td) / "paper.tex"
            out_md = Path(td) / ".literature_digest_tmp" / "source.md"
            out_meta = Path(td) / ".literature_digest_tmp" / "source_meta.json"
            source_path.write_text(
                "\\documentclass{article}\n\\begin{document}\nHello from LaTeX.\n\\end{document}\n",
                encoding="utf-8",
            )

            result = self.run_normalize(source_path, out_md, out_meta)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            meta = json.loads(out_meta.read_text(encoding="utf-8"))
            normalized = out_md.read_text(encoding="utf-8")

            self.assertEqual(meta["source_type"], "latex_tex")
            self.assertEqual(meta["conversion_backend"], "fenced_raw_latex")
            self.assertIn("```tex", normalized)
            self.assertIn("\\documentclass{article}", normalized)
            self.assertIn("Hello from LaTeX.", normalized)

    def test_latex_project_is_flattened_and_appends_bibtex_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            project_dir = Path(td) / "paper_project"
            sections_dir = project_dir / "sections"
            sections_dir.mkdir(parents=True)
            main_tex = project_dir / "main.tex"
            intro_tex = sections_dir / "intro.tex"
            bib_path = project_dir / "refs.bib"
            main_tex.write_text(
                "\\documentclass{article}\n"
                "\\begin{document}\n"
                "\\input{sections/intro}\n"
                "\\addbibresource{refs.bib}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
            intro_tex.write_text("Intro text from included file.\n", encoding="utf-8")
            bib_path.write_text(
                "@article{smith2020,\n"
                "  author = {Smith, J.},\n"
                "  title = {Paper A},\n"
                "  journal = {Journal A},\n"
                "  year = {2020}\n"
                "}\n",
                encoding="utf-8",
            )
            out_md = Path(td) / ".literature_digest_tmp" / "source.md"
            out_meta = Path(td) / ".literature_digest_tmp" / "source_meta.json"

            result = self.run_normalize(project_dir, out_md, out_meta)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            meta = json.loads(out_meta.read_text(encoding="utf-8"))
            normalized = out_md.read_text(encoding="utf-8")

            self.assertEqual(meta["source_type"], "latex_project")
            self.assertEqual(meta["conversion_backend"], "fenced_raw_latex")
            self.assertEqual(Path(meta["main_tex_path"]), main_tex.resolve())
            self.assertIn(str(intro_tex.resolve()), meta["included_tex_files"])
            self.assertIn(str(bib_path.resolve()), meta["bib_files"])
            self.assertIn("```tex", normalized)
            self.assertIn("% >>> BEGIN INCLUDED FILE: sections/intro.tex", normalized)
            self.assertIn("Intro text from included file.", normalized)
            self.assertIn("```bibtex", normalized)
            self.assertIn("@article{smith2020", normalized)


if __name__ == "__main__":
    unittest.main()
