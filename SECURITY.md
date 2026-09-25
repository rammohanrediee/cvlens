# Security and Privacy

## Reporting a vulnerability

Please report security issues privately through GitHub's security advisory
workflow. Do not include real resumes, credentials, access tokens, or personal
information in a public issue.

## Data handling

Resume text and uploaded PDF bytes are processed for the active request. The
current application does not persist resumes or analysis results. Browser-side
suggestion drafts remain in memory and do not alter the uploaded document.

## Public deployment checklist

- Terminate TLS at a trusted reverse proxy or deployment platform.
- Set `API_HOST=0.0.0.0` and the platform-provided `PORT`.
- Set a strong, unique `RESUME_API_KEY` for API bearer authentication.
- Route the React client's `/api` requests through the same trusted reverse proxy.
- Apply deployment-level request and resource limits in addition to API limits.
- Rotate credentials after any suspected exposure.
