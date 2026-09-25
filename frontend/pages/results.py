"""Completed analysis results page."""

import streamlit as st

from ..components.report import render_analysis_report
from ..components.styles import section_card


def render_results_page(client):
    notice = st.session_state.pop("analysis_notice", None)
    if notice:
        st.success(notice)

    result = st.session_state.get("latest_analysis")
    if not result:
        st.markdown(
            section_card("No analysis yet", "Open Analyze resume, upload a PDF, and submit it to create a report."),
            unsafe_allow_html=True,
        )
        return

    render_analysis_report(
        analysis=result["analysis"],
        pdf_name=result["pdf_name"],
        pdf_content=result["pdf_content"],
        api_payload=result["api_payload"],
        client=client,
    )
