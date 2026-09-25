import unittest
from pathlib import Path
import tomllib


class ProjectStructureTests(unittest.TestCase):
    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    def test_application_uses_separate_backend_and_web_client(self):
        backend_dir = self.PROJECT_ROOT / "backend" / "app"
        web_dir = self.PROJECT_ROOT / "web"

        self.assertTrue((backend_dir / "main.py").is_file())
        self.assertTrue((backend_dir / "api" / "server.py").is_file())
        self.assertTrue((backend_dir / "core" / "resume_analysis.py").is_file())
        self.assertTrue((backend_dir / "services" / "pdf_extraction.py").is_file())
        self.assertTrue((backend_dir / "models" / "analysis.py").is_file())
        self.assertTrue((backend_dir / "schemas" / "analysis.py").is_file())
        self.assertTrue((web_dir / "package.json").is_file())
        self.assertTrue((web_dir / "src" / "App.jsx").is_file())
        self.assertTrue((web_dir / "src" / "api.js").is_file())
        self.assertTrue((web_dir / "src" / "components" / "ResultsView.jsx").is_file())
        self.assertTrue((web_dir / "vite.config.js").is_file())

    def test_application_modules_import_from_project_root(self):
        from backend.app import main
        from backend.app.core import matching, parser, resume_analysis

        self.assertTrue(callable(main.create_app))
        self.assertTrue(callable(matching.compute_semantic_matches))
        self.assertTrue(callable(parser.parse_resume_document))
        self.assertTrue(callable(resume_analysis.build_full_analysis))

    def test_package_metadata_installs_runtime_dependencies(self):
        metadata = tomllib.loads((self.PROJECT_ROOT / "pyproject.toml").read_text())
        self.assertIn("dependencies", metadata["project"]["dynamic"])
        dependency_file = metadata["tool"]["setuptools"]["dynamic"]["dependencies"]["file"]
        self.assertEqual(dependency_file, ["requirements.txt"])


if __name__ == "__main__":
    unittest.main()
