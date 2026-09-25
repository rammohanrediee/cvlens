# AI Resume Analyzer — Verification Log

## 2026-09-22 — Replacement frontend specification

- Read existing Streamlit report rendering and FastAPI route declarations; distinguished existing analysis features from proposed React session interactions.
- Created root design.md and FRONTEND_PLAN.md; corrected the current checkout path in tracking files and recorded the React rollback.
- Palette OKLCH values calculated from supplied hex colors. Responsive widths and interaction checks are acceptance criteria, not completed browser checks.
- Documentation only: no frontend implementation, new tests, runtime changes or visual pass claimed.

## Existing evidence carried forward

- Remote audit: confirmed repository is a fork of `deepakpadhi986/AI-Resume-Analyzer`; comparison at inspection showed 10 commits ahead, 0 behind and 95 changed files. This demonstrates differences, not individual authorship or quality by itself.
- Inspected HEAD: `b3e819b3c7e5d7584cf1b5dad1bfc6e362178458`.
- Existing GitHub Actions run reported success: https://github.com/rammohanrediee/AI-Resume-Analyzer/actions/runs/30190193694 . This is historical CI evidence, not a new local test run.
- Inspected source showed PDF extraction and analytics persistence under frontend services, a `ThreadingHTTPServer` backend, and SQLite-based storage tests. Those findings motivate the backend-boundary work.

## 2026-09-22 — Local workspace and tooling inspection

- `git status --short`, `git log -5 --oneline`, and `git remote -v` in the supplied local checkout showed a different remote and an uncommitted matching change. No files were changed there.
- `headroom --version`: 0.37.0. MCP compression returned successfully; inspected content remained unchanged (0 tokens saved). Configured proxy was unreachable.
- A Headroom `loc --help` invocation attempted to download its scc dependency and failed due to network resolution. Repository inspection continued with existing tools; this is not an application failure.
- Referenced PeerMock's season/episode and checkpoint format read-only. Created this project's separate tracker, checkpoint, decisions and verification documents.

## Future entry format

For each episode record: date; branch/commit and relevant dirty state; changed behaviour; exact verification command; result; test environment; skipped/failed checks and reason; completion gate status; next action. Keep logs free of credentials and resume contents.

## Unverified at tracker creation (superseded by milestone evidence below)

Authoritative repository's local installation, test baseline, running frontend/backend flow, PostgreSQL integration, React implementation, new FastAPI implementation, benchmarks and deployment. None is marked complete.

## Tracker relocation

At the user’s request, moved all four trackers into the local project’s `docs/project-tracking/` directory. Verified document contents and relative links. No application code, Git remote, or existing matching changes were modified. The original task-output files now only point to this canonical location.

## 2026-09-22 — S0 baseline and S1E1 FastAPI milestone

- Checkout: `AI-Resume-Analyzer-authoritative`, origin `rammohanrediee/AI-Resume-Analyzer`,
  main initially clean at `b3e819b`. Original sibling checkout preserved.
- Environment: fresh Python 3.12 virtual environment; Tesseract available. Installed
  `requirements/dev.txt`. FastAPI 0.141.1 and Pydantic 2.13.5 resolved for local checks.
- Baseline command: `coverage run --source=backend.app -m unittest discover -s tests -v`:
  61 passed, including real OCR. `coverage report --fail-under=80`: 91%.
- After migration, same suite: 62 passed, no skips; backend coverage 92%.
- `ruff check backend frontend scripts tests`: passed. `python -m pip check`: passed.
- `pip-audit -r requirements.txt`: passed, no known vulnerabilities reported.
- Real process smoke: launched `python -m backend.app.main` on an ephemeral localhost
  port with an API key. Used the unchanged `ResumeAnalyzerClient` to check health,
  analyze a synthetic resume and download a PDF. All passed; server terminated cleanly.
- Existing API tests were migrated to TestClient and consolidated; only one net test was
  added. Tests protect strict field validation, real body limits without Content-Length,
  rate-limit enforcement, bearer authentication, error/log privacy and OpenAPI contracts.
- `git diff --check`: passed. Only changed Python files were formatted.
- Local Docker verification unavailable: daemon socket absent. Hosted CI container job
  remains required after push; do not claim local Docker success.
- Dependencies emit non-failing Starlette/httpx and PyMuPDF deprecation warnings. No
  optional embedding model was installed; live analysis smoke exercises lexical fallback.
- Scope remaining: backend PDF boundary, PostgreSQL migration/integration, React frontend,
  deployment and measured portfolio results. Whole-project completion is not claimed.

## 2026-09-22 — S1E2 backend PDF/OCR boundary

- Moved framework-independent extraction into `backend/app/services/pdf_extraction.py`.
  Streamlit keeps PDF preview responsibilities and calls the backend upload API for text.
- Added `POST /api/v1/documents/extract` with multipart parsing, exact PDF media-type
  validation, safe domain errors, worker-thread execution, and OpenAPI documentation.
- Enforced 5 MiB file, 20-page document, five-page OCR, and 200,000-character output
  limits. Multipart requests are bounded at 6 MiB before route processing.
- Full command: `.venv/bin/coverage run --source=backend.app -m unittest discover -s tests -v`
  followed by `.venv/bin/coverage report --fail-under=80`: 64 passed, no skips, 91%.
- `.venv/bin/ruff check backend frontend scripts tests`: passed.
  `.venv/bin/python -m pip check`: passed. `.venv/bin/pip-audit -r requirements.txt`:
  passed with no known vulnerabilities reported. `git diff --check`: passed.
- A real Uvicorn process with API-key authentication accepted a generated PDF through
  `ResumeAnalyzerClient.extract_document`, returned native extracted text, and completed
  analysis through the existing endpoint. The server was then terminated cleanly.
- No hard wall-clock cancellation surrounds parser/OCR worker threads. File, page, OCR-page,
  request, and text-output bounds constrain normal work; deployment-level request timeouts
  remain a release requirement.
- Docker was not repeated because the previously observed local daemon socket remains
  unavailable. Hosted CI remains the container verification path.
- S1E2 gate passed. Per user priority, S2E1 React work is next; S1E3 analytics/database
  restructuring is deferred until the React core workflow is usable.
## 2026-09-22 — Replacement React workspace

- `npm run lint`: passed with oxlint.
- `npm run build`: passed with Vite 7.3.6; 35 modules transformed.
- Real browser smoke at 1440 px: PDF upload → FastAPI extraction → analysis → Overview passed.
- Real response rendered resume structure 41/100, JD similarity 50%, candidate level
  Experienced and five backend-provided section scores; no demo metrics were fabricated.
- Responsive browser inspection passed at 375 px for the Results view. The desktop rail
  collapses to a compact application header and native view selector.

## 2026-09-24 — Hallmark React redesign and S2E3 completion

- Rebuilt upload and results around the Hallmark Workbench specification while preserving
  React/Vite, FastAPI contracts, Streamlit, and real backend-derived content.
- npm run lint: passed with oxlint.
- npm run build: passed with Vite 7.3.6; 39 modules transformed.
- Real local browser flow passed: selected a generated PDF, extracted it through FastAPI,
  analyzed it, rendered results, and downloaded resume-lens-qa-analysis-report.pdf.
- Results expose Overview, ATS Check, Suggestions, and Keywords without demo scores or
  screenshot-only product claims. Report download and document replacement are wired.
- Visual and overflow checks passed at 320, 375, 414, 768, 1024, 1280, and 1440 px.
  Desktop and mobile upload/results screenshots were inspected under output/playwright/.
- Mobile menu opens and closes with Escape. Keyboard focus on the visually hidden file
  input produces a visible two-pixel outline on the upload control.
- Results tabs use the WAI-ARIA tab pattern: from Suggestions, ArrowRight moved focus and
  selection to Keywords and rendered the matching Keywords tabpanel.
- Calculated contrast ratios: ink/paper 16.91:1; soft/paper 10.16:1;
  muted/paper 5.37:1; accent-ink/accent 4.75:1; focus/paper 5.50:1;
  warning-ink/warning-surface 9.10:1; error/error-surface 5.61:1.
- Hallmark/static checks found no gradients, transition-all, 100vw, raw hex/RGB/HSL page
  colors, italic headings, placeholder marketing cliches, or undefined CSS variables.
  Runtime and portable token blocks match; JSON metadata and git diff whitespace validate.
- Backend source was unchanged, so the full Python suite was not repeated for this visual
  milestone. S2E4 remains open for repeated analyses, deliberate failures/late responses,
  and zoom verification.

## 2026-09-24 — Product-workspace redesign

- Replaced the intermediate document layout with exclusive tab panels, contextual document
  tools, grouped ATS disclosures and local suggestion editing. No backend changes.
- npm run lint and npm run build passed after the primary implementation.
- Real synthetic PDF → extraction → analysis → results → PDF report download passed.
- Keyboard ArrowRight selected ATS; its first disclosure expanded. Native preview opened,
  Escape closed it and restored focus to View resume. Download filename was
  resume-lens-qa-analysis-report.pdf; saved locally under output/playwright/.
- Upload and actual-result widths 320/375/414/768/1280/1440 had document width equal to viewport.
  Exactly one result tab panel was visible at every measured width. At 1280×800 the upload
  CTA bottom was 793.22px (inside the fold). Screenshots: output/playwright/v3-*.
- The first synthetic resume returned no specific bullet rewrites; the honest empty state
  was observed. A second temporary synthetic PDF with weak bullet openers returned two
  actual backend findings and populated the draft editor.
- Primary palette contrast: ink/canvas 15.39:1; muted/canvas 5.57:1; white/green button
  6.42:1; soft ink/white 9.75:1; muted/green-tint 5.42:1.
- One replacement test timed out because an index.html title edit caused Vite to reload
  and clear the in-memory session. Refreshed the snapshot and repeated the real upload.
- Whole-project release, full failure/late-response suite, 200% browser zoom and live
  deployment are not claimed. No blanket 58/58 Hallmark certification.
- Populated feedback: editing, clipboard read-back, skip/undo and draft retention across
  tab changes and Edit job description → Back to results passed against backend findings.
- Mobile suggestion dialogs measured full viewport at 320/375/414 × 844, and Escape
  dismissal passed at each width. Mobile PDF dialog opens a native-viewer link; in-place
  PDF editing is not provided. Final desktop, mobile overview and editor screenshots saved.
- Final npm run lint, npm run build and git diff --check passed after the mobile editor
  change. Browser console contained no runtime errors. No commit or push in this pass.
