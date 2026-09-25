"""Admin dashboard charts and tables."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .styles import info_card, section_card


def get_chart_theme_settings(theme_mode):
    is_dark = theme_mode == "Dark"
    return {
        "template": "plotly_dark" if is_dark else "plotly_white",
        "font_color": "#e5eef8" if is_dark else "#1f2933",
        "grid_color": "rgba(203, 213, 225, 0.16)" if is_dark else "rgba(31, 41, 51, 0.12)",
        "paper_bg": "rgba(9,17,26,0)" if is_dark else "rgba(255,255,255,0)",
        "plot_bg": "rgba(9,17,26,0)" if is_dark else "rgba(255,255,255,0)",
        "bar_line": "rgba(255,255,255,0.12)" if is_dark else "rgba(31,41,51,0.18)",
    }


def apply_chart_theme(figure, theme_mode):
    chart_theme = get_chart_theme_settings(theme_mode)
    figure.update_layout(
        template=chart_theme["template"],
        paper_bgcolor=chart_theme["paper_bg"],
        plot_bgcolor=chart_theme["plot_bg"],
        font=dict(color=chart_theme["font_color"]),
        title_font=dict(color=chart_theme["font_color"], size=18),
        legend=dict(font=dict(color=chart_theme["font_color"])),
    )
    figure.update_xaxes(showgrid=True, gridcolor=chart_theme["grid_color"], zeroline=False, color=chart_theme["font_color"])
    figure.update_yaxes(showgrid=False, zeroline=False, color=chart_theme["font_color"])
    return figure


def build_ranked_bar_chart(dataframe, column_name, title, color_scale, theme_mode, limit=6):
    chart_theme = get_chart_theme_settings(theme_mode)
    series = (
        dataframe[column_name]
        .fillna("Unknown")
        .astype(str)
        .replace("", "Unknown")
        .value_counts()
        .head(limit)
        .sort_values(ascending=True)
    )
    figure = go.Figure(
        go.Bar(
            x=series.values,
            y=series.index,
            orientation="h",
            marker=dict(color=series.values, colorscale=color_scale, line=dict(color=chart_theme["bar_line"], width=1)),
            text=series.values,
            textposition="outside",
            textfont=dict(color=chart_theme["font_color"]),
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    )
    figure.update_layout(title=title, height=320, margin=dict(l=10, r=20, t=56, b=10), xaxis_title="Count", yaxis_title="")
    return apply_chart_theme(figure, theme_mode)


def build_score_distribution_chart(dataframe, theme_mode):
    scores = pd.to_numeric(dataframe["resume_score"], errors="coerce").dropna()
    if scores.empty:
        scores = pd.Series([0], dtype=float)
    figure = go.Figure(
        go.Histogram(
            x=scores,
            nbinsx=10,
            marker=dict(color="rgba(15, 118, 110, 0.78)", line=dict(color="rgba(15, 118, 110, 1)", width=1)),
            hovertemplate="Score %{x}<br>Count %{y}<extra></extra>",
        )
    )
    figure.update_layout(title="Resume Score Distribution", height=320, margin=dict(l=10, r=20, t=56, b=10), xaxis_title="Resume score", yaxis_title="Profiles", bargap=0.08)
    return apply_chart_theme(figure, theme_mode)


def build_feedback_mix_chart(feedback_df, theme_mode):
    chart_theme = get_chart_theme_settings(theme_mode)
    ratings = pd.to_numeric(feedback_df["Feedback Score"], errors="coerce").dropna()
    if ratings.empty:
        ratings = pd.Series([0], dtype=float)
    counts = ratings.astype(int).value_counts().sort_index()
    figure = go.Figure(
        go.Scatterpolar(
            r=counts.values.tolist(),
            theta=[f"{index} Star" for index in counts.index.tolist()],
            fill="toself",
            line=dict(color="rgba(217, 119, 6, 0.9)", width=3),
            marker=dict(size=8, color="rgba(217, 119, 6, 0.9)"),
            hovertemplate="%{theta}: %{r}<extra></extra>",
        )
    )
    figure.update_layout(
        title="Feedback Rating Mix",
        height=320,
        margin=dict(l=20, r=20, t=56, b=20),
        polar=dict(
            bgcolor=chart_theme["plot_bg"],
            radialaxis=dict(visible=True, showline=False, gridcolor=chart_theme["grid_color"], color=chart_theme["font_color"]),
            angularaxis=dict(color=chart_theme["font_color"]),
        ),
    )
    return apply_chart_theme(figure, theme_mode)


def build_level_mix_chart(dataframe, theme_mode):
    chart_theme = get_chart_theme_settings(theme_mode)
    series = dataframe["User_Level"].fillna("Unknown").astype(str).replace("", "Unknown").value_counts()
    figure = go.Figure(
        go.Pie(
            labels=series.index,
            values=series.values,
            hole=0.62,
            marker=dict(colors=["#0f766e", "#d97706", "#1f2933", "#94a3b8"]),
            textinfo="label+percent",
            textfont=dict(color=chart_theme["font_color"]),
            hovertemplate="%{label}: %{value}<extra></extra>",
        )
    )
    figure.update_layout(title="Candidate Seniority Mix", height=320, margin=dict(l=20, r=20, t=56, b=20), showlegend=False)
    return apply_chart_theme(figure, theme_mode)


def render_admin_console(plot_data, events_df, feedback_df, theme_mode):
    plot_data = plot_data.copy()
    plot_data["resume_score_num"] = pd.to_numeric(plot_data["resume_score"], errors="coerce")
    total_profiles = int(len(plot_data))
    average_score = float(plot_data["resume_score_num"].dropna().mean()) if total_profiles else 0.0
    top_track = plot_data["Predicted_Field"].fillna("Unknown").astype(str).value_counts().idxmax() if total_profiles else "No data"
    total_feedback = int(len(feedback_df))
    average_rating = float(pd.to_numeric(feedback_df["Feedback Score"], errors="coerce").dropna().mean()) if total_feedback else 0.0

    st.markdown(section_card("Admin Console", "Anonymous product analytics for score quality, role signals, and feedback."), unsafe_allow_html=True)
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.markdown(info_card("Profiles Reviewed", f"{total_profiles}", "Total resumes processed in the system.", "teal"), unsafe_allow_html=True)
    with metric_col2:
        st.markdown(info_card("Average Score", f"{average_score:.1f}", "Mean resume quality score across all uploads.", "warm"), unsafe_allow_html=True)
    with metric_col3:
        st.markdown(info_card("Top Talent Track", top_track, "Most frequently predicted role family.", "ink"), unsafe_allow_html=True)
    with metric_col4:
        st.markdown(info_card("Feedback Pulse", f"{average_rating:.1f}/5", "Average feedback rating from submitted reviews.", "teal"), unsafe_allow_html=True)

    dashboard_tabs = st.tabs(["Overview", "Talent Signals", "Feedback", "Data Tables"])
    with dashboard_tabs[0]:
        overview_col1, overview_col2 = st.columns(2)
        with overview_col1:
            st.plotly_chart(build_ranked_bar_chart(plot_data, "Predicted_Field", "Top Predicted Role Tracks", "Tealgrn", theme_mode), width="stretch")
        with overview_col2:
            st.plotly_chart(build_score_distribution_chart(plot_data, theme_mode), width="stretch")

    with dashboard_tabs[1]:
        st.plotly_chart(build_level_mix_chart(plot_data, theme_mode), width="stretch")
    with dashboard_tabs[2]:
        st.plotly_chart(build_feedback_mix_chart(feedback_df, theme_mode), width="stretch")

        st.markdown(section_card("Feedback stream", "Latest comments collected from users."), unsafe_allow_html=True)
        if feedback_df.empty:
            st.info("No feedback has been recorded yet.")
        else:
            recent_feedback = feedback_df.sort_values("Timestamp", ascending=False).head(8)
            st.dataframe(recent_feedback[["Feedback Score", "Comments", "Timestamp"]], width="stretch")

    with dashboard_tabs[3]:
        data_tab1, data_tab2 = st.tabs(["Anonymous Analysis Events", "Feedback Records"])
        with data_tab1:
            st.markdown(section_card("Analysis events", "Aggregate product metrics without resume content or personal identifiers."), unsafe_allow_html=True)
            st.dataframe(events_df, width="stretch", height=380)
            st.download_button("Download Analysis Events", data=events_df.to_csv(index=False), file_name="analysis_events.csv", mime="text/csv")
        with data_tab2:
            st.markdown(section_card("Feedback records", "All submitted ratings and comments in one table."), unsafe_allow_html=True)
            st.dataframe(feedback_df, width="stretch", height=320)
