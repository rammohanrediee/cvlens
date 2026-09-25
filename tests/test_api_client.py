import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from frontend.api_client import ResumeAnalyzerClient


class ResumeAnalyzerClientTestCase(unittest.TestCase):
    @patch("frontend.api_client.urlopen")
    def test_healthcheck_reports_connected_api(self, mocked_urlopen):
        response = MagicMock()
        response.status = 200
        response.read.return_value = json.dumps({"data": {"status": "ok"}}).encode("utf-8")
        mocked_urlopen.return_value.__enter__.return_value = response

        self.assertTrue(ResumeAnalyzerClient("http://example.test").is_available())
        mocked_urlopen.assert_called_once_with("http://example.test/api/v1/health", timeout=2)

    @patch("frontend.api_client.urlopen", side_effect=URLError("offline"))
    def test_healthcheck_reports_unavailable_api(self, _mocked_urlopen):
        self.assertFalse(ResumeAnalyzerClient("http://example.test").is_available())

    @patch("frontend.api_client.urlopen")
    def test_client_sends_api_key_page_count_and_pdf_upload(self, mocked_urlopen):
        response = MagicMock()
        response.read.return_value = json.dumps({"data": {"candidate": {}}}).encode("utf-8")
        mocked_urlopen.return_value.__enter__.return_value = response

        client = ResumeAnalyzerClient("http://example.test", api_key="secret")
        client.analyze(
            candidate_name="Ramu",
            resume_text="Python",
            resume_skills=[],
            job_description="Python engineer",
            page_count=2,
        )

        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")
        self.assertEqual(json.loads(request.data)["page_count"], 2)

        response.read.return_value = json.dumps({"data": {"text": "Python", "page_count": 1}}).encode("utf-8")
        extraction = client.extract_document(filename='resume".pdf', pdf_bytes=b"%PDF-data")
        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(extraction["page_count"], 1)
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")
        self.assertIn("multipart/form-data", request.get_header("Content-type"))
        self.assertIn(b'filename="resume.pdf"', request.data)
        self.assertIn(b"%PDF-data", request.data)


if __name__ == "__main__":
    unittest.main()
