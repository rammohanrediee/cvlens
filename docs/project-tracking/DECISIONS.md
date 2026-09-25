# AI Resume Analyzer — Decisions

## D01 — Repository authority

Use `rammohanrediee/AI-Resume-Analyzer`, explicitly confirmed by the user. The supplied local folder's different remote must not override this decision.

## D02 — Frontend

Accepted 2026-09-22: React + JavaScript + Vite. No TypeScript migration in the first release. Explain JavaScript/React concepts through implementation walkthroughs.

## D03 — Backend and transition

Target FastAPI with PostgreSQL-backed, privacy-minimized analytics. Preserve existing analysis behaviour and keep Streamlit working while the core React flow is built. Verify actual baseline before deciding exact migrations.

## D04 — Delivery pace

The two-month target is an outer deadline, not eight mandatory weeks of development. Complete one verified release at a time. Do not promise a finish date before reproducing the baseline.

## D05 — Ownership and positioning

Resume Analyzer is an open-source extension/re-architecture. Retain upstream attribution and distinguish new changes in contribution documentation. Never claim from-scratch authorship, invented usage, benchmark improvements or test results.

## D06 — Learning and implementation

Codex handles authorized Resume Analyzer implementation and mechanical checks; the user gets milestone walkthroughs and small useful inspection exercises. PeerMock's separate guided-build rules are not copied as implementation restrictions into this project.

## D07 — Headroom and progress

Use available Headroom compression for large outputs where helpful. Retrieve original details when needed for exact code reasoning. Never treat compression as a substitute for saved checkpoints or verified evidence. Do not claim the running desktop task is proxy-routed when it is not.

## D08 — Scope boundary

First React release: upload, job description, processing/error feedback, results/evidence/gaps, and report download. Defer new accounts, elaborate administration, microservices and extra AI features. Preserve privacy controls as functionality moves between components.

## D09 — Git and test discipline

User explicitly authorized implementation and GitHub pushes on 2026-09-22. Use the existing
main branch and coherent milestone commits; no unnecessary branches or tests. Durable
execution rules live in the repository-root AGENTS.md.

## D10 — Correct local checkout

Work in the confirmed Backend_project/ai_reseme_cloned_version/AI-Resume-Analyzer checkout. Origin
is the confirmed rammohanrediee repository; never push to upstream. The old checkout's
uncommitted matching changes remain preserved.

## D11 — HTTP migration

Preserve v1 URLs and success/error envelopes. Use Pydantic strict inputs and Uvicorn.
Synchronous analysis routes run in FastAPI's worker thread pool. Enforce actual streamed
JSON body size before parsing, retain optional API-key authentication, and emit only
sanitary operational metadata in request logs. The rate limiter is explicitly per process,
not a distributed guarantee. React authentication and deployment design remain later work.

## D12 — PDF extraction boundary and next priority

Reuse the existing native-PDF and OCR behaviour through `POST /api/v1/documents/extract`
instead of rebuilding the feature. The backend owns validation and processing, with a
5 MiB PDF limit, 20-page limit, five-page OCR limit, and 200,000-character output limit.
Streamlit remains compatible but now uses this API boundary. Build the React core flow
next; defer analytics/database restructuring until that flow works end to end.

## D14 — Replacement frontend design and scope (2026-09-22)

The user requested a plan and design.md before rebuilding React. Use React/JavaScript/Vite
for an in-memory analysis workspace with evidence filters, editable inputs, reruns and
latest-two-run comparison, reusing existing FastAPI analysis capabilities. Root design.md
specifies the supplied Mirage/Blaze Orange/Deep Sea Green/Wild Sand palette and responsive
workspace DNA. No template imagery, pricing or unrelated interview platform is included.
The prior React build was reverted in 8dfc143. This historical visual direction was
superseded by D15 when the user supplied the complete desktop/mobile reference set.

## D13 — Headroom privacy boundary

The user requested Headroom for longer tasks, but automatic approval review rejected
sending repository-derived implementation details to that external service. Do not export
private repository content through Headroom without approval that satisfies that review.
Use the repository checkpoint documents and concise local command output for continuity.

## D15 — Hallmark responsive redesign and product truth (2026-09-24)

Use a modern-minimal Hallmark Workbench with a cool-paper surface, restrained indigo accent,
Space Grotesk/IBM Plex Sans typography, an N1b product header, a three-column upload canvas,
and a split document/results workspace that stacks deliberately on mobile. Use original SVG
interface artwork and real backend data only. Preserve the FastAPI and Streamlit paths.

The screenshots are visual references, not permission to fabricate features. PDF upload,
optional job description, real analysis sections, replace-document flow, and PDF report
download are in scope. DOC/DOCX, cloud-drive imports, accounts/profile UI, dark mode,
Templates/Pricing/Resources/Job Match pages, and automatic rewritten-resume download remain
unsupported until a separate product and backend decision authorizes them.

## D16 — Product-workspace redesign (2026-09-24)
The user's attached brief supersedes D15 and the intermediate Garden/Long Document pass.
Keep green brand identity but move to neutral gray/white surfaces and sans-led product UI.
Use an analysis-first workbench, genuine tabs, expandable checks, on-demand PDF and local
draft edits with truthful limits. Rename visible UI to ResumeAI as requested in the brief.
Keep APIs and Streamlit unchanged. Do not fabricate account/product pages or apply/URL-import
capabilities. No production files are deleted; prior stylesheets remain unused.
