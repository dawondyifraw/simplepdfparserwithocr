import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pdfparser.parser import parse_pdfs


class _FakePage:
    def __init__(self, text, tables=None):
        self._text = text
        self._tables = tables or []

    def extract_text(self):
        return self._text

    def extract_tables(self):
        return self._tables


class _FakePdf:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeImage:
    def __init__(self):
        self.saved_path = None

    def save(self, path, format=None):
        self.saved_path = str(path)


class ParserTests(unittest.TestCase):
    def test_parse_pdfs_writes_csv_with_metadata_and_ocr(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            pdfs_dir = base / "pdfs"
            pdfs_dir.mkdir(parents=True)
            pdf_path = pdfs_dir / "sample.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\n%")

            pages = [_FakePage(""), _FakePage("hello")]
            fake_pdf = _FakePdf(pages)

            fake_image = _FakeImage()

            with patch("pdfparser.parser.pdfplumber.open", return_value=fake_pdf), patch(
                "pdfparser.parser.convert_from_path", return_value=[fake_image, fake_image]
            ), patch(
                "pdfparser.parser.pytesseract.image_to_string", return_value="ocr text"
            ):
                output = parse_pdfs(
                    pdfs_dir=pdfs_dir,
                    output_csv=base / "out.csv",
                    save_ocr_images=True,
                    ocr_images_dir=base / "ocr",
                )

            self.assertTrue(output.exists())
            content = output.read_text()
            self.assertIn("file_size_bytes", content)
            self.assertIn("ocr_used", content)
            self.assertIn("ocr_image_path", content)
            self.assertIn("ocr text", content)


if __name__ == "__main__":
    unittest.main()
