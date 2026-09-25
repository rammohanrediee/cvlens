import sqlite3
import unittest

from frontend.services.storage import (
    FrontendDatabase,
    build_analysis_event,
    hash_admin_password,
    verify_admin_password,
)


class StoragePrivacyTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.database = FrontendDatabase(self.connection, "sqlite")
        self.database.initialize()

    def tearDown(self):
        self.connection.close()

    def test_analysis_schema_excludes_resume_and_personal_identifiers(self):
        columns = {
            row[1]
            for row in self.connection.execute("PRAGMA table_info(analysis_events)").fetchall()
        }
        forbidden = {
            "pdf_content",
            "pdf_name",
            "name",
            "email",
            "mobile",
            "ip_address",
            "host_name",
            "device_user",
            "os_name",
        }
        self.assertFalse(columns.intersection(forbidden))

    def test_analysis_event_contains_only_aggregate_product_metrics(self):
        event = build_analysis_event(
            analysis={
                "candidate": {
                    "name": "Ramu Reddy",
                    "email": "ramu@example.com",
                    "mobile_number": "9876543210",
                    "page_count": 2,
                    "candidate_level": "Fresher",
                    "skills": ["Python", "SQL"],
                },
                "summary": {
                    "resume_score": 78,
                    "career_track": "Data Science",
                    "recommended_skills": ["Docker"],
                },
            },
            recommended_courses=["Practical MLOps"],
        )

        serialized = repr(event)
        self.assertNotIn("Ramu Reddy", serialized)
        self.assertNotIn("ramu@example.com", serialized)
        self.assertNotIn("9876543210", serialized)
        self.assertEqual(event["page_count"], 2)

    def test_feedback_storage_does_not_collect_name_or_email(self):
        self.database.save_feedback(score=4, comments="Clear report")
        feedback = self.database.load_feedback()
        self.assertEqual(list(feedback.columns), ["ID", "Feedback Score", "Comments", "Timestamp"])
        self.assertEqual(feedback.iloc[0]["Comments"], "Clear report")

    def test_admin_passwords_are_verified_from_salted_hashes(self):
        password_hash = hash_admin_password("correct horse")
        self.assertTrue(verify_admin_password("correct horse", password_hash))
        self.assertFalse(verify_admin_password("wrong password", password_hash))

    def test_admin_can_delete_all_anonymous_analytics(self):
        event = build_analysis_event(
            analysis={
                "candidate": {"page_count": 1, "candidate_level": "Fresher", "skills": []},
                "summary": {
                    "resume_score": 50,
                    "career_track": "Data Science",
                    "recommended_skills": [],
                },
            },
            recommended_courses=[],
        )
        self.database.save_analysis(event)
        self.database.save_feedback(score=5, comments="Useful")
        self.connection.execute("CREATE TABLE user_data (email TEXT, pdf_content BLOB)")
        self.connection.execute("CREATE TABLE user_feedback (feed_email TEXT)")
        self.connection.commit()

        self.database.clear_analytics()

        self.assertEqual(len(self.database.load_feedback()), 0)
        self.assertEqual(len(self.database.load_admin_frames()[0]), 0)
        tables = {
            row[0]
            for row in self.connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        self.assertNotIn("user_data", tables)
        self.assertNotIn("user_feedback", tables)
