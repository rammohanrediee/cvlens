"""Bounded PDF text extraction shared by API clients."""

from __future__ import annotations

import io
import re
import threading
import unicodedata
from dataclasses import asdict, dataclass

import pymupdf
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTTextContainer

MAX_PDF_BYTES = 5 * 1024 * 1024
MAX_PDF_PAGES = 20
MAX_OCR_PAGES = 5
MAX_EXTRACTED_CHARACTERS = 200_000
MAX_PAGE_POINTS = 1440
OCR_CONCURRENCY_LIMIT = 2
DOCUMENT_EXTRACTION_CONCURRENCY_LIMIT = 2
EXTRACTION_SLOT_TIMEOUT_SECONDS = 30
_OCR_SEMAPHORE = threading.BoundedSemaphore(OCR_CONCURRENCY_LIMIT)
_DOCUMENT_EXTRACTION_SEMAPHORE = threading.BoundedSemaphore(DOCUMENT_EXTRACTION_CONCURRENCY_LIMIT)


class PDFExtractionError(ValueError):
    """A safe, client-facing document validation or extraction error."""

    def __init__(self, code: str, message: str, status_code: int = 422):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True)
class ExtractionResult:
    text: str
    method: str
    page_count: int
    ocr_pages: tuple[int, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["ocr_pages"] = list(self.ocr_pages)
        payload["warnings"] = list(self.warnings)
        return payload


_LIGATURES = str.maketrans(
    {
        "\ufb00": "ff",
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\ufb03": "ffi",
        "\ufb04": "ffl",
        "\ufb05": "st",
        "\ufb06": "st",
    }
)


def normalize_resume_text(text: str) -> str:
    """Clean extraction artifacts without rewriting resume content."""
    normalized = unicodedata.normalize("NFKC", text.translate(_LIGATURES))
    normalized = normalized.replace("\u00a0", " ").replace("\u200b", "")
    normalized = re.sub(r"(?<=\w)-\s*\n\s*(?=[a-z])", "", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r" *\n *", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def text_quality(text: str) -> float:
    """Return a conservative 0..1 signal for whether a page is usable."""
    cleaned = normalize_resume_text(text)
    if not cleaned:
        return 0.0

    visible = [character for character in cleaned if not character.isspace()]
    if not visible:
        return 0.0

    word_count = len(re.findall(r"\b[\w.+#/-]{2,}\b", cleaned))
    readable = sum(character.isalnum() or character in ".,:;@+/#&()[]-'\"" for character in visible)
    replacement_penalty = cleaned.count("\ufffd") / len(visible)
    length_score = min(len(visible) / 120, 1.0)
    word_score = min(word_count / 20, 1.0)
    character_score = readable / len(visible)
    return max(0.0, min(1.0, 0.35 * length_score + 0.35 * word_score + 0.30 * character_score - replacement_penalty))


def _inspect_pdf(pdf_bytes: bytes) -> int:
    if not pdf_bytes or len(pdf_bytes) > MAX_PDF_BYTES:
        raise PDFExtractionError(
            "document_too_large",
            f"Resume PDF must not exceed {MAX_PDF_BYTES // (1024 * 1024)} MiB.",
            413,
        )
    if b"%PDF" not in pdf_bytes[:1024]:
        raise PDFExtractionError("invalid_pdf", "The uploaded file is not a valid PDF.")
    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
            if document.needs_pass:
                raise PDFExtractionError("encrypted_pdf", "Password-protected PDFs are not supported.")
            page_count = document.page_count
            if page_count < 1:
                raise PDFExtractionError("empty_pdf", "The PDF does not contain any pages.")
            if page_count > MAX_PDF_PAGES:
                raise PDFExtractionError(
                    "too_many_pages",
                    f"Resume PDF must not exceed {MAX_PDF_PAGES} pages.",
                )
            for page in document:
                if page.rect.width > MAX_PAGE_POINTS or page.rect.height > MAX_PAGE_POINTS:
                    raise PDFExtractionError(
                        "document_too_complex",
                        "The PDF page dimensions are too large to process safely.",
                    )
    except PDFExtractionError:
        raise
    except Exception as error:
        raise PDFExtractionError("invalid_pdf", "The uploaded PDF could not be opened.") from error
    return page_count


def _extract_native_pages(pdf_bytes: bytes) -> list[str]:
    pages: list[str] = []
    extracted_characters = 0
    layout_parameters = LAParams(boxes_flow=0.5, all_texts=True)
    try:
        for page in extract_pages(io.BytesIO(pdf_bytes), laparams=layout_parameters, maxpages=MAX_PDF_PAGES):
            containers = [element for element in page if isinstance(element, LTTextContainer)]
            page_width = page.bbox[2] - page.bbox[0]
            midpoint = page.bbox[0] + (page_width / 2)
            left_column = [element for element in containers if element.bbox[0] < midpoint]
            right_column = [element for element in containers if element.bbox[0] >= midpoint]
            right_column_anchors = [
                element for element in right_column if element.bbox[0] <= page.bbox[0] + (page_width * 0.75)
            ]
            if len(left_column) >= 2 and len(right_column_anchors) >= 2:
                containers = [
                    *sorted(left_column, key=lambda element: (-element.bbox[3], element.bbox[0])),
                    *sorted(right_column, key=lambda element: (-element.bbox[3], element.bbox[0])),
                ]
            else:
                containers = sorted(containers, key=lambda element: (-element.bbox[3], element.bbox[0]))
            page_text = "\n".join(element.get_text().strip() for element in containers if element.get_text().strip())
            normalized_page = normalize_resume_text(page_text)
            extracted_characters += len(normalized_page)
            if extracted_characters > MAX_EXTRACTED_CHARACTERS:
                raise PDFExtractionError("document_too_complex", "The extracted resume text is too large to process.")
            pages.append(normalized_page)
    except PDFExtractionError:
        raise
    except Exception as error:
        raise PDFExtractionError("pdf_extraction_failed", "The PDF text layer could not be read.") from error
    return pages


def _ocr_page(pdf_bytes: bytes, page_index: int) -> str:
    acquired = _OCR_SEMAPHORE.acquire(timeout=EXTRACTION_SLOT_TIMEOUT_SECONDS)
    if not acquired:
        raise RuntimeError("OCR capacity unavailable")
    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
            page = document[page_index]
            text_page = page.get_textpage_ocr(language="eng", dpi=300, full=True)
            return normalize_resume_text(page.get_text(textpage=text_page, sort=True))
    except Exception as error:
        raise RuntimeError("OCR unavailable") from error
    finally:
        _OCR_SEMAPHORE.release()


def _extract_resume_text(pdf_bytes: bytes, quality_threshold: float) -> ExtractionResult:
    """Extract native text and OCR only a bounded number of weak pages."""
    expected_pages = _inspect_pdf(pdf_bytes)
    native_pages = _extract_native_pages(pdf_bytes)
    if not native_pages or len(native_pages) != expected_pages:
        raise PDFExtractionError("pdf_extraction_failed", "The PDF pages could not be read reliably.")

    final_pages: list[str] = []
    ocr_pages: list[int] = []
    warnings: list[str] = []
    ocr_attempts = 0

    for page_index, native_text in enumerate(native_pages):
        if text_quality(native_text) >= quality_threshold:
            final_pages.append(native_text)
            continue

        if ocr_attempts >= MAX_OCR_PAGES:
            final_pages.append(native_text)
            warnings.append(f"Page {page_index + 1}: OCR skipped because the document OCR limit was reached.")
            continue

        ocr_attempts += 1
        try:
            ocr_text = _ocr_page(pdf_bytes, page_index)
        except RuntimeError:
            warnings.append(f"Page {page_index + 1}: OCR unavailable.")
            final_pages.append(native_text)
            continue

        if text_quality(ocr_text) > text_quality(native_text):
            final_pages.append(ocr_text)
            ocr_pages.append(page_index + 1)
        else:
            final_pages.append(native_text)
            warnings.append(f"Page {page_index + 1}: OCR did not improve the extracted text.")

    combined_text = normalize_resume_text("\n\n".join(page for page in final_pages if page))
    if len(combined_text) > MAX_EXTRACTED_CHARACTERS:
        raise PDFExtractionError("document_too_complex", "The extracted resume text is too large to process.")
    if text_quality(combined_text) < 0.20:
        raise PDFExtractionError("no_readable_text", "No usable resume text could be extracted from the PDF.")

    if len(ocr_pages) == len(native_pages):
        method = "ocr"
    elif ocr_pages:
        method = "hybrid"
    else:
        method = "native"

    return ExtractionResult(
        text=combined_text,
        method=method,
        page_count=len(native_pages),
        ocr_pages=tuple(ocr_pages),
        warnings=tuple(warnings),
    )


def extract_resume_text(pdf_bytes: bytes, quality_threshold: float = 0.48) -> ExtractionResult:
    """Bound concurrent document extraction and reject excess work promptly."""
    acquired = _DOCUMENT_EXTRACTION_SEMAPHORE.acquire(timeout=EXTRACTION_SLOT_TIMEOUT_SECONDS)
    if not acquired:
        raise PDFExtractionError(
            "service_busy",
            "Resume extraction is temporarily busy. Try again shortly.",
            503,
        )
    try:
        return _extract_resume_text(pdf_bytes, quality_threshold)
    finally:
        _DOCUMENT_EXTRACTION_SEMAPHORE.release()


def extract_text(pdf_bytes: bytes) -> str:
    """Backward-compatible text-only interface."""
    return extract_resume_text(pdf_bytes).text
