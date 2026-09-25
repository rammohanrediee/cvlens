import unittest

from backend.app.core.parser import (
    extract_degrees,
    extract_email,
    extract_name,
    extract_phone,
    extract_structured_skills,
    merge_resume_data,
)


class ParserUtilsTests(unittest.TestCase):
    def test_extracts_basic_contact_fields(self):
        text = """
        Ramu Kumar
        ramu@example.com
        +91 98765 43210
        """
        self.assertEqual(extract_name(text), "Ramu Kumar")
        self.assertEqual(extract_email(text), "ramu@example.com")
        self.assertIn("98765", extract_phone(text))

    def test_extracts_degree_and_skills_from_text(self):
        text = """
        EDUCATION
        B.Tech in Computer Science

        SKILLS
        Python, React.js, Postgres, Docker, FastAPI
        """
        self.assertIn("B.Tech", extract_degrees(text))
        skills = extract_structured_skills(text)
        self.assertIn("Python", skills)
        self.assertIn("React", skills)
        self.assertIn("SQL", skills)
        self.assertIn("Docker", skills)

    def test_merge_resume_data_prefers_parser_and_fallback_union(self):
        text = """
        Asha Sharma
        asha@example.com
        Projects
        Built APIs with FastAPI and Docker for analytics workflows.
        """
        merged = merge_resume_data(
            text,
            {
                "name": None,
                "email": None,
                "mobile_number": None,
                "skills": ["Python"],
                "degree": [],
                "no_of_pages": 1,
            },
        )
        self.assertEqual(merged["name"], "Asha Sharma")
        self.assertEqual(merged["email"], "asha@example.com")
        self.assertIn("Python", merged["skills"])
        self.assertIn("FastAPI", merged["skills"])
        self.assertIn("Docker", merged["skills"])


if __name__ == "__main__":
    unittest.main()
