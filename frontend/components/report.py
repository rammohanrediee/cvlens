"""Reusable report rendering for the candidate analysis page."""

import html
import os
import random

import pandas as pd
import streamlit as st

from ..api_client import BackendAPIError
from ..services.pdf_parser import render_pdf_preview
from .courses import android_course, ds_course, interview_videos, ios_course, resume_videos, uiux_course, web_course
from .styles import info_card, section_card

COURSE_LIBRARY = {
    "data_science": ds_course,
    "web": web_course,
    "android": android_course,
    "ios": ios_course,
    "uiux": uiux_course,
}


def success_bullet(text):
    st.markdown(
        f"""
        <div style="padding: 12px 15px; margin: 8px 0; background: var(--surface-alt); border-left: 4px solid #2f7d5b; border-radius: 12px;">
            <span style="color: #2f7d5b; font-weight: 600;">✓</span>
            <span style="color: var(--ink); margin-left: 10px; font-weight: 600;">{html.escape(str(text))}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def warning_bullet(text):
    st.markdown(
        f"""
        <div style="padding: 12px 15px; margin: 8px 0; background: var(--surface-alt); border-left: 4px solid #b65f56; border-radius: 12px;">
            <span style="color: #b65f56; font-weight: 600;">○</span>
            <span style="color: var(--ink); margin-left: 10px; font-weight: 600;">{html.escape(str(text))}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_skill_panel(title, subtitle, items, tone="emerald"):
    chip_html = "".join(
        f"<span class='skill-chip skill-chip-{tone}'>{html.escape(str(item))}</span>"
        for item in items
    )
    st.markdown(
        f"""
        <section class="skill-panel">
            <div class="skill-panel-title">{html.escape(title)}</div>
            <div class="skill-panel-subtitle">{html.escape(subtitle)}</div>
            <div class="skill-chip-row">{chip_html or "<span class='skill-chip skill-chip-muted'>No items</span>"}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def recommended_courses_for(analysis: dict, limit: int = 5) -> list[str]:
    course_list = COURSE_LIBRARY.get(analysis["summary"]["courses_key"], ds_course)
    return [name for name, _ in course_list[:limit]]


def render_course_recommender(course_list):
    st.markdown(
        "<section class='course-panel'><div class='course-panel-title'>Recommended courses &amp; certifications</div><div class='course-panel-subtitle'>Practical resources for the skills this role asks for.</div></section>",
        unsafe_allow_html=True,
    )
    recommendation_count = st.slider("Choose Number of Course Recommendations:", 1, 10, 5)
    shuffled_courses = list(course_list)
    random.shuffle(shuffled_courses)
    selected = shuffled_courses[:recommendation_count]
    cards_html = "".join(
        f"<a class='course-card' href='{html.escape(link, quote=True)}' target='_blank' rel='noopener noreferrer'>"
        f"<span class='course-card-index'>{index:02d}</span>"
        f"<span class='course-card-body'><span class='course-card-title'>{html.escape(name)}</span>"
        f"<span class='course-card-meta'>Open course ↗</span></span></a>"
        for index, (name, link) in enumerate(selected, start=1)
    )
    st.markdown(f"<div class='course-grid'>{cards_html}</div>", unsafe_allow_html=True)
    return [name for name, _ in selected]


def render_section_scorecards(section_scores):
    for section in section_scores:
        st.markdown(
            section_card(
                section["category"],
                f"{section['matched_checks']} of {section['total_checks']} checks matched · {section['score']}/{section['max_score']} points",
            ),
            unsafe_allow_html=True,
        )
        st.progress(min(max(section["percent"] / 100, 0.0), 1.0))
        st.caption(f"Coverage score: {section['percent']}%")
        matched_labels = [item["label"] for item in section["checks"] if item["matched"]]
        missing_labels = [item["label"] for item in section["checks"] if not item["matched"]]
        if matched_labels:
            render_skill_panel("Already covered", "Strong signals already present in your resume.", matched_labels, tone="emerald")
        if missing_labels:
            render_skill_panel("Still missing", "Sections to strengthen in the next revision.", missing_labels, tone="blue")


def render_bullet_quality_panel(bullet_quality):
    st.markdown(section_card("Bullet quality checker", bullet_quality["summary"]), unsafe_allow_html=True)
    if not bullet_quality["flagged_bullets"]:
        st.success("No weak bullet patterns were detected in the parsed resume text.")
        return

    for finding in bullet_quality["flagged_bullets"]:
        issues = ", ".join(finding["issues"])
        st.markdown(
            f"""
            <div style="padding:1rem 1.1rem; border-radius:20px; background:var(--card-bg); border:1px solid var(--line); box-shadow:var(--shadow); margin:0 0 1rem 0;">
                <div style="font-size:0.82rem; text-transform:uppercase; letter-spacing:0.08em; color:var(--accent-3); font-weight:700;">Flagged Bullet</div>
                <div style="margin-top:0.55rem; font-size:1rem; font-weight:700; color:var(--ink);">{html.escape(finding['original'])}</div>
                <div style="margin-top:0.55rem; font-size:0.92rem; color:var(--muted);">Issues: {html.escape(issues)}</div>
                <div style="margin-top:0.75rem; font-size:0.9rem; color:var(--accent-2); font-weight:700;">Suggested rewrite</div>
                <div style="margin-top:0.3rem; font-size:0.95rem; color:var(--ink);">{html.escape(finding['suggestion'])}</div>
                <div style="margin-top:0.55rem; font-size:0.9rem; color:var(--muted);">{html.escape(finding['coaching_tip'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_gap_explainer_panel(gap_explainer):
    st.markdown(section_card("Resume-to-JD gap explainer", gap_explainer["summary"]), unsafe_allow_html=True)
    categorized = gap_explainer["categorized_missing_keywords"]
    if not categorized:
        st.success("No major gap categories were detected from the JD.")
        return

    gap_cols = st.columns(2)
    for index, (category, items) in enumerate(categorized.items()):
        with gap_cols[index % 2]:
            render_skill_panel(category, "Keywords from the JD that are not yet clearly proven in the resume.", items, tone="slate" if category in {"Domain", "Evidence"} else "emerald")


def render_requirement_evidence_panel(requirement_evidence):
    st.markdown(
        section_card("JD requirement evidence", requirement_evidence["summary"]),
        unsafe_allow_html=True,
    )
    requirements = requirement_evidence["requirements"]
    if not requirements:
        st.info("Add a target JD to map its requirements to exact resume evidence.")
        return

    st.progress(min(max(requirement_evidence["coverage_percent"] / 100, 0.0), 1.0))
    st.caption(f"Evidence coverage: {requirement_evidence['coverage_percent']}%")
    evidence_rows = pd.DataFrame(requirements).rename(
        columns={"requirement": "JD Capability", "status": "Coverage", "evidence": "Resume Evidence"}
    )
    st.dataframe(evidence_rows, width="stretch", hide_index=True)


def render_interview_prep_panel(interview_prep):
    st.markdown(section_card("Interview prep from JD", "Pattern-based questions generated from the JD and your current skills."), unsafe_allow_html=True)
    tech_col, project_col, behavior_col = st.columns(3)
    groups = [
        ("Technical", interview_prep.get("technical_questions", []), tech_col),
        ("Project", interview_prep.get("project_questions", []), project_col),
        ("Behavioral", interview_prep.get("behavioral_questions", []), behavior_col),
    ]
    for title, questions, column in groups:
        with column:
            st.markdown(f"#### {title}")
            if questions:
                for question in questions:
                    warning_bullet(question)
            else:
                st.info("Add a target job description to generate questions for this section.")


def render_semantic_evidence_panel(semantic_results):
    st.markdown(section_card("Semantic evidence", "Recovered resume signals and top JD-aligned capabilities used by the matcher."), unsafe_allow_html=True)
    evidence_col1, evidence_col2 = st.columns(2)
    with evidence_col1:
        strengths = [item["skill"] for item in semantic_results.get("resume_skill_evidence", [])[:12]]
        render_skill_panel("Recovered Resume Strengths", "Signals detected from parser output and full resume text.", strengths, tone="emerald")
    with evidence_col2:
        jd_matches = [
            f'{item["skill"]} · {item["score"]}%'
            for item in semantic_results.get("jd_skill_matches", [])[:12]
            if item.get("present_in_resume")
        ]
        if jd_matches:
            render_skill_panel("JD Signals Already Covered", "Capabilities the semantic matcher found in both the JD and your resume.", jd_matches, tone="slate")
        else:
            st.info("No strong shared JD signals were recovered yet.")


def render_analysis_report(*, analysis: dict, pdf_name: str, pdf_content: bytes, api_payload: dict, client):
    candidate = analysis["candidate"]
    summary = analysis["summary"]
    semantic_results = analysis["semantic_results"]
    semantic_error = analysis["semantic_error"]
    resume_score = summary["resume_score"]

    st.header("Resume report")
    st.success("Hello " + (candidate["name"] or api_payload["candidate_name"] or "there"))

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    with summary_col1:
        st.markdown(info_card("Resume score", f"{resume_score}/100", "Weighted from key sections found in the resume.", "warm"), unsafe_allow_html=True)
    with summary_col2:
        st.markdown(info_card("Career track", summary["career_track"], summary["role_title"], "teal"), unsafe_allow_html=True)
    with summary_col3:
        st.markdown(info_card("Candidate level", candidate["candidate_level"], f"{candidate['page_count']} page resume", "ink"), unsafe_allow_html=True)
    with summary_col4:
        semantic_score = f"{summary['semantic_match_score']}%" if summary["semantic_match_score"] is not None else "N/A"
        semantic_note = "Based on your pasted job description." if semantic_results else "Add a job description to calculate this."
        st.markdown(info_card("JD match", semantic_score, semantic_note, "warm"), unsafe_allow_html=True)

    report_tabs = st.tabs(["Overview", "ATS Sections", "JD Gap", "Bullet Checker", "Interview Prep", "PDF Report"])

    with report_tabs[0]:
        st.markdown(section_card("Candidate snapshot", "Core details extracted from the uploaded resume."), unsafe_allow_html=True)
        info_col1, info_col2 = st.columns([1.2, 1])
        with info_col1:
            st.markdown(candidate["highlights"])
            st.write(f"Name: {candidate['name']}")
            st.write(f"Email: {candidate['email']}")
            st.write(f"Contact: {candidate['mobile_number']}")
            st.write(f"Degree: {candidate['degree'] or 'Not found'}")
        with info_col2:
            render_pdf_preview(pdf_content)

        st.markdown(section_card("Skills and role direction", "Skills found in the resume, likely role track, and the most useful gaps to address."), unsafe_allow_html=True)
        render_skill_panel("Your Current Skills", "Detected directly from your resume", candidate["skills"], tone="emerald")
        st.info(f"Our analysis suggests you are trending toward {summary['role_title']} roles. {summary['match_reason']}")
        render_skill_panel("Recommended Skills For Your Next Iteration", "Add the strongest missing signals to improve role fit", summary["recommended_skills"], tone="blue")
        render_course_recommender(COURSE_LIBRARY.get(summary["courses_key"], ds_course))

        if semantic_results:
            st.markdown(section_card("Job match", "Semantic matching compares your resume with the job description and reference role profiles."), unsafe_allow_html=True)
            match_cols = st.columns(len(semantic_results["role_matches"]))
            for index, role in enumerate(semantic_results["role_matches"]):
                with match_cols[index]:
                    st.markdown(info_card(role["title"], f"{role['score']}%", role["summary"], "teal" if index == 0 else "ink"), unsafe_allow_html=True)
            render_semantic_evidence_panel(semantic_results)
        elif semantic_error:
            st.warning(
                "Semantic matching could not start yet. Install the embedding dependencies and ensure the model can download. "
                f"Details: {semantic_error}"
            )
        else:
            st.info("Paste a target job description above to calculate semantic role matches.")

    with report_tabs[1]:
        st.markdown(section_card("Section-level ATS score", "The original 10 ATS checks are grouped into scored categories with visual bars."), unsafe_allow_html=True)
        render_section_scorecards(analysis["ats_section_scores"])
        st.markdown(section_card("Detailed ATS checklist", "A weighted review of the sections recruiters usually expect to see."), unsafe_allow_html=True)
        for check in analysis["ats_checks"]:
            success_bullet(check["success"] if check["matched"] else check["warning"]) if check["matched"] else warning_bullet(check["warning"])
        st.subheader("Your Resume Score")
        st.progress(resume_score / 100)
        st.success("Your resume writing score is " + str(resume_score) + "/100")
        st.caption("This score is based on section coverage and positioning cues found in the uploaded resume.")

    with report_tabs[2]:
        render_requirement_evidence_panel(analysis["requirement_evidence"])
        render_gap_explainer_panel(analysis["gap_explainer"])
        if semantic_results:
            detail_col1, detail_col2 = st.columns(2)
            with detail_col1:
                render_skill_panel("Missing JD Keywords", "Keywords from the JD that do not yet appear clearly in your resume skills.", semantic_results["missing_keywords"], tone="slate")
            with detail_col2:
                render_skill_panel("Priority Keywords", "High-signal terms worth proving with projects, bullets, or skills.", semantic_results["priority_keywords"], tone="emerald")
            if semantic_results.get("jd_skill_matches"):
                evidence_rows = pd.DataFrame(semantic_results["jd_skill_matches"])
                evidence_rows["present_in_resume"] = evidence_rows["present_in_resume"].map({True: "Yes", False: "No"})
                st.markdown(section_card("Vector search matches", "JD-aligned capabilities ranked by semantic similarity and resume coverage."), unsafe_allow_html=True)
                st.dataframe(
                    evidence_rows.rename(columns={"skill": "Capability", "category": "Category", "score": "Semantic Score", "present_in_resume": "Found In Resume"}),
                    width="stretch",
                    height=320,
                )
        else:
            st.info("Add a target job description to generate the resume-to-job gap analysis.")

    with report_tabs[3]:
        render_bullet_quality_panel(analysis["bullet_quality"])

    with report_tabs[4]:
        render_interview_prep_panel(analysis["interview_prep"])

    with report_tabs[5]:
        st.markdown(section_card("PDF report export", "Download the full analysis summary as a PDF report."), unsafe_allow_html=True)
        report_key = f"pdf_report_{pdf_name}_{summary['resume_score']}"
        if report_key not in st.session_state:
            try:
                st.session_state[report_key] = client.download_report(**api_payload)
            except BackendAPIError as error:
                st.error(str(error))
                st.session_state[report_key] = None
        if st.session_state[report_key]:
            st.download_button(
                "Download PDF Report",
                data=st.session_state[report_key],
                file_name=f"{os.path.splitext(pdf_name)[0]}-analysis-report.pdf",
                mime="application/pdf",
                width="stretch",
            )
        st.caption("The export includes ATS section scores, evidence-backed JD mapping, bullet rewrite guidance, gap analysis, and interview prep prompts.")

    st.markdown(section_card("Recommended videos", "A few extra learning resources to improve your resume storytelling and interviews."), unsafe_allow_html=True)
    vid_col1, vid_col2 = st.columns(2)
    with vid_col1:
        st.markdown("**Resume Writing Tips**")
        st.video(random.choice(resume_videos))
    with vid_col2:
        st.markdown("**Interview Tips**")
        st.video(random.choice(interview_videos))
