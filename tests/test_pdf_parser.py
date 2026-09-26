import unittest
import io
import shutil
from unittest.mock import patch

import pymupdf
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from backend.app.services.pdf_extraction import (
    MAX_PDF_BYTES,
    PDFExtractionError,
    _inspect_pdf,
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

    def test_rejects_extreme_page_geometry_before_ocr(self):
        document = pymupdf.open()
        document.new_page(width=2000, height=792)
        pdf_bytes = document.tobytes()
        document.close()

        with self.assertRaisesRegex(PDFExtractionError, "page dimensions"):
            extract_resume_text(pdf_bytes)

    def test_rejects_page_count_before_traversing_page_objects(self):
        class TooLongDocument:
            needs_pass = False
            page_count = 21

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def __iter__(self):
                raise AssertionError("pages must not be traversed after the count limit is exceeded")

        with patch("backend.app.services.pdf_extraction.pymupdf.open", return_value=TooLongDocument()):
            with self.assertRaisesRegex(PDFExtractionError, "must not exceed 20 pages"):
                _inspect_pdf(b"%PDF-too-many-pages")

    def test_rejects_when_document_extraction_capacity_is_exhausted(self):
        class BusySemaphore:
            def acquire(self, timeout=None):
                return False

            def release(self):
                raise AssertionError("an unacquired slot must not be released")

        with patch("backend.app.services.pdf_extraction._DOCUMENT_EXTRACTION_SEMAPHORE", BusySemaphore()):
            with self.assertRaisesRegex(PDFExtractionError, "temporarily busy") as raised:
                extract_resume_text(b"%PDF-busy")

        self.assertEqual(raised.exception.code, "service_busy")
        self.assertEqual(raised.exception.status_code, 503)

    def test_preserves_column_reading_order_for_two_column_resumes(self):
        pdf_buffer = io.BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        pdf.drawString(40, 760, "EXPERIENCE")
        pdf.drawString(40, 735, "Built Python APIs for 500 users.")
        pdf.drawString(40, 680, "EDUCATION")
        pdf.drawString(40, 655, "Bachelor of Technology 2024")
        pdf.drawString(330, 760, "SKILLS")
        pdf.drawString(330, 735, "Python SQL Docker FastAPI")
        pdf.drawString(330, 680, "PROJECTS")
        pdf.drawString(330, 655, "Resume Analyzer Platform")
        pdf.save()

        text = extract_resume_text(pdf_buffer.getvalue()).text

        self.assertLess(text.index("EXPERIENCE"), text.index("EDUCATION"))
        self.assertLess(text.index("EDUCATION"), text.index("SKILLS"))
        self.assertLess(text.index("SKILLS"), text.index("PROJECTS"))

    def test_right_aligned_dates_do_not_trigger_two_column_reordering(self):
        pdf_buffer = io.BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        pdf.drawString(40, 760, "EXPERIENCE")
        pdf.drawString(500, 760, "2024-2025")
        pdf.drawString(40, 735, "Built Python APIs for enterprise customers.")
        pdf.drawString(40, 680, "EDUCATION")
        pdf.drawString(500, 680, "2020-2024")
        pdf.drawString(40, 655, "Bachelor of Technology in Computer Science")
        pdf.save()

        text = extract_resume_text(pdf_buffer.getvalue()).text

        self.assertLess(text.index("2024-2025"), text.index("Built Python"))
        self.assertLess(text.index("Built Python"), text.index("EDUCATION"))

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
