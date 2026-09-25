"""Candidate upload and analysis page."""

import streamlit as st

from ..api_client import BackendAPIError, ResumeAnalyzerClient
from ..components.report import recommended_courses_for
from ..components.styles import section_card
from ..services.storage import build_analysis_event


def _validate_upload(pdf_file) -> bool:
    if pdf_file is None:
        st.warning("Please upload a PDF resume first.")
        return False
    return True


def render_candidate_page(database, client: ResumeAnalyzerClient):
    st.markdown(
        section_card("Start your review", "Add your details, the target job description, and a PDF resume."),
        unsafe_allow_html=True,
    )

    with st.form("resume_analysis_form"):
        name = st.text_input("Name override (optional)")
        job_description = st.text_area(
            "Target Job Description",
            height=130,
            placeholder="Paste the job description here. The analysis will compare its requirements with evidence in your resume.",
        )
        pdf_file = st.file_uploader("Upload resume", type=["pdf"])
        submitted = st.form_submit_button("Analyze resume", width="stretch")

    if submitted:
        if not _validate_upload(pdf_file):
            return

        pdf_content = pdf_file.getvalue()
        with st.spinner("Reading your resume and comparing it with the role..."):
            try:
                extraction = client.extract_document(filename=pdf_file.name, pdf_bytes=pdf_content)
                api_payload = {
                    "candidate_name": name,
                    "resume_text": extraction["text"],
                    "resume_skills": [],
                    "job_description": job_description,
                    "page_count": extraction["page_count"],
                }
                analysis = client.analyze(**api_payload)
            except BackendAPIError as error:
                st.error(str(error))
                return
            except Exception as error:
                st.error(f"Resume parsing failed. Details: {error}")
                return

        recommended_courses = recommended_courses_for(analysis)
        try:
            database.save_analysis(
                build_analysis_event(
                    analysis=analysis,
                    recommended_courses=recommended_courses,
                )
            )
        except Exception as error:
            st.warning(f"Analysis finished, but the session record could not be stored. Details: {error}")

        st.session_state.latest_analysis = {
            "analysis": analysis,
            "pdf_name": pdf_file.name,
            "pdf_content": pdf_content,
            "api_payload": api_payload,
            "extraction": {
                "method": extraction["method"],
                "page_count": extraction["page_count"],
                "ocr_pages": extraction["ocr_pages"],
                "warnings": extraction["warnings"],
            },
        }
        st.session_state.nav_choice = "Results"
        if extraction["warnings"]:
            extraction_note = "with an extraction warning: " + " ".join(extraction["warnings"])
        elif extraction["method"] == "native":
            extraction_note = "using the PDF text layer"
        else:
            pages = ", ".join(str(page) for page in extraction["ocr_pages"])
            extraction_note = f"using OCR on page(s) {pages}"
        st.session_state.analysis_notice = f"Analysis complete {extraction_note}."
        st.rerun()
