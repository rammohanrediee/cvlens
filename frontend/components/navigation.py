"""Navigation and shell controls for the Streamlit frontend."""

import streamlit as st


PRIMARY_NAV_OPTIONS = ["Analyze", "Results", "Feedback"]
SECONDARY_NAV_OPTIONS = ["Home", "About", "Admin"]
NAV_OPTIONS = PRIMARY_NAV_OPTIONS + SECONDARY_NAV_OPTIONS
NAV_LABELS = {
    "Home": "Home",
    "Analyze": "Analyze",
    "Results": "Results",
    "Feedback": "Feedback",
    "About": "About",
    "Admin": "Admin",
}
NAV_ICONS = {
    "Home": "00",
    "Analyze": "01",
    "Results": "02",
    "Feedback": "03",
    "About": "04",
    "Admin": "05",
}

def render_theme_picker():
    def _on_theme_change():
        st.session_state.theme_mode = {
            "Auto": "System",
            "Light": "Light",
            "Dark": "Dark",
        }[st.session_state.theme_selector]

    st.sidebar.selectbox(
        "Theme",
        ["Auto", "Light", "Dark"],
        key="theme_selector",
        on_change=_on_theme_change,
    )


def render_navigation() -> str:
    def _set_nav(target):
        st.session_state.nav_choice = target

    def _format_nav(key):
        return f"{NAV_ICONS[key]}  {NAV_LABELS[key]}"

    st.sidebar.markdown(
        """
        <div class='nav-stage'>
            <div class='nav-mark'>AI</div>
            <div class='nav-title'>AI Resume Analyzer</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("<div class='nav-group-label'>Workflow</div>", unsafe_allow_html=True)
    for nav_key in PRIMARY_NAV_OPTIONS:
        st.sidebar.button(
            _format_nav(nav_key),
            key=f"nav_{nav_key.lower()}",
            width="stretch",
            on_click=_set_nav,
            args=(nav_key,),
        )

    st.sidebar.markdown("<div class='nav-group-label secondary'>Workspace</div>", unsafe_allow_html=True)
    for nav_key in SECONDARY_NAV_OPTIONS:
        st.sidebar.button(
            _format_nav(nav_key),
            key=f"nav_{nav_key.lower()}",
            width="stretch",
            on_click=_set_nav,
            args=(nav_key,),
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div class='nav-footnote'>
            <div class='nav-footnote-title'>Evidence first</div>
            <div class='nav-footnote-copy'>Resume fit, gaps, and next edits in one workflow.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.session_state.get("nav_choice", "Home")
