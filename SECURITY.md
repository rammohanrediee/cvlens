# Security and Privacy

## Reporting a vulnerability

Please report security issues privately through GitHub's security advisory
workflow. Do not include real resumes, credentials, access tokens, or personal
information in a public issue.

## Data handling

Resume text and uploaded PDF bytes are processed for the active session and are
not persisted by the analytics layer. Anonymous analytics are disabled by
default. When enabled, the database stores only aggregate analysis fields and
anonymous feedback.

The admin console includes a confirmed deletion action. It clears current
analytics and removes the legacy `user_data` and `user_feedback` tables that
older versions used for personal data.

## Public deployment checklist

- Terminate TLS at a trusted reverse proxy or deployment platform.
- Set `API_HOST=0.0.0.0` and the platform-provided `PORT`.
- Set a strong, unique `RESUME_API_KEY` for API bearer authentication.
- Generate `ADMIN_PASSWORD_HASH` with `python scripts/hash_admin_password.py`.
- Keep analytics disabled unless aggregate metrics are genuinely required.
- Restrict database access to the application services.
- Rotate credentials after any suspected exposure.
