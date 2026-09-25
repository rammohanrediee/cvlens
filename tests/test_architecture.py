import unittest


class ArchitectureTests(unittest.TestCase):
    def test_backend_layers_are_importable(self):
        from backend.app.main import create_app
        from backend.app.models.analysis import AnalysisRecord
        from backend.app.schemas.analysis import AnalysisRequest
        from backend.app.services.analysis_service import analyze_resume

        self.assertTrue(callable(create_app))
        self.assertTrue(callable(analyze_resume))
        self.assertEqual(AnalysisRequest(resume_text="Text").resume_text, "Text")
        self.assertEqual(AnalysisRecord(candidate_name="Asha").candidate_name, "Asha")

    def test_frontend_client_targets_backend_api(self):
        from frontend.api_client import ResumeAnalyzerClient

        client = ResumeAnalyzerClient("http://127.0.0.1:8001")
        self.assertEqual(client.base_url, "http://127.0.0.1:8001")
        self.assertTrue(callable(client.analyze))
        self.assertTrue(callable(client.download_report))


if __name__ == "__main__":
    unittest.main()
