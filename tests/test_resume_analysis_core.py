import unittest

from backend.app.core.resume_analysis import (
    _build_pdf_report_bytes_fallback,
    build_api_payload,
    build_requirement_evidence_matrix,
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


if __name__ == "__main__":
    unittest.main()
