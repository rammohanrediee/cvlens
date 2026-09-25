import json
import unittest
from pathlib import Path


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

    def test_react_workspace_declares_build_and_lint_commands(self):
        package_file = Path(__file__).resolve().parents[1] / "web" / "package.json"
        package = json.loads(package_file.read_text())

        self.assertEqual(package["scripts"]["build"], "vite build")
        self.assertEqual(package["scripts"]["lint"], "oxlint")
        self.assertIn("react", package["dependencies"])


if __name__ == "__main__":
    unittest.main()
