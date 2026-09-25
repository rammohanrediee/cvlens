import json
import os
from uuid import uuid4
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class BackendAPIError(RuntimeError):
    pass


class ResumeAnalyzerClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or os.getenv("BACKEND_API_URL", "http://127.0.0.1:8001")).rstrip("/")
        self.api_key = api_key if api_key is not None else os.getenv("RESUME_API_KEY", "")

    def _post(self, path: str, payload: dict, *, accept: str = "application/json"):
        headers = {"Content-Type": "application/json", "Accept": accept}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                return response.read()
        except HTTPError as error:
            try:
                payload = json.loads(error.read().decode("utf-8"))
                message = payload.get("error", {}).get("message")
            except (UnicodeDecodeError, json.JSONDecodeError):
                message = None
            raise BackendAPIError(message or "The backend rejected the request.") from error
        except URLError as error:
            raise BackendAPIError(
                "The backend API is unavailable. Start it with `python -m backend.app.main`."
            ) from error

    def extract_document(self, *, filename: str, pdf_bytes: bytes) -> dict:
        boundary = f"resume-analyzer-{uuid4().hex}"
        safe_filename = filename.replace('"', "").replace("\r", "").replace("\n", "") or "resume.pdf"
        body = (
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="file"; filename="{safe_filename}"\r\n'
                "Content-Type: application/pdf\r\n\r\n"
            ).encode("utf-8")
            + pdf_bytes
            + f"\r\n--{boundary}--\r\n".encode("utf-8")
        )
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(
            f"{self.base_url}/api/v1/documents/extract",
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))["data"]
        except HTTPError as error:
            try:
                payload = json.loads(error.read().decode("utf-8"))
                message = payload.get("error", {}).get("message")
            except (UnicodeDecodeError, json.JSONDecodeError):
                message = None
            raise BackendAPIError(message or "The backend rejected the resume PDF.") from error
        except (URLError, TimeoutError) as error:
            raise BackendAPIError("The backend could not process the resume PDF.") from error
        except (KeyError, json.JSONDecodeError) as error:
            raise BackendAPIError("The backend returned an unexpected extraction response.") from error

    def is_available(self) -> bool:
        """Return whether the configured analysis API is reachable."""
        try:
            with urlopen(f"{self.base_url}/api/v1/health", timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return response.status == 200 and payload.get("data", {}).get("status") == "ok"
        except (HTTPError, URLError, json.JSONDecodeError, TimeoutError):
            return False

    def analyze(
        self,
        *,
        candidate_name: str,
        resume_text: str,
        resume_skills: list[str],
        job_description: str,
        page_count: int,
    ) -> dict:
        try:
            body = self._post(
                "/api/v1/analyses",
                {
                    "candidate_name": candidate_name,
                    "resume_text": resume_text,
                    "resume_skills": resume_skills,
                    "job_description": job_description,
                    "page_count": page_count,
                },
            )
            return json.loads(body.decode("utf-8"))["data"]
        except (KeyError, json.JSONDecodeError) as error:
            raise BackendAPIError("The backend API returned an unexpected response.") from error

    def download_report(
        self,
        *,
        candidate_name: str,
        resume_text: str,
        resume_skills: list[str],
        job_description: str,
        page_count: int,
    ) -> bytes:
        return self._post(
            "/api/v1/reports/pdf",
            {
                "candidate_name": candidate_name,
                "resume_text": resume_text,
                "resume_skills": resume_skills,
                "job_description": job_description,
                "page_count": page_count,
            },
            accept="application/pdf",
        )
