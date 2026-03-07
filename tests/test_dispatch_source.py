import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DISPATCH = REPO_ROOT / "literature-digest" / "scripts" / "dispatch_source.py"


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


class DispatchSourceTests(unittest.TestCase):
    def run_dispatch(
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
        return subprocess.run(
            [
                "python",
                str(DISPATCH),
                "--source-path",
                str(source_path),
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

            result = self.run_dispatch(source_path, out_md, out_meta)
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

            result = self.run_dispatch(source_path, out_md, out_meta, disable_pymupdf4llm=True)
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

    def test_utf8_text_wins_even_when_extension_is_pdf(self):
        with tempfile.TemporaryDirectory() as td:
            source_path = Path(td) / "paper.pdf"
            out_md = Path(td) / ".literature_digest_tmp" / "source.md"
            out_meta = Path(td) / ".literature_digest_tmp" / "source_meta.json"
            source_path.write_text("# Intro\n\ntext\n", encoding="utf-8")

            result = self.run_dispatch(source_path, out_md, out_meta)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            payload = json.loads(result.stdout.decode("utf-8"))
            meta = json.loads(out_meta.read_text(encoding="utf-8"))

            self.assertEqual(meta["source_type"], "markdown")
            self.assertEqual(meta["conversion_backend"], "direct_copy")
            self.assertTrue(any("content detected as UTF-8 text" in warning for warning in payload["warnings"]))

    def test_unsupported_binary_returns_schema_compatible_error(self):
        with tempfile.TemporaryDirectory() as td:
            source_path = Path(td) / "payload"
            out_md = Path(td) / ".literature_digest_tmp" / "source.md"
            out_meta = Path(td) / ".literature_digest_tmp" / "source_meta.json"
            source_path.write_bytes(b"\xff\x00\x81\x82")

            result = self.run_dispatch(source_path, out_md, out_meta)
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout.decode("utf-8"))
            meta = json.loads(out_meta.read_text(encoding="utf-8"))

            self.assertEqual(payload["error"]["code"], "UNSUPPORTED_INPUT")
            self.assertEqual(meta["error"]["code"], "UNSUPPORTED_INPUT")


if __name__ == "__main__":
    unittest.main()
