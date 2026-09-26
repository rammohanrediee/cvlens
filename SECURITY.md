# Security and Privacy

## Reporting a vulnerability

Please report security issues privately through GitHub's security advisory
workflow. Do not include real resumes, credentials, access tokens, or personal
information in a public issue.

## Data handling

Resume text and uploaded PDF bytes are processed for the active request. The
current application does not persist resumes or analysis results. Browser-side
suggestion drafts remain in memory and do not alter the uploaded document.

Enhanced AI review is disabled per request unless the user selects it. For an
enhanced request, email addresses, phone numbers, and URLs are removed before
bounded resume text and the job description are sent to OpenRouter. OpenRouter
and its routed inference provider then become subprocessors for that request;
deployment privacy notices and retention settings must reflect their current
terms. The `OPENROUTER_API_KEY` is a backend-only secret.

## Public deployment checklist

- Terminate TLS at a trusted reverse proxy or deployment platform.
- Set `API_HOST=0.0.0.0` and the platform-provided `PORT`.
- Keep the backend private and set a strong, unique `RESUME_API_KEY` for bearer authentication. A trusted reverse proxy must discard client-supplied authorization before injecting this backend-only secret.
- If the service is intentionally public and anonymous, set `ALLOW_UNAUTHENTICATED_POSTS=true` explicitly and enforce edge rate, concurrency, body-size, and timeout limits.
- Start the service with `python -m backend.app.main`; direct ASGI factory launches must select an authenticated or explicitly anonymous deployment mode.
- Isolate PDF/OCR workers in separately constrained processes for hostile multi-tenant uploads. In-process semaphores bound concurrency and queue waits, but cannot terminate a native parser or OCR library call that has stalled.
- Route the React client's `/api` requests through the same trusted reverse proxy.
- Apply deployment-level request and resource limits in addition to API limits.
- Rotate credentials after any suspected exposure.
