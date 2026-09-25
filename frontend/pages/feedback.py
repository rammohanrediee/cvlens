"""Feedback page."""

import plotly.graph_objects as go
import streamlit as st

from ..components.admin_dashboard import apply_chart_theme, get_chart_theme_settings
from ..components.styles import section_card


def build_rating_chart(feedback_df, theme_mode):
    chart_theme = get_chart_theme_settings(theme_mode)
    ratings = feedback_df["Feedback Score"].value_counts().sort_index()
    labels = [f"{rating} star" for rating in ratings.index]
    figure = go.Figure(
        go.Pie(
            labels=labels,
            values=ratings.values,
            hole=0.58,
            marker=dict(
                colors=["#5ba4d9", "#45b979", "#8fb8dd", "#2f9e62", "#1769aa"],
                line=dict(color=chart_theme["bar_line"], width=2),
            ),
            textinfo="percent",
            textfont=dict(color=chart_theme["font_color"], size=15),
            hovertemplate="%{label}: %{value} response(s)<extra></extra>",
        )
    )
    figure.update_layout(
        title="User Rating Mix",
        height=360,
        margin=dict(l=20, r=20, t=58, b=20),
        legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center"),
        annotations=[
            dict(
                text=f"{int(ratings.sum())}<br>reviews",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=18, color=chart_theme["font_color"]),
            )
        ],
    )
    return apply_chart_theme(figure, theme_mode)


def render_feedback_page(database, theme_mode: str):
    st.markdown(section_card("Feedback", "Share what worked, what felt unclear, and what you want next."), unsafe_allow_html=True)
    with st.form("feedback_form"):
        score = st.slider("Rate Us From 1 - 5", 1, 5)
        comments = st.text_input("Comments")
        submitted = st.form_submit_button("Submit")
        if submitted:
            try:
                database.save_feedback(score=score, comments=comments)
                st.success("Thanks. Your anonymous feedback was recorded.")
            except Exception as error:
                st.warning(f"Feedback was received, but storing it failed. Details: {error}")

    feedback_df = database.load_feedback()
    st.subheader("Past User Ratings")
    if feedback_df.empty:
        st.info("No feedback has been recorded yet.")
    else:
        st.plotly_chart(build_rating_chart(feedback_df, theme_mode), width="stretch")
