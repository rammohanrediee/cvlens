"""Streamlit user interface entry point."""

import streamlit as st

from .api_client import ResumeAnalyzerClient
from .components.navigation import render_navigation, render_theme_picker
from .components.styles import render_app_styles
from .pages.about import render_about_page
from .pages.admin import render_admin_page
from .pages.candidate import render_candidate_page
from .pages.feedback import render_feedback_page
from .pages.home import render_home_page
from .pages.results import render_results_page
from .services.storage import get_database


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _initialize_session():
    st.session_state.setdefault("theme_mode", "System")
    st.session_state.setdefault("theme_selector", "Auto")
    st.session_state.setdefault("nav_choice", "Home")


def run():
    _initialize_session()
    st.markdown(render_app_styles(st.session_state.theme_mode), unsafe_allow_html=True)
    choice = render_navigation()
    render_theme_picker()

    database = get_database()
    if database.status_message:
        st.info(database.status_message)

    client = ResumeAnalyzerClient()
    api_connected = client.is_available()
    status_class = "connected" if api_connected else "offline"
    status_label = "Analysis API connected" if api_connected else "Analysis API offline"
    st.markdown(
        f"<div class='connection-status {status_class}'><span></span>{status_label}</div>",
        unsafe_allow_html=True,
    )
    if not api_connected:
        st.caption("Start the backend with `python -m backend.app.main`, then refresh this page.")

    if choice == "Home":
        render_home_page(api_connected)
    elif choice == "Analyze":
        render_candidate_page(database, client)
    elif choice == "Results":
        render_results_page(client)
    elif choice == "Feedback":
        render_feedback_page(database, st.session_state.theme_mode)
    elif choice == "About":
        render_about_page()
    elif choice == "Admin":
        render_admin_page(database, st.session_state.theme_mode)


if __name__ == "__main__":
    run()
