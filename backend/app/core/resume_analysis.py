import io
import json
import re
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .matching import (
    build_resume_highlights,
    canonicalize_skills,
    compute_semantic_matches,
    evaluate_resume_score,
    extract_keywords,
    infer_candidate_level,
    infer_role_from_skills,
    normalize_text,
)
from .parser import merge_resume_data

SECTION_CATEGORY_MAP = {
    "Objective or Summary": "Positioning",
    "Education": "Core Sections",
    "Skills": "Core Sections",
    "Experience": "Experience",
    "Internships": "Experience",
    "Projects": "Experience",
    "Achievements": "Proof",
    "Certifications": "Proof",
    "Interests": "Personality",
    "Hobbies": "Personality",
}

SECTION_CATEGORY_ORDER = ["Core Sections", "Experience", "Proof", "Personality", "Positioning"]

WEAK_BULLET_PHRASES = {
    "worked on": "Built",
    "responsible for": "Owned",
    "helped with": "Contributed to",
    "involved in": "Executed",
    "participated in": "Collaborated on",
    "assisted with": "Supported",
    "handled": "Managed",
    "did": "Delivered",
}

TOOLS_KEYWORDS = {
    "python", "sql", "excel", "tableau", "power bi", "aws", "azure", "gcp", "docker",
    "kubernetes", "react", "next.js", "node.js", "postgresql", "mysql", "mongodb",
    "tensorflow", "pytorch", "scikit-learn", "figma", "git", "github", "linux",
    "fastapi", "flask", "django", "java", "kotlin", "swift", "javascript", "typescript",
    "html", "css", "spark", "hadoop", "airflow", "redis",
}

DOMAIN_KEYWORDS = {
    "fintech", "healthcare", "ecommerce", "education", "saas", "b2b", "b2c",
    "payments", "fraud", "supply chain", "marketing", "analytics", "data science",
    "machine learning", "computer vision", "nlp", "recommendation", "product",
    "cloud", "security", "banking", "insurance", "retail",
}

EVIDENCE_KEYWORDS = {
    "stakeholders", "ownership", "roadmap", "architecture", "mentoring", "leadership",
    "scale", "scaled", "metrics", "results", "impact", "performance", "latency",
    "reliability", "optimization", "optimize", "improve", "improved", "reduce", "reduced",
    "increase", "increased", "deliver", "delivered",
}

SKILL_HINTS = {
    "testing", "debugging", "communication", "leadership", "analysis", "design",
    "deployment", "monitoring", "automation", "accessibility", "storytelling",
    "collaboration", "problem-solving", "architecture", "documentation",
}

ACTIONABLE_METRIC_HINT = "Add a metric, outcome, or scale detail so the bullet proves impact."
TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9+#./-]*")
PDF_FONT_NAME = "BBHBartle"
PDF_FONT_PATH = Path(__file__).resolve().parents[1] / "assets" / "fonts" / "BBHBartle-Regular.ttf"


def build_section_category_scores(score_checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for check in score_checks:
        category = SECTION_CATEGORY_MAP.get(check["label"], "Core Sections")
        if category not in grouped:
            grouped[category] = {
                "category": category,
                "score": 0,
                "max_score": 0,
                "checks": [],
            }
        grouped[category]["max_score"] += check["weight"]
        if check["matched"]:
            grouped[category]["score"] += check["weight"]
        grouped[category]["checks"].append(
            {
                "label": check["label"],
                "matched": check["matched"],
                "weight": check["weight"],
            }
        )

    categories = []
    for category in SECTION_CATEGORY_ORDER:
        if category not in grouped:
            continue
        entry = grouped[category]
        percent = round((entry["score"] / entry["max_score"]) * 100, 1) if entry["max_score"] else 0.0
        categories.append(
            {
                **entry,
                "percent": percent,
                "matched_checks": sum(1 for item in entry["checks"] if item["matched"]),
                "total_checks": len(entry["checks"]),
            }
        )
    return categories


def _extract_bullets(resume_text: str) -> list[str]:
    bullets = []
    for raw_line in (resume_text or "").splitlines():
        line = normalize_text(raw_line)
        if len(line) < 18:
            continue
        if re.match(r"^\s*[\-\*\u2022\u25cf]", raw_line):
            bullets.append(re.sub(r"^\s*[\-\*\u2022\u25cf]\s*", "", raw_line).strip())
            continue
        if re.match(r"^(worked on|responsible for|helped with|involved in|participated in|assisted with)\b", line.lower()):
            bullets.append(line)
    return bullets


def _rewrite_bullet(bullet: str) -> str:
    lowered = bullet.lower()
    suggestion = bullet
    for weak_phrase, replacement in WEAK_BULLET_PHRASES.items():
        if lowered.startswith(weak_phrase):
            remainder = bullet[len(weak_phrase):].strip(" :,-")
            suggestion = f"{replacement} {remainder}".strip()
            break
    if not re.search(r"\b\d+%|\b\d+\+|\b\d+\b", suggestion):
        suggestion = f"{suggestion.rstrip('.')} by using specific tools and measurable outcomes."
    return suggestion


def analyze_bullet_quality(resume_text: str) -> dict[str, Any]:
    bullets = _extract_bullets(resume_text)
    findings = []
    for bullet in bullets:
        lowered = bullet.lower()
        issues = []
        for weak_phrase in WEAK_BULLET_PHRASES:
            if weak_phrase in lowered:
                issues.append(f"Weak opener: '{weak_phrase}'")
                break
        if not re.search(r"\b\d+%|\b\d+\+|\b\d+\b", bullet):
            issues.append("Missing measurable result")
        if len(TOKEN_PATTERN.findall(bullet)) < 8:
            issues.append("Too short to show context and impact")
        if issues:
            findings.append(
                {
                    "original": bullet,
                    "issues": issues,
                    "suggestion": _rewrite_bullet(bullet),
                    "coaching_tip": ACTIONABLE_METRIC_HINT,
                }
            )

    return {
        "total_bullets": len(bullets),
        "flagged_bullets": findings,
        "summary": (
            f"Flagged {len(findings)} of {len(bullets)} bullets."
            if bullets
            else "No clear bullet lines were detected in the parsed resume text."
        ),
    }


def _keyword_in_resume(keyword: str, resume_text: str, resume_skills: list[str]) -> bool:
    lowered_resume = (resume_text or "").lower()
    lowered_skills = {skill.lower() for skill in (resume_skills or [])}
    return keyword.lower() in lowered_resume or keyword.lower() in lowered_skills


def categorize_gap_keywords(job_description: str, resume_text: str, resume_skills: list[str]) -> dict[str, list[str]]:
    categories = {
        "Skills": [],
        "Tools": [],
        "Domain": [],
        "Evidence": [],
    }
    for keyword in extract_keywords(job_description):
        if _keyword_in_resume(keyword, resume_text, resume_skills):
            continue
        lowered = keyword.lower()
        if lowered in TOOLS_KEYWORDS or any(marker in lowered for marker in [".js", "sql", "aws", "api", "figma"]):
            bucket = "Tools"
        elif lowered in DOMAIN_KEYWORDS:
            bucket = "Domain"
        elif lowered in EVIDENCE_KEYWORDS or any(marker in lowered for marker in ["metric", "scale", "stakeholder", "ownership"]):
            bucket = "Evidence"
        elif lowered in SKILL_HINTS or lowered.endswith(("ing", "tion", "ment")):
            bucket = "Skills"
        else:
            bucket = "Skills"
        categories[bucket].append(keyword)
    return {key: values[:10] for key, values in categories.items() if values}


def build_gap_explainer(job_description: str, resume_text: str, resume_skills: list[str]) -> dict[str, Any]:
    grouped = categorize_gap_keywords(job_description, resume_text, resume_skills)
    summary = []
    for category, items in grouped.items():
        summary.append(f"{category}: {', '.join(items[:4])}")
    return {
        "categorized_missing_keywords": grouped,
        "summary": " | ".join(summary) if summary else "No major JD gaps surfaced from keyword matching.",
    }


def build_requirement_evidence_matrix(
    job_description: str,
    resume_text: str,
    resume_skills: list[str],
    semantic_results: dict[str, Any] | None = None,
    limit: int = 12,
) -> dict[str, Any]:
    if not normalize_text(job_description):
        return {
            "requirements": [],
            "matched_count": 0,
            "total_count": 0,
            "coverage_percent": 0.0,
            "summary": "Add a target job description to generate evidence-backed requirement mapping.",
        }

    candidates = []
    if semantic_results:
        candidates = [item.get("skill", "") for item in semantic_results.get("jd_skill_matches", [])]
    if not candidates:
        candidates = extract_keywords(job_description)

    requirements = []
    seen = set()
    resume_lines = [normalize_text(line) for line in (resume_text or "").splitlines() if normalize_text(line)]
    normalized_skills = {normalize_text(skill).lower() for skill in resume_skills or []}

    for candidate in candidates:
        requirement = normalize_text(str(candidate))
        key = requirement.lower()
        if not key or key in seen or len(key) < 2:
            continue
        seen.add(key)

        evidence = next((line for line in resume_lines if key in line.lower()), "")
        listed_skill = key in normalized_skills
        matched = bool(evidence or listed_skill)
        if not evidence and listed_skill:
            evidence = "Listed in parsed resume skills."
        if len(evidence) > 180:
            evidence = evidence[:177].rstrip() + "..."

        requirements.append(
            {
                "requirement": requirement,
                "status": "Matched" if matched else "Missing",
                "evidence": evidence,
            }
        )
        if len(requirements) >= limit:
            break

    matched_count = sum(item["status"] == "Matched" for item in requirements)
    total_count = len(requirements)
    coverage_percent = round((matched_count / total_count) * 100, 1) if total_count else 0.0
    return {
        "requirements": requirements,
        "matched_count": matched_count,
        "total_count": total_count,
        "coverage_percent": coverage_percent,
        "summary": f"Found resume evidence for {matched_count} of {total_count} prioritized JD capabilities.",
    }


def generate_interview_prep(job_description: str, resume_skills: list[str], role_title: str) -> dict[str, Any]:
    jd_keywords = extract_keywords(job_description)[:8]
    skill_keywords = [skill for skill in (resume_skills or [])[:6]]
    technical = [
        f"How have you used {keyword} in a real project, and what tradeoffs did you make?"
        for keyword in jd_keywords[:3]
    ]
    project = [
        f"Walk me through a project where you used {skill} and explain the outcome."
        for skill in skill_keywords[:3]
    ]
    behavioral = [
        f"Tell me about a time you handled ambiguity while working toward a {role_title} outcome.",
        "Describe a time you improved a weak process, result, or metric.",
        "Tell me about a time you aligned stakeholders around a difficult technical decision.",
    ]
    return {
        "technical_questions": technical,
        "project_questions": project,
        "behavioral_questions": behavioral,
    }


def _safe_semantic_matches(job_description: str, resume_text: str, resume_skills: list[str]) -> tuple[dict[str, Any] | None, str | None]:
    if not normalize_text(job_description):
        return None, None
    try:
        return compute_semantic_matches(job_description, resume_text, resume_skills), None
    except Exception as exc:
        return None, str(exc)


def build_full_analysis(resume_data: dict[str, Any], resume_text: str, job_description: str) -> dict[str, Any]:
    parsed_resume_skills = resume_data.get("skills") or []
    role_summary = infer_role_from_skills(parsed_resume_skills, resume_text)
    candidate_level = infer_candidate_level(resume_data.get("no_of_pages", 0), resume_text)
    resume_score, score_checks = evaluate_resume_score(resume_text)
    section_scores = build_section_category_scores(score_checks)
    bullet_quality = analyze_bullet_quality(resume_text)
    semantic_results, semantic_error = _safe_semantic_matches(job_description, resume_text, parsed_resume_skills)
    resume_skills = (
        [item["skill"] for item in semantic_results.get("resume_skill_evidence", [])]
        if semantic_results else canonicalize_skills(parsed_resume_skills)
    )
    gap_explainer = build_gap_explainer(job_description, resume_text, resume_skills) if normalize_text(job_description) else {
        "categorized_missing_keywords": {},
        "summary": "Add a target job description to unlock gap analysis.",
    }
    requirement_evidence = build_requirement_evidence_matrix(
        job_description,
        resume_text,
        resume_skills,
        semantic_results,
    )
    interview_prep = generate_interview_prep(job_description, resume_skills, role_summary["title"]) if normalize_text(job_description) else {
        "technical_questions": [],
        "project_questions": [],
        "behavioral_questions": [],
    }

    return {
        "candidate": {
            "name": resume_data.get("name") or "Candidate",
            "email": resume_data.get("email") or "Not found",
            "mobile_number": resume_data.get("mobile_number") or "Not found",
            "degree": resume_data.get("degree") or [],
            "page_count": resume_data.get("no_of_pages", 0),
            "skills": resume_skills,
            "highlights": build_resume_highlights(resume_data),
            "candidate_level": candidate_level,
        },
        "summary": {
            "resume_score": resume_score,
            "career_track": role_summary["field"],
            "role_title": role_summary["title"],
            "recommended_skills": role_summary["recommended_skills"],
            "courses_key": role_summary["courses_key"],
            "match_reason": role_summary["match_reason"],
            "semantic_match_score": semantic_results["resume_job_similarity"] if semantic_results else None,
        },
        "ats_checks": score_checks,
        "ats_section_scores": section_scores,
        "bullet_quality": bullet_quality,
        "gap_explainer": gap_explainer,
        "requirement_evidence": requirement_evidence,
        "semantic_results": semantic_results,
        "semantic_error": semantic_error,
        "interview_prep": interview_prep,
        "job_description": job_description,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf_report_lines(report_title: str, analysis: dict[str, Any]) -> list[str]:
    lines = [
        report_title,
        "",
        f"Candidate: {analysis['candidate']['name']}",
        f"Role Track: {analysis['summary']['role_title']}",
        f"Resume Score: {analysis['summary']['resume_score']}/100",
        f"Candidate Level: {analysis['candidate']['candidate_level']}",
        f"Generated: {analysis['generated_at']}",
        "",
        "Section-Level ATS Scores:",
    ]
    for item in analysis["ats_section_scores"]:
        lines.append(f"- {item['category']}: {item['score']}/{item['max_score']} ({item['percent']}%)")

    lines.extend(["", "Bullet Quality Summary:", analysis["bullet_quality"]["summary"]])
    for finding in analysis["bullet_quality"]["flagged_bullets"][:5]:
        lines.append(f"- Original: {finding['original']}")
        lines.append(f"  Rewrite: {finding['suggestion']}")

    lines.extend(["", "JD Gap Summary:", analysis["gap_explainer"]["summary"], "", "Requirement Evidence:"])
    for item in analysis["requirement_evidence"]["requirements"][:8]:
        evidence = f" - {item['evidence']}" if item["evidence"] else ""
        lines.append(f"- {item['requirement']}: {item['status']}{evidence}")
    lines.extend(["", "Interview Prep Questions:"])
    for question in analysis["interview_prep"]["technical_questions"][:3]:
        lines.append(f"- {question}")
    for question in analysis["interview_prep"]["project_questions"][:2]:
        lines.append(f"- {question}")
    return lines


def _build_pdf_report_bytes_fallback(report_title: str, analysis: dict[str, Any]) -> bytes:
    lines = _build_pdf_report_lines(report_title, analysis)
    wrapped_lines = []
    for line in lines:
        wrapped_lines.extend(textwrap.wrap(line, width=92) or [""])

    page_chunks = [wrapped_lines[index:index + 42] for index in range(0, len(wrapped_lines), 42)] or [[]]
    objects = []
    kids = []

    objects.append("<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(None)

    page_object_numbers = []
    for page_lines in page_chunks:
        content_stream = ["BT", "/F1 10 Tf", "50 780 Td", "14 TL"]
        for line in page_lines:
            content_stream.append(f"({_escape_pdf_text(line)}) Tj")
            content_stream.append("T*")
        content_stream.append("ET")
        stream_text = "\n".join(content_stream)
        content_obj_no = len(objects) + 1
        objects.append(f"<< /Length {len(stream_text.encode('latin-1', errors='replace'))} >>\nstream\n{stream_text}\nendstream")
        page_obj_no = len(objects) + 1
        page_object_numbers.append(page_obj_no)
        kids.append(f"{page_obj_no} 0 R")
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {len(objects) + 1} 0 R >> >> /Contents {content_obj_no} 0 R >>"
        )
    objects[1] = f"<< /Type /Pages /Count {len(page_object_numbers)} /Kids [{' '.join(kids)}] >>"
    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font_object_number = len(objects)

    updated_objects = []
    for raw in objects:
        if "/Font << /F1" in raw:
            updated_objects.append(raw.replace(f"{font_object_number + 1} 0 R", f"{font_object_number} 0 R"))
        else:
            updated_objects.append(raw)

    pdf_parts = [b"%PDF-1.4\n"]
    offsets = [0]
    for index, obj in enumerate(updated_objects, start=1):
        offsets.append(sum(len(part) for part in pdf_parts))
        pdf_parts.append(f"{index} 0 obj\n{obj}\nendobj\n".encode("latin-1", errors="replace"))
    xref_offset = sum(len(part) for part in pdf_parts)
    pdf_parts.append(f"xref\n0 {len(updated_objects) + 1}\n".encode("latin-1"))
    pdf_parts.append(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf_parts.append(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf_parts.append(
        f"trailer\n<< /Size {len(updated_objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("latin-1")
    )
    return b"".join(pdf_parts)


def _build_pdf_report_bytes_with_reportlab(report_title: str, analysis: dict[str, Any]) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    top_margin = height - 54
    bottom_margin = 54
    line_height = 16
    font_size = 10.5
    wrap_width = 88

    pdfmetrics.registerFont(TTFont(PDF_FONT_NAME, str(PDF_FONT_PATH)))
    pdf.setTitle(report_title)

    y = top_margin
    for line in _build_pdf_report_lines(report_title, analysis):
        wrapped = textwrap.wrap(line, width=wrap_width) or [""]
        for segment in wrapped:
            if y < bottom_margin:
                pdf.showPage()
                y = top_margin
            pdf.setFont(PDF_FONT_NAME, 13 if segment == report_title else font_size)
            pdf.drawString(50, y, segment)
            y -= line_height

    pdf.save()
    return buffer.getvalue()


def build_pdf_report_bytes(report_title: str, analysis: dict[str, Any]) -> bytes:
    if PDF_FONT_PATH.exists():
        try:
            return _build_pdf_report_bytes_with_reportlab(report_title, analysis)
        except Exception:
            pass
    return _build_pdf_report_bytes_fallback(report_title, analysis)


def build_api_payload(
    resume_text: str,
    resume_skills: list[str],
    job_description: str,
    candidate_name: str = "",
    page_count: int | None = None,
) -> dict[str, Any]:
    parser_data = {
        "skills": resume_skills,
        "no_of_pages": page_count,
    }
    if candidate_name.strip():
        parser_data["name"] = candidate_name.strip()
    resume_data = merge_resume_data(resume_text, parser_data)
    return build_full_analysis(resume_data, resume_text, job_description)


def as_json(data: dict[str, Any]) -> bytes:
    return json.dumps(data, ensure_ascii=True).encode("utf-8")
