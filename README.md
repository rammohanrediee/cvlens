# CVLens

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![React 19](https://img.shields.io/badge/React-19-149ECA?logo=react&logoColor=white)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Tests](https://github.com/rammohanrediee/cvlens/actions/workflows/tests.yml/badge.svg)](https://github.com/rammohanrediee/cvlens/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-216B4B.svg)](LICENSE)

CVLens is a responsive resume analysis workspace built with React and FastAPI. It extracts text from PDF resumes, checks document structure and bullet quality, compares resume evidence with a pasted job description, and generates a downloadable analysis report.

Scores and suggestions are decision support. They do not reproduce a specific employer's applicant tracking system or guarantee an interview.

## Product preview

### Resume upload

![CVLens resume upload workspace](images/cvlens-upload.png)

### Analysis workspace

![CVLens analysis overview](images/cvlens-analysis.png)

### Mobile suggestion editor

<p align="center">
  <img src="images/cvlens-mobile-editor.png" alt="CVLens mobile suggestion editor" width="375">
</p>

## What it does

- Accepts PDF resumes up to 5 MiB and 20 pages.
- Uses native PDF text when available and Tesseract OCR for weak or image-only pages.
- Detects contact details, education, skills, experience, projects, achievements, and certifications.
- Scores resume structure and groups ATS checks into passed and needs-attention sections.
- Reviews weak bullet openings, missing metrics, and short evidence statements.
- Compares a resume with a pasted job description using deterministic matching and optional embeddings.
- Maps requirements to supporting resume lines and identifies missing skills, tools, domain terms, and evidence.
- Supports editable local suggestion drafts, copying, skip and undo, and a full-screen mobile editor.
- Generates a downloadable PDF analysis report.

## Technology

| Layer | Technology |
|---|---|
| Web client | React 19, Vite 7, JavaScript, CSS design tokens |
| API | FastAPI, Uvicorn, Pydantic |
| Resume analysis | Python, scikit-learn, deterministic parsers |
| PDF extraction | PyMuPDF, pdfminer.six, Tesseract OCR |
| PDF reports | ReportLab with a built-in fallback writer |
| Automation | GitHub Actions, Ruff, Coverage, pip-audit, Docker |

## Architecture

```text
.
├── backend/app/
│   ├── api/                 # FastAPI routes and request boundary
│   ├── core/                # Parsing, scoring, matching, and report generation
│   ├── models/              # Domain records
│   ├── schemas/             # Request and response models
│   └── services/            # Analysis and PDF extraction use cases
├── web/
│   ├── src/components/      # Upload, navigation, and result views
│   ├── src/api.js           # Browser API client
│   ├── src/App.jsx          # Product workflow and state
│   └── vite.config.js       # Local API proxy
├── tests/                   # Python unit, API, OCR, and architecture checks
├── images/                  # README product screenshots
├── requirements/            # Development and optional semantic dependencies
├── Dockerfile               # FastAPI container
└── .github/workflows/       # Python, web, and container checks
```

```mermaid
flowchart LR
    U[React workspace] -->|PDF upload| API[FastAPI]
    API --> X[Native extraction]
    X --> Q{Text quality}
    Q -->|Usable| A[Analysis core]
    Q -->|Weak page| O[Tesseract OCR]
    O --> A
    U -->|Job description| A
    A --> R[Scores, evidence, gaps, suggestions]
    R --> U
    A --> P[PDF report]
```

The browser uses Vite's `/api` proxy during local development. The API performs extraction and analysis and returns structured JSON; the React workspace owns interaction state such as selected tabs and suggestion drafts.

## Getting started

### Requirements

- Python 3.11 or newer
- Node.js 22 or newer
- Tesseract 5 with English language data

On macOS:

```bash
brew install tesseract
```

### Install the API

```bash
git clone https://github.com/rammohanrediee/cvlens.git
cd cvlens

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Optional semantic matching:

```bash
python -m pip install -r requirements/semantic.txt
```

### Install the web client

```bash
cd web
npm ci
cd ..
```

## Run locally

Start FastAPI in the first terminal:

```bash
source .venv/bin/activate
python -m backend.app.main
```

Start React in the second terminal:

```bash
cd web
npm run dev
```

Open `http://127.0.0.1:5173`. The API runs at `http://127.0.0.1:8001`, and its OpenAPI documentation is available at `http://127.0.0.1:8001/docs`.

## Configuration

The backend reads process environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `API_HOST` | `127.0.0.1` | API bind address |
| `PORT` | `8001` | API port |
| `RESUME_API_KEY` | empty | Requires a bearer token for POST requests when set |
| `API_RATE_LIMIT_PER_MINUTE` | `60` | Per-client POST request limit |
| `HF_TOKEN` | empty | Token for optional Hugging Face model downloads |

The web client calls the same origin by default. `web/.env.example` therefore leaves the API base URL empty:

```env
VITE_API_BASE_URL=
```

During local development, Vite proxies `/api` to port 8001. Production should route the same path to FastAPI through the site's reverse proxy.

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health |
| `POST` | `/api/v1/documents/extract` | PDF text extraction and OCR |
| `POST` | `/api/v1/analyses` | Complete resume and job-description analysis |
| `POST` | `/api/v1/analyses/bullet-quality` | Bullet-quality review |
| `POST` | `/api/v1/analyses/jd-gap` | Categorized job-description gaps |
| `POST` | `/api/v1/analyses/interview-prep` | Interview-question generation |
| `POST` | `/api/v1/reports/pdf` | Downloadable PDF report |

Example health check:

```bash
curl http://127.0.0.1:8001/api/v1/health
```

## Development checks

Python checks:

```bash
python -m pip install -r requirements/dev.txt
ruff check backend tests
coverage run --source=backend.app -m unittest discover -s tests -v
coverage report -m --fail-under=80
```

React checks:

```bash
cd web
npm run lint
npm run build
```

GitHub Actions runs the Python checks, the React lint/build, a dependency audit, a Docker build, and a container health check.

## Deployment

The Docker image and `nixpacks.toml` run the FastAPI service on port 8001:

```bash
docker build -t cvlens-api .
docker run --rm -p 8001:8001 cvlens-api
```

Build the React client separately:

```bash
cd web
npm ci
npm run build
```

Deploy `web/dist/` with a static host or reverse proxy. Route `/api` to the FastAPI service so the browser and API share an origin.

## Privacy and limits

- Uploaded PDF bytes and resume text are processed for the active request and are not persisted by this repository.
- Local suggestion drafts stay in browser memory and do not modify the uploaded PDF.
- Request size, PDF size, page count, and extracted-text limits are enforced by the API.
- PDF quality depends on the source document's layout and embedded fonts.
- Keyword and embedding similarity do not prove proficiency or job readiness.
- Suggested rewrites require human review; never add unsupported claims or metrics.

## Project lineage

CVLens is based on [Deepak Padhi's AI Resume Analyzer](https://github.com/deepakpadhi986/AI-Resume-Analyzer), used under the MIT License. The current repository adds the React product workspace, FastAPI boundary, bounded PDF/OCR extraction, evidence-backed job matching, report generation, automated checks, and deployment configuration.

See [CONTRIBUTIONS.md](CONTRIBUTIONS.md), [NOTICE](NOTICE), and [LICENSE](LICENSE) for attribution and license details.

## License

CVLens is available under the [MIT License](LICENSE). The upstream copyright and permission notice are retained.
