import unittest
from unittest.mock import patch

from backend.app.core.matching import (
    canonicalize_skills,
    compute_semantic_matches,
    cosine_similarity,
    evaluate_resume_score,
    extract_resume_evidence,
    infer_candidate_level,
    infer_role_from_skills,
)
from backend.app.core.analysis_data import ROLE_CATALOG, SECTION_RULES, SKILL_ONTOLOGY


class MatchingUtilsTests(unittest.TestCase):
    def test_analysis_catalogs_have_stable_metadata(self):
        self.assertEqual(sum(rule["weight"] for rule in SECTION_RULES), 100)
        self.assertEqual(len({rule["key"] for rule in SECTION_RULES}), len(SECTION_RULES))
        self.assertTrue(all(rule["category"] for rule in SECTION_RULES))
        self.assertTrue(all(role["key"] for role in ROLE_CATALOG))
        self.assertEqual(len({role["key"] for role in ROLE_CATALOG}), len(ROLE_CATALOG))
        self.assertTrue(all(entry["name"] and entry["category"] for entry in SKILL_ONTOLOGY))

    def test_section_aliases_and_match_source_are_reported(self):
        resume_text = """
        Professional Summary
        Work History
        Technical Skills
        Case Studies
        """
        _, checks = evaluate_resume_score(resume_text)
        matched = {check["label"]: check for check in checks if check["matched"]}

        self.assertEqual(matched["Objective or Summary"]["matched_by"], "pattern")
        self.assertEqual(matched["Experience"]["matched_by"], "pattern")
        self.assertEqual(matched["Skills"]["matched_by"], "pattern")
        self.assertEqual(matched["Projects"]["matched_by"], "pattern")

    def test_section_fallback_is_data_driven(self):
        _, checks = evaluate_resume_score("- Built a service\n- Improved reliability")
        by_label = {check["label"]: check for check in checks}

        self.assertEqual(by_label["Experience"]["matched_by"], "bullet_fallback")
        self.assertEqual(by_label["Projects"]["matched_by"], "bullet_fallback")

    def test_resume_score_rewards_detected_sections(self):
        resume_text = """
        Summary
        Education
        Work Experience
        Skills
        Projects
        Certifications
        """
        score, checks = evaluate_resume_score(resume_text)
        self.assertGreaterEqual(score, 70)
        self.assertTrue(any(check["label"] == "Projects" and check["matched"] for check in checks))

    def test_candidate_level_prefers_experience_signal(self):
        self.assertEqual(infer_candidate_level(0, ""), "NA")
        self.assertEqual(infer_candidate_level(2, "Work Experience with backend ownership"), "Experienced")
        self.assertEqual(infer_candidate_level(1, "Internship at a startup"), "Intermediate")
        self.assertEqual(infer_candidate_level(1, "Portfolio and education details only"), "Fresher")

    def test_role_inference_from_skills(self):
        result = infer_role_from_skills(["React", "JavaScript", "CSS", "Accessibility"])
        self.assertEqual(result["field"], "Web Development")
        self.assertIn("TypeScript", result["recommended_skills"])

    def test_role_inference_has_sparse_resume_fallback(self):
        result = infer_role_from_skills([], "")
        self.assertEqual(result["field"], "General")

    def test_skill_canonicalization_normalizes_aliases(self):
        normalized = canonicalize_skills(["Postgres", "postgresql", "Node", "React.js", "JS"])
        self.assertIn("SQL", normalized)
        self.assertIn("Node.js", normalized)
        self.assertIn("React", normalized)
        self.assertIn("JavaScript", normalized)

    def test_resume_evidence_recovers_skills_from_resume_text(self):
        resume_text = "Built APIs with FastAPI, Docker, and PostgreSQL. Improved API latency by 40%."
        evidence = extract_resume_evidence(resume_text, ["Python"])
        self.assertIn("FastAPI", evidence)
        self.assertIn("Docker", evidence)
        self.assertIn("SQL", evidence)

    def test_role_inference_uses_resume_text_evidence(self):
        result = infer_role_from_skills(["Python"], "Built REST APIs with Docker, PostgreSQL, caching, and authentication.")
        self.assertEqual(result["title"], "Backend Engineer")

    def test_role_catalog_expansion_supports_devops_signals(self):
        result = infer_role_from_skills(
            ["Docker", "AWS"],
            "Managed CI/CD pipelines, Kubernetes clusters, Terraform modules, and cloud observability.",
        )
        self.assertEqual(result["title"], "DevOps Engineer")

    def test_resume_score_rewards_metrics_and_bullets(self):
        resume_text = """
        Summary
        Education
        Experience
        Projects
        Skills
        - Improved API latency by 42%
        - Reduced build time by 30%
        - Led a migration for 5000 users
        - Built dashboards for analytics reviews
        """
        score, _ = evaluate_resume_score(resume_text)
        self.assertGreaterEqual(score, 75)

    def test_semantic_matching_fallback_uses_normalized_resume_evidence(self):
        with patch("backend.app.core.matching.build_vector_indexes", side_effect=RuntimeError("embedding unavailable")):
            results = compute_semantic_matches(
                "Looking for a backend engineer with FastAPI, Docker, PostgreSQL, and authentication experience.",
                "Built APIs using FastAPI, Docker, and Postgres. Implemented auth flows for internal tools.",
                ["Python", "Node"],
            )
        self.assertGreater(len(results["role_matches"]), 0)
        self.assertIn("FastAPI", results["priority_keywords"] + [item["skill"] for item in results["jd_skill_matches"]])
        self.assertIn("SQL", [item["skill"] for item in results["resume_skill_evidence"]])

    def test_semantic_matching_uses_available_vector_index(self):
        class FakeModel:
            def encode(self, texts, convert_to_numpy=True):
                return [[1.0, 0.0] for _ in texts]

        fake_indexes = {
            "model": FakeModel(),
            "role_vectors": [[1.0, 0.0]] * 20,
            "skill_vectors": [[1.0, 0.0]] * 100,
        }
        with patch("backend.app.core.matching.build_vector_indexes", return_value=fake_indexes):
            results = compute_semantic_matches(
                "Python backend engineer",
                "Built Python APIs",
                ["Python"],
            )
        self.assertGreater(results["resume_job_similarity"], 0)
        self.assertGreater(len(results["role_matches"]), 0)

    def test_cosine_similarity_handles_zero_and_aligned_vectors(self):
        self.assertEqual(cosine_similarity([0, 0], [1, 0]), 0.0)
        self.assertEqual(cosine_similarity([1, 0], [1, 0]), 1.0)


if __name__ == "__main__":
    unittest.main()
