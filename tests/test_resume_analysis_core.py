import unittest
from unittest.mock import patch

from backend.app.core.resume_analysis import (
    _build_pdf_report_bytes_fallback,
    analyze_bullet_quality,
    build_api_payload,
    build_requirement_evidence_matrix,
    build_section_category_scores,
    categorize_gap_keywords,
)


class ResumeAnalysisCoreTests(unittest.TestCase):
    def test_api_payload_parses_contact_degree_skills_and_real_page_count(self):
        analysis = build_api_payload(
            resume_text=(
                "Ramu Reddy\nramu@example.com\n+91 98765 43210\n"
                "EDUCATION\nB.Tech in Artificial Intelligence\n"
                "SKILLS\nPython, FastAPI, SQL\n"
                "PROJECTS\nBuilt a resume analysis API with automated tests."
            ),
            resume_skills=[],
            job_description="Python FastAPI engineer",
            candidate_name="",
            page_count=2,
        )

        candidate = analysis["candidate"]
        self.assertEqual(candidate["name"], "Ramu Reddy")
        self.assertEqual(candidate["email"], "ramu@example.com")
        self.assertIn("98765", candidate["mobile_number"])
        self.assertIn("B.Tech", candidate["degree"])
        self.assertEqual(candidate["page_count"], 2)
        self.assertIn("Python", candidate["skills"])
        self.assertIn("Python", candidate["highlights"])

    def test_full_analysis_without_job_description_uses_guidance_defaults(self):
        analysis = build_api_payload(
            resume_text="Summary\nSkills\nPython\nProjects\n- Built an API for 500 users",
            resume_skills=["Python"],
            job_description="",
            candidate_name="Asha",
        )
        self.assertEqual(analysis["candidate"]["name"], "Asha")
        self.assertIsNone(analysis["semantic_results"])
        self.assertEqual(analysis["interview_prep"]["technical_questions"], [])

    def test_builtin_pdf_fallback_produces_valid_pdf(self):
        analysis = build_api_payload(
            resume_text="Summary\nSkills\nPython\n- Built an API for 500 users",
            resume_skills=["Python"],
            job_description="Python API engineer",
        )
        report = _build_pdf_report_bytes_fallback("Resume (Analysis)", analysis)
        self.assertTrue(report.startswith(b"%PDF-1.4"))
        self.assertTrue(report.endswith(b"%%EOF"))

    def test_requirement_evidence_maps_jd_capabilities_to_resume_lines(self):
        result = build_requirement_evidence_matrix(
            job_description="Python SQL Docker",
            resume_text="Skills: Python and SQL\nBuilt a reporting API for 500 users.",
            resume_skills=["Python", "SQL"],
            semantic_results={
                "jd_skill_matches": [
                    {"skill": "Python"},
                    {"skill": "SQL"},
                    {"skill": "Docker"},
                ]
            },
        )

        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(result["total_count"], 3)
        self.assertEqual(result["coverage_percent"], 66.7)
        self.assertEqual(result["requirements"][0]["status"], "Matched")
        self.assertIn("Skills: Python and SQL", result["requirements"][0]["evidence"])
        self.assertEqual(result["requirements"][2]["status"], "Missing")

    def test_requirement_evidence_requires_a_job_description(self):
        result = build_requirement_evidence_matrix("", "Skills: Python", ["Python"])
        self.assertEqual(result["requirements"], [])
        self.assertEqual(result["coverage_percent"], 0.0)

    def test_requirement_evidence_uses_term_boundaries(self):
        result = build_requirement_evidence_matrix(
            job_description="SQL required",
            resume_text="Built a NoSQL database.",
            resume_skills=[],
            semantic_results={"jd_skill_matches": [{"skill": "SQL"}]},
        )

        self.assertEqual(result["requirements"][0]["status"], "Missing")
        self.assertEqual(result["coverage_percent"], 0.0)

    def test_gap_keywords_use_term_boundaries(self):
        result = categorize_gap_keywords("Git required", "Worked on digital products.", [])

        self.assertIn("git", result["Tools"])

    def test_section_category_scores_preserve_partial_credit(self):
        result = build_section_category_scores(
            [
                {
                    "label": "Experience",
                    "category": "Experience",
                    "required": True,
                    "matched": True,
                    "score": 8,
                    "weight": 16,
                }
            ]
        )

        self.assertEqual(result[0]["score"], 8)
        self.assertEqual(result[0]["percent"], 50.0)

    def test_bullet_quality_supports_numbered_bullets_and_rejects_years_as_impact(self):
        result = analyze_bullet_quality(
            "1. Built a customer API and completed the initial release in 2024\n"
            "2. Improved API latency for enterprise customers by 20% across three regions"
        )

        self.assertEqual(result["total_bullets"], 2)
        self.assertIn("Missing measurable result", result["flagged_bullets"][0]["issues"])
        self.assertEqual(len(result["flagged_bullets"]), 1)

    def test_semantic_failures_return_a_stable_public_error_code(self):
        with patch("backend.app.core.resume_analysis.compute_semantic_matches", side_effect=RuntimeError("private path")):
            analysis = build_api_payload("Summary\nSkills\nPython", ["Python"], "Python engineer")

        self.assertEqual(analysis["semantic_error"], "semantic_unavailable")
        self.assertNotIn("private path", str(analysis))

    def test_requested_openrouter_analysis_replaces_heuristics_with_grounded_results(self):
        ai_result = {
            "model": "z-ai/glm-5.3-flash",
            "match_score": 84,
            "summary": "The resume supports most backend requirements.",
            "bullet_findings": [
                {
                    "original": "Worked on a customer API for banking teams.",
                    "issues": ["The outcome is not demonstrated."],
                    "suggestion": "Built a customer API for banking teams [add a verified outcome].",
                    "coaching_tip": "Add a verified result without inventing a metric.",
                }
            ],
            "requirements": [
                {
                    "requirement": "Python APIs",
                    "status": "Matched",
                    "evidence": "Worked on a customer API for banking teams.",
                    "rationale": "Direct API delivery evidence.",
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        }
        with patch("backend.app.core.resume_analysis.analyze_with_openrouter", return_value=ai_result) as analyze_ai:
            analysis = build_api_payload(
                "EXPERIENCE\n- Worked on a customer API for banking teams.",
                ["Python"],
                "Build Python APIs for banking customers.",
                use_ai_analysis=True,
            )

        analyze_ai.assert_called_once()
        self.assertEqual(analysis["ai_analysis"]["status"], "completed")
        self.assertEqual(analysis["ai_analysis"]["model"], "z-ai/glm-5.3-flash")
        self.assertEqual(analysis["summary"]["semantic_match_score"], 84)
        self.assertEqual(analysis["bullet_quality"]["analysis_method"], "openrouter_llm")
        self.assertEqual(analysis["requirement_evidence"]["coverage_percent"], 100.0)

    def test_openrouter_failure_preserves_deterministic_results_with_visible_status(self):
        with patch(
            "backend.app.core.resume_analysis.analyze_with_openrouter",
            side_effect=RuntimeError("provider secret"),
        ):
            analysis = build_api_payload(
                "EXPERIENCE\n- Worked on a customer API for banking teams.",
                ["Python"],
                "Build Python APIs for banking customers.",
                use_ai_analysis=True,
            )

        self.assertEqual(analysis["ai_analysis"]["status"], "unavailable")
        self.assertEqual(analysis["bullet_quality"]["analysis_method"], "deterministic")
        self.assertNotIn("provider secret", str(analysis))

    def test_openrouter_is_not_called_without_explicit_user_consent(self):
        with patch("backend.app.core.resume_analysis.analyze_with_openrouter") as analyze_ai:
            analysis = build_api_payload(
                "EXPERIENCE\n- Worked on a customer API for banking teams.",
                ["Python"],
                "Build Python APIs for banking customers.",
            )

        analyze_ai.assert_not_called()
        self.assertEqual(analysis["ai_analysis"]["status"], "not_requested")


if __name__ == "__main__":
    unittest.main()
