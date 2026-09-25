"""Home page for the resume analyzer."""

import streamlit as st

from ..components.styles import hero_section, section_card


def render_home_page(api_connected: bool):
    st.markdown(hero_section(), unsafe_allow_html=True)

    if st.button("Start analysis", type="primary", width="stretch"):
        st.session_state.nav_choice = "Analyze"
        st.rerun()

    first, second, third = st.columns(3)
    with first:
        st.markdown(section_card("1. Add the role", "Paste the job description you are applying to."), unsafe_allow_html=True)
    with second:
        st.markdown(section_card("2. Upload the resume", "Use the PDF version you plan to send."), unsafe_allow_html=True)
    with third:
        st.markdown(section_card("3. Review evidence", "Open Results for scores, gaps, and supporting details."), unsafe_allow_html=True)

    if not api_connected:
        st.info("The interface is ready. Start the analysis API before uploading a resume.")
