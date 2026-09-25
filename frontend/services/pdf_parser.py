"""PDF preview helpers and compatibility exports for the Streamlit frontend."""

import base64
import streamlit as st

from backend.app.services.pdf_extraction import (
    ExtractionResult,
    extract_resume_text,
    extract_text,
    normalize_resume_text,
    text_quality,
)

__all__ = [
    "ExtractionResult",
    "extract_resume_text",
    "extract_text",
    "normalize_resume_text",
    "render_pdf_preview",
    "text_quality",
]


def render_pdf_preview(pdf_bytes: bytes):
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    st.markdown(
        f"""
        <iframe
            src="data:application/pdf;base64,{encoded_pdf}"
            width="400"
            height="500"
            type="application/pdf"
            style="border-radius: 10px; border: 2px solid #1ed760;">
        </iframe>
        """,
        unsafe_allow_html=True,
    )
