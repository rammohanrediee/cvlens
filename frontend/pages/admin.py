"""Admin analytics page."""

import time

import streamlit as st

from ..components.admin_dashboard import render_admin_console
from ..components.styles import section_card
from ..services.storage import parse_admin_credentials, verify_admin_password

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 60


def render_admin_page(database, theme_mode: str):
    credentials = parse_admin_credentials()
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    st.session_state.setdefault("admin_failed_attempts", 0)
    st.session_state.setdefault("admin_locked_until", 0.0)

    st.markdown(
        section_card("Admin Console v2", "A polished analytics workspace for role flow, score quality, and feedback intelligence."),
        unsafe_allow_html=True,
    )

    if not st.session_state.admin_authenticated:
        login_col1, login_col2 = st.columns([1.1, 0.9])
        with login_col1:
            st.markdown(section_card("Secure access", "Enter admin credentials to open the analytics workspace."), unsafe_allow_html=True)
            username = st.text_input("Username", key="admin_username")
            password = st.text_input("Password", type="password", key="admin_password")
            if not credentials:
                st.warning("Admin credentials are not configured. Add them in `.env` before using the console.")
            seconds_remaining = max(0, int(st.session_state.admin_locked_until - time.time()))
            if seconds_remaining:
                st.error(f"Too many failed attempts. Try again in {seconds_remaining} seconds.")
            if st.button("Open Admin Console", width="stretch", disabled=bool(seconds_remaining)):
                password_hash = credentials.get(username, "")
                if password_hash and verify_admin_password(password, password_hash):
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_username = username
                    st.session_state.admin_failed_attempts = 0
                    st.rerun()
                else:
                    st.session_state.admin_failed_attempts += 1
                    if st.session_state.admin_failed_attempts >= MAX_LOGIN_ATTEMPTS:
                        st.session_state.admin_locked_until = time.time() + LOCKOUT_SECONDS
                        st.session_state.admin_failed_attempts = 0
                    st.error("Invalid username or password.")
        with login_col2:
            st.markdown(
                """
                <section class="skill-panel">
                    <div class="skill-panel-title">Control room access</div>
                    <div class="skill-panel-subtitle">This workspace includes candidate records, regional signals, score distribution, and feedback monitoring.</div>
                    <div class="skill-chip-row">
                        <span class="skill-chip skill-chip-emerald">Role Trends</span>
                        <span class="skill-chip skill-chip-blue">Score Analytics</span>
                        <span class="skill-chip skill-chip-slate">Anonymous Metrics</span>
                        <span class="skill-chip skill-chip-emerald">Feedback Pulse</span>
                    </div>
                </section>
                """,
                unsafe_allow_html=True,
            )
        return

    admin_action_col1, admin_action_col2 = st.columns([1, 5])
    with admin_action_col1:
        if st.button("Logout", width="stretch"):
            st.session_state.admin_authenticated = False
            st.session_state.admin_username = None
            st.rerun()
    with admin_action_col2:
        active_admin = st.session_state.get("admin_username", "Admin")
        st.success(f"Welcome {active_admin}. The analytics workspace is ready.")

    plot_data, events_df, feedback_df = database.load_admin_frames()
    render_admin_console(plot_data, events_df, feedback_df, theme_mode)

    st.divider()
    with st.expander("Delete stored analytics"):
        st.warning("This permanently deletes anonymous analysis events and feedback.")
        confirmation = st.text_input("Type DELETE to confirm", key="delete_analytics_confirmation")
        if st.button("Delete analytics", disabled=confirmation != "DELETE"):
            database.clear_analytics()
            st.success("Stored analytics were deleted.")
            st.rerun()
