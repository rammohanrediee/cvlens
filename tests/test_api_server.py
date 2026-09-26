import unittest
from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from backend.app.api.server import MAX_REQUEST_BYTES, RequestRateLimiter, create_app, resolve_server_config, run
from backend.app.schemas.analysis import MAX_JOB_DESCRIPTION_CHARACTERS, MAX_RESUME_CHARACTERS, MAX_RESUME_SKILLS


SAMPLE_RESUME = """
- Worked on a customer analytics dashboard using Python and SQL.
- Responsible for data cleaning and reporting.
- Built churn models that improved retention by 12%.
"""

SAMPLE_JD = """
Looking for a backend engineer with Python, FastAPI, SQL, Docker, cloud deployment,
stakeholder communication, and experience scaling APIs for fintech products.
"""


class ResumeAnalysisAPITestCase(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict("os.environ", {"RESUME_API_KEY": "", "API_RATE_LIMIT_PER_MINUTE": "60"})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.app = create_app(host="127.0.0.1")
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def assert_error(self, response, status, code):
        self.assertEqual(response.status_code, status, response.text)
        self.assertEqual(response.json()["error"]["code"], code)
        self.assertIn("x-request-id", response.headers)

    def test_health_endpoint(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["status"], "ok")

    def test_unknown_endpoint_returns_json_404(self):
        for method in ("get", "post"):
            with self.subTest(method=method):
                self.assert_error(getattr(self.client, method)("/missing"), 404, "not_found")
        self.assert_error(self.client.put("/api/v1/health"), 405, "method_not_allowed")

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            "/api/v1/analyses", content=b"{not-json", headers={"Content-Type": "application/json"}
        )
        self.assert_error(response, 400, "invalid_json")

    def test_json_body_must_be_an_object(self):
        self.assert_error(self.client.post("/api/v1/analyses", json=[]), 400, "invalid_request")

    def test_invalid_field_types_are_rejected_without_echoing_private_input(self):
        for fields in (
            {"page_count": 0},
            {"page_count": True},
            {"page_count": "2"},
            {"resume_text": {"private": "sensitive-resume"}},
            {"resume_skills": "Python"},
            {"use_ai_analysis": "true"},
        ):
            with self.subTest(fields=fields):
                response = self.client.post("/api/v1/analyses", json={"resume_text": SAMPLE_RESUME, **fields})
                self.assert_error(response, 422, "validation_error")
                self.assertNotIn("sensitive-resume", response.text)
                self.assertNotIn(SAMPLE_RESUME, response.text)

    def test_analysis_fields_have_product_specific_limits(self):
        invalid_payloads = (
            {"resume_text": "x" * (MAX_RESUME_CHARACTERS + 1)},
            {"resume_text": SAMPLE_RESUME, "job_description": "x" * (MAX_JOB_DESCRIPTION_CHARACTERS + 1)},
            {"resume_text": SAMPLE_RESUME, "resume_skills": ["Python"] * (MAX_RESUME_SKILLS + 1)},
            {"resume_text": SAMPLE_RESUME, "page_count": 21},
        )
        for payload in invalid_payloads:
            with self.subTest(fields=payload.keys()):
                self.assert_error(self.client.post("/api/v1/analyses", json=payload), 422, "validation_error")

    def test_analysis_endpoint(self):
        response = self.client.post(
            "/api/v1/analyses",
            json={
                "candidate_name": "Asha",
                "resume_text": SAMPLE_RESUME,
                "resume_skills": ["Python", "SQL"],
                "job_description": SAMPLE_JD,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["candidate"]["name"], "Asha")
        self.assertIn("ats_section_scores", data)
        self.assertIn("bullet_quality", data)
        self.assertGreater(data["requirement_evidence"]["total_count"], 0)

    def test_analysis_endpoint_uses_openrouter_only_when_explicitly_requested(self):
        ai_result = {
            "model": "z-ai/glm-5.3-flash",
            "match_score": 88,
            "summary": "The resume directly supports the API requirement.",
            "bullet_findings": [],
            "requirements": [
                {
                    "requirement": "Python API",
                    "status": "Matched",
                    "evidence": "Built a Python API for customer analytics.",
                    "rationale": "The resume contains direct API delivery evidence.",
                }
            ],
            "usage": {"prompt_tokens": 80, "completion_tokens": 40},
        }
        with patch("backend.app.core.resume_analysis.analyze_with_openrouter", return_value=ai_result) as analyze_ai:
            response = self.client.post(
                "/api/v1/analyses",
                json={
                    "resume_text": "EXPERIENCE\n- Built a Python API for customer analytics.",
                    "job_description": "Build a Python API for customer analytics products.",
                    "use_ai_analysis": True,
                },
            )

        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()["data"]
        self.assertEqual(data["ai_analysis"]["status"], "completed")
        self.assertEqual(data["summary"]["semantic_match_score"], 88)
        analyze_ai.assert_called_once()

    def test_analysis_endpoint_returns_parsed_resume_metadata(self):
        response = self.client.post(
            "/api/v1/analyses",
            json={
                "candidate_name": "",
                "resume_text": (
                    "Ramu Reddy\nramu@example.com\n+91 98765 43210\nEDUCATION\nB.Tech\nSKILLS\nPython, FastAPI, SQL"
                ),
                "page_count": 2,
                "job_description": "Python API engineer",
            },
        )
        candidate = response.json()["data"]["candidate"]
        self.assertEqual(candidate["name"], "Ramu Reddy")
        self.assertEqual(candidate["email"], "ramu@example.com")
        self.assertEqual(candidate["page_count"], 2)

    def test_rejects_request_larger_than_configured_limit(self):
        response = self.client.post(
            "/api/v1/analyses", content=b"{}", headers={"Content-Length": str(MAX_REQUEST_BYTES + 1)}
        )
        self.assert_error(response, 413, "payload_too_large")
        # No Content-Length: enforce the actual stream size, not just the header.
        chunks = (b"x" * (MAX_REQUEST_BYTES // 2) for _ in range(3))
        response = self.client.post("/api/v1/analyses", content=chunks)
        self.assert_error(response, 413, "payload_too_large")

    def test_requires_bearer_token_when_api_key_is_configured(self):
        with patch.dict("os.environ", {"RESUME_API_KEY": "test-secret"}):
            for token in ("", "test-secret", "Bearer wrong"):
                response = self.client.post(
                    "/api/v1/analyses", json={"resume_text": SAMPLE_RESUME}, headers={"Authorization": token}
                )
                self.assert_error(response, 401, "unauthorized")
            response = self.client.post(
                "/api/v1/analyses", json={"resume_text": SAMPLE_RESUME}, headers={"Authorization": "Bearer test-secret"}
            )
            self.assertEqual(response.status_code, 200)

    @patch.dict("os.environ", {"API_HOST": "0.0.0.0", "PORT": "9123"}, clear=False)
    def test_server_configuration_uses_deployment_environment(self):
        self.assertEqual(resolve_server_config(), ("0.0.0.0", 9123))

    def test_public_binding_requires_authentication_or_explicit_anonymous_opt_in(self):
        public_environment = {
            "API_HOST": "0.0.0.0",
            "RESUME_API_KEY": "",
            "ALLOW_UNAUTHENTICATED_POSTS": "",
        }
        with patch.dict("os.environ", public_environment, clear=False):
            with self.assertRaisesRegex(RuntimeError, "RESUME_API_KEY"):
                create_app(host="0.0.0.0")

        public_environment["ALLOW_UNAUTHENTICATED_POSTS"] = "true"
        with patch.dict("os.environ", public_environment, clear=False):
            app = create_app(host="0.0.0.0")
            self.assertIsNotNone(app)

    def test_app_factory_requires_an_explicit_bind_or_deployment_security_mode(self):
        with patch.dict(
            "os.environ",
            {"RESUME_API_KEY": "", "ALLOW_UNAUTHENTICATED_POSTS": ""},
            clear=False,
        ):
            with self.assertRaisesRegex(RuntimeError, "explicit bind host"):
                create_app()
            self.assertIsNotNone(create_app(host="127.0.0.2"))

    def test_cli_host_override_cannot_bypass_public_bind_guard(self):
        with patch.dict(
            "os.environ",
            {
                "API_HOST": "127.0.0.1",
                "RESUME_API_KEY": "",
                "ALLOW_UNAUTHENTICATED_POSTS": "",
            },
            clear=False,
        ):
            with patch("backend.app.api.server.uvicorn.run") as uvicorn_run:
                with self.assertRaisesRegex(RuntimeError, "RESUME_API_KEY"):
                    run(host="0.0.0.0")
        uvicorn_run.assert_not_called()

    def test_rate_limiter_rejects_requests_after_the_window_limit(self):
        limiter = RequestRateLimiter(limit=2, window_seconds=60, max_clients=1)
        self.assertTrue(limiter.allow("client", now=100.0))
        self.assertTrue(limiter.allow("client", now=101.0))
        self.assertFalse(limiter.allow("client", now=102.0))
        self.assertFalse(limiter.allow("another", now=102.0))
        self.assertTrue(limiter.allow("another", now=161.0))
        self.app.state.rate_limiter.limit = 1
        self.client.post("/api/v1/analyses", json={"resume_text": SAMPLE_RESUME})
        response = self.client.post("/api/v1/analyses", json={"resume_text": SAMPLE_RESUME})
        self.assert_error(response, 429, "rate_limited")
        self.assertEqual(response.headers["retry-after"], "60")
        self.assertEqual(self.client.get("/api/v1/health").status_code, 200)

    def test_bullet_quality_endpoint(self):
        response = self.client.post("/api/v1/analyses/bullet-quality", json={"resume_text": SAMPLE_RESUME})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()["data"]["flagged_bullets"]), 1)

    def test_interview_prep_endpoint(self):
        response = self.client.post(
            "/api/v1/analyses/interview-prep",
            json={
                "job_description": SAMPLE_JD,
                "resume_skills": ["Python", "SQL"],
                "role_title": "Backend Engineer",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()["data"]["technical_questions"]), 0)

    def test_gap_endpoint_requires_fields(self):
        self.assert_error(
            self.client.post("/api/v1/analyses/jd-gap", json={"resume_text": SAMPLE_RESUME}), 422, "validation_error"
        )
        response = self.client.post(
            "/api/v1/analyses/jd-gap",
            json={
                "resume_text": SAMPLE_RESUME,
                "job_description": SAMPLE_JD,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())

    def test_pdf_report_endpoint(self):
        response = self.client.post(
            "/api/v1/reports/pdf",
            json={
                "candidate_name": "Asha",
                "resume_text": SAMPLE_RESUME,
                "resume_skills": ["Python", "SQL"],
                "job_description": SAMPLE_JD,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertIn("attachment", response.headers["content-disposition"])
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_document_upload_extracts_text_and_rejects_non_pdf_content(self):
        pdf_buffer = BytesIO()
        document = canvas.Canvas(pdf_buffer)
        document.drawString(72, 760, "Ramu Reddy Python FastAPI SQL backend engineer")
        document.drawString(72, 730, "Built and tested reliable resume analysis services")
        document.save()

        response = self.client.post(
            "/api/v1/documents/extract",
            files={"file": ("resume.pdf", pdf_buffer.getvalue(), "application/pdf")},
        )
        self.assertEqual(response.status_code, 200, response.text)
        extraction = response.json()["data"]
        self.assertEqual(extraction["method"], "native")
        self.assertEqual(extraction["page_count"], 1)
        self.assertIn("Python", extraction["text"])

        response = self.client.post(
            "/api/v1/documents/extract",
            files={"file": ("resume.txt", b"private resume", "text/plain")},
        )
        self.assert_error(response, 415, "unsupported_media_type")
        self.assertNotIn("private resume", response.text)

    def test_failures_and_logs_do_not_expose_resume_contents(self):
        with patch("backend.app.api.routes.analysis.analyze_resume", side_effect=RuntimeError("sensitive-resume")):
            with self.assertLogs("resume.api", level="INFO") as logs:
                response = self.client.post(
                    "/api/v1/analyses?private=sensitive-resume", json={"resume_text": "sensitive-resume"}
                )
        self.assert_error(response, 500, "internal_error")
        self.assertNotIn("sensitive-resume", response.text + " ".join(logs.output))
        self.assertIn(response.headers["x-request-id"], " ".join(logs.output))

    def test_openapi_exposes_request_contracts(self):
        schema = self.client.get("/openapi.json").json()
        self.assertIn("/api/v1/reports/pdf", schema["paths"])
        self.assertIn("/api/v1/documents/extract", schema["paths"])
        self.assertIn("resume_text", schema["components"]["schemas"]["AnalysisRequest"]["required"])


if __name__ == "__main__":
    unittest.main()
