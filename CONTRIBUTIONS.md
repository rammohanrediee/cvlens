# Contributions and project lineage

## Upstream

cvLens is based on [Deepak Padhi's AI Resume Analyzer](https://github.com/deepakpadhi986/AI-Resume-Analyzer), distributed under the MIT License. The upstream project established the resume-analysis concept, initial parsing foundation, recommendation data, and early candidate workflow. Its copyright notice remains in `LICENSE`.

## Current implementation

The current repository adds or rebuilds:

- a responsive React and Vite product workspace;
- a versioned FastAPI service with bounded requests and stable error contracts;
- native PDF extraction with page-quality checks and selective Tesseract OCR;
- deterministic ATS checks, skill normalization, bullet review, and PDF reports;
- resume-to-job requirement mapping with supporting evidence and gap categories;
- optional semantic matching with deterministic fallbacks;
- API authentication, rate limiting, request IDs, and sanitized logging;
- Python, React, dependency, Docker, and container checks in GitHub Actions;
- Docker and Nixpacks deployment configuration.

## Ownership map

| Path | Status |
|---|---|
| `backend/` | API, extraction, analysis, matching, and report implementation |
| `web/` | React product interface and browser API client |
| `tests/` | Unit, API, OCR, architecture, and boundary checks |
| `.github/workflows/` | Continuous integration and container verification |
| `Dockerfile`, `nixpacks.toml`, startup scripts | Deployment configuration |
| `LICENSE` | Retained upstream MIT license and copyright |

The repository name, current interface, API architecture, and new implementation work are maintained by Ram Mohan Reddy.
