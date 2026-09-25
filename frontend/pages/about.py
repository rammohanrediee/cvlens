"""About page."""

import streamlit as st

from ..components.styles import section_card


def render_about_page():
    st.markdown(
        section_card("About The Tool", "A modern resume review workflow with role matching and focused career guidance."),
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <p align='justify'>
            This application parses resume information, identifies skills, predicts likely role direction, scores structure quality,
            and supports job-description-aware matching for clearer role alignment.
        </p>
        <p align='justify'>
            <b>User:</b> Upload a resume, optionally paste a target job description, and review role fit, gaps, and recommendations.<br/><br/>
            <b>Feedback:</b> Share suggestions and usability notes.<br/><br/>
            <b>Admin:</b> Review anonymous aggregate product metrics and feedback.
        </p>
        """,
        unsafe_allow_html=True,
    )
