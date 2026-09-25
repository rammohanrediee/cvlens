import unittest
import io
import shutil
from unittest.mock import patch

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from backend.app.services.pdf_extraction import (
    MAX_PDF_BYTES,
    PDFExtractionError,
    extract_resume_text,
    extract_text,
    normalize_resume_text,
    text_quality,
)


class PDFParserTests(unittest.TestCase):
    def test_normalizes_ligatures_spacing_and_line_wrap_hyphens(self):
        raw = "Pro\ufb01le  \nMachine learn-\ning\n\n\nPython\u00a0 SQL"
        self.assertEqual(normalize_resume_text(raw), "Profile\nMachine learning\n\nPython SQL")

    def test_quality_rejects_empty_or_garbled_text(self):
        self.assertEqual(text_quality(""), 0.0)
        self.assertLess(text_quality("\ufffd \ufffd \ufffd"), 0.20)
        self.assertGreater(
            text_quality(
                "Ramu Reddy\nAI Engineer\nPython FastAPI SQL\n"
                "Built and tested a resume analysis service with measurable results."
            ),
            0.48,
        )

    @patch("backend.app.services.pdf_extraction._inspect_pdf", return_value=1)
    @patch("backend.app.services.pdf_extraction._extract_native_pages")
    @patch("backend.app.services.pdf_extraction._ocr_page")
    def test_keeps_good_native_text_without_running_ocr(self, ocr_page, native_pages, _inspect_pdf):
        native_text = (
            "Ramu Reddy\nAI Engineer\nPython FastAPI SQL PostgreSQL\n"
            "Built reliable API services and tested resume parsing workflows."
        )
        native_pages.return_value = [native_text]

        result = extract_resume_text(b"%PDF-native")

        self.assertEqual(result.method, "native")
        self.assertEqual(result.ocr_pages, ())
        self.assertEqual(result.text, native_text)
        ocr_page.assert_not_called()

    @patch("backend.app.services.pdf_extraction._inspect_pdf", return_value=2)
    @patch("backend.app.services.pdf_extraction._extract_native_pages")
    @patch("backend.app.services.pdf_extraction._ocr_page")
    def test_uses_ocr_for_a_weak_page_and_preserves_page_order(self, ocr_page, native_pages, _inspect_pdf):
        native_pages.return_value = [
            "Ramu Reddy\nAI Engineer\nPython FastAPI SQL PostgreSQL\n"
            "Built reliable API services and tested resume parsing workflows.",
            "",
        ]
        ocr_page.return_value = (
            "PROJECTS\nResume Analyzer\nExtracted resume text and mapped job requirements to supporting evidence."
        )

        result = extract_resume_text(b"%PDF-scanned")

        self.assertEqual(result.method, "hybrid")
        self.assertEqual(result.ocr_pages, (2,))
        self.assertLess(result.text.index("AI Engineer"), result.text.index("PROJECTS"))

    @patch("backend.app.services.pdf_extraction._inspect_pdf", return_value=1)
    @patch("backend.app.services.pdf_extraction._extract_native_pages")
    @patch("backend.app.services.pdf_extraction._ocr_page")
    def test_reports_missing_ocr_when_weak_text_cannot_be_recovered(self, ocr_page, native_pages, _inspect_pdf):
        native_pages.return_value = [""]
        ocr_page.side_effect = RuntimeError("Tesseract is not installed")

        with self.assertRaisesRegex(PDFExtractionError, "No usable resume text"):
            extract_resume_text(b"%PDF-scanned")

    @patch("backend.app.services.pdf_extraction.extract_resume_text")
    def test_text_only_interface_remains_compatible(self, extract_result):
        extract_result.return_value.text = "Resume content"
        self.assertEqual(extract_text(b"%PDF-file"), "Resume content")

    def test_rejects_invalid_and_oversized_documents_before_extraction(self):
        with self.assertRaisesRegex(PDFExtractionError, "valid PDF"):
            extract_resume_text(b"not-a-pdf")
        with self.assertRaisesRegex(PDFExtractionError, "must not exceed"):
            extract_resume_text(b"%PDF" + b"x" * MAX_PDF_BYTES)

    @unittest.skipUnless(shutil.which("tesseract"), "Tesseract is required for OCR integration")
    def test_extracts_a_real_image_only_pdf_with_tesseract(self):
        image = Image.new("RGB", (1700, 2200), "white")
        draw = ImageDraw.Draw(image)
        font = None
        for font_path in (
            "Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ):
            try:
                font = ImageFont.truetype(font_path, 52)
                break
            except OSError:
                continue
        if font is None:
            self.skipTest("No suitable TrueType font is available for the OCR fixture")
        draw.multiline_text(
            (120, 150),
            "RAMU REDDY\nAI ENGINEER\nPython FastAPI SQL\nResume Analyzer",
            fill="black",
            font=font,
            spacing=24,
        )

        image_buffer = io.BytesIO()
        image.save(image_buffer, format="PNG")
        pdf_buffer = io.BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        pdf.drawInlineImage(
            Image.open(io.BytesIO(image_buffer.getvalue())),
            0,
            0,
            width=letter[0],
            height=letter[1],
        )
        pdf.save()

        result = extract_resume_text(pdf_buffer.getvalue())
        self.assertEqual(result.method, "ocr")
        self.assertIn("Python", result.text)
        self.assertIn("FastAPI", result.text)


if __name__ == "__main__":
    unittest.main()
