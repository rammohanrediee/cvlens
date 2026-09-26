import json
import unittest
from unittest.mock import Mock, patch

from backend.app.services.openrouter_analysis import (
    DEFAULT_OPENROUTER_MODEL,
    OpenRouterAnalysisError,
    analyze_with_openrouter,
)


RESUME_TEXT = (
    "Asha Rao\nasha@example.com\n+91 98765 43210\n"
    "Employment: 2020 - 2024\n"
    "EXPERIENCE\n"
    "Built Python APIs for 500 customers and reduced latency by 20%.\n"
    "Worked on dashboards for finance stakeholders."
)
JOB_DESCRIPTION = "Build Python APIs, improve service reliability, and communicate with finance stakeholders."
BULLETS = [
    "Built Python APIs for 500 customers and reduced latency by 20%.",
    "Worked on dashboards for finance stakeholders.",
]


def provider_payload(**overrides):
    payload = {
        "match_score": 82,
        "summary": "Strong API evidence with limited reliability detail.",
        "bullet_findings": [
            {
                "original": BULLETS[1],
                "issues": ["The outcome is not demonstrated."],
                "suggestion": "Built dashboards for finance stakeholders [add a verified outcome].",
                "coaching_tip": "Name the decision or measurable outcome supported by the dashboard.",
            }
        ],
        "requirements": [
            {
                "requirement": "Python APIs",
                "status": "Matched",
                "evidence": "Built Python APIs for 500 customers and reduced latency by 20%.",
                "rationale": "The resume explicitly describes production API work.",
            },
            {
                "requirement": "service reliability",
                "status": "Missing",
                "evidence": "",
                "rationale": "No resume line directly supports reliability ownership.",
            },
        ],
    }
    payload.update(overrides)
    return payload


class OpenRouterAnalysisTests(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {
            "OPENROUTER_API_KEY": "server-secret",
            "OPENROUTER_MODEL": DEFAULT_OPENROUTER_MODEL,
            "OPENROUTER_SITE_URL": "https://cvlens.example",
        },
        clear=False,
    )
    @patch("backend.app.services.openrouter_analysis.httpx.post")
    def test_sends_grounded_structured_request_and_redacts_contact_details(self, post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(provider_payload())}}],
            "usage": {"prompt_tokens": 120, "completion_tokens": 80},
        }
        post.return_value = response

        result = analyze_with_openrouter(RESUME_TEXT, JOB_DESCRIPTION, BULLETS)

        self.assertEqual(result["model"], DEFAULT_OPENROUTER_MODEL)
        self.assertEqual(result["match_score"], 82)
        self.assertEqual(result["usage"], {"prompt_tokens": 120, "completion_tokens": 80})
        request = post.call_args
        self.assertEqual(request.kwargs["headers"]["Authorization"], "Bearer server-secret")
        self.assertEqual(request.kwargs["json"]["model"], "z-ai/glm-5.3-flash")
        self.assertEqual(request.kwargs["json"]["response_format"]["type"], "json_schema")
        serialized_request = json.dumps(request.kwargs["json"])
        self.assertNotIn("asha@example.com", serialized_request)
        self.assertNotIn("98765", serialized_request)
        self.assertIn("2020 - 2024", serialized_request)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}, clear=False)
    def test_requires_server_side_api_key(self):
        with self.assertRaisesRegex(OpenRouterAnalysisError, "not configured"):
            analyze_with_openrouter(RESUME_TEXT, JOB_DESCRIPTION, BULLETS)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "server-secret"}, clear=False)
    @patch("backend.app.services.openrouter_analysis.httpx.post")
    def test_rejects_suggestion_that_invents_a_metric(self, post):
        invented = provider_payload()
        invented["bullet_findings"][0]["suggestion"] = "Built dashboards that increased revenue by 35%."
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"choices": [{"message": {"content": json.dumps(invented)}}]}
        post.return_value = response

        with self.assertRaisesRegex(OpenRouterAnalysisError, "invented metric"):
            analyze_with_openrouter(RESUME_TEXT, JOB_DESCRIPTION, BULLETS)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "server-secret"}, clear=False)
    @patch("backend.app.services.openrouter_analysis.httpx.post")
    def test_rejects_evidence_that_is_not_an_exact_resume_line(self, post):
        unsupported = provider_payload()
        unsupported["requirements"][0]["evidence"] = "Asha led a team of ten API engineers."
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"choices": [{"message": {"content": json.dumps(unsupported)}}]}
        post.return_value = response

        with self.assertRaisesRegex(OpenRouterAnalysisError, "unsupported evidence"):
            analyze_with_openrouter(RESUME_TEXT, JOB_DESCRIPTION, BULLETS)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "server-secret"}, clear=False)
    @patch("backend.app.services.openrouter_analysis.httpx.post")
    def test_returns_stable_error_for_malformed_provider_response(self, post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"choices": []}
        post.return_value = response

        with self.assertRaisesRegex(OpenRouterAnalysisError, "invalid response"):
            analyze_with_openrouter(RESUME_TEXT, JOB_DESCRIPTION, BULLETS)


if __name__ == "__main__":
    unittest.main()
