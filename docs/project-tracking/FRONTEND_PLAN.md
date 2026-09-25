# React frontend plan

Status: Phases 1 and 2 implemented locally, 2026-09-24. Phase 3 and the remaining
Phase 4 verification are still open.
The previous React implementation was removed in `8dfc143`; the replacement follows the
functional product-workspace design in `../../design.md`. The intermediate Long Document layout was explicitly superseded by the user's attached redesign brief.

## What React adds
React owns a single browser session across input editing, analysis views, filtering and
repeat runs. FastAPI remains responsible for extraction, scoring and report generation.
React is useful here because these interactions share state; it is not a prerequisite
for analysis and does not improve the scoring algorithm by itself.

| Capability | Existing behavior | Planned React addition |
| --- | --- | --- |
| PDF/OCR extraction | Backend upload endpoint, bounded files/pages | Upload validation, filename/size, extraction warnings, replace document and retry |
| Resume/JD analysis | Existing analyses endpoint and Streamlit form | Preserve draft inputs when changing sections; edit JD without re-extracting the same PDF |
| Scores and ATS checks | Existing summary and section checks | Explain each score, expand its breakdown; show unavailable scores as unavailable |
| Requirement evidence and gaps | Existing evidence, gap and semantic outputs | Search/filter requirements, select a requirement to inspect supporting text, separate missing from unavailable |
| Bullet feedback | Existing bullet-quality analysis | Filter feedback, inspect source bullet and guidance, copy guidance with accessible confirmation |
| Interview prompts and learning resources | Existing prompts and course recommendations | Group prompts by skill/topic where provided; keep resources secondary |
| Repeat analysis | Existing processing callable again | Retain latest two successful snapshots in memory and compare score/check/gap changes |
| PDF report | Existing report endpoint | Explicit download state, retry, attach report to the intended analysis inputs |

## Session behavior
1. Upload PDF, paste optional JD (required for JD-specific views), then Analyze.
2. Display actual extraction and analysis phases; prevent duplicate submission.
3. Read Overview, ATS Check, Suggestions and Keywords without losing the PDF or JD.
4. Edit inputs and re-analyze. Unchanged PDF reuses extracted text; replacing it invalidates extraction.
5. A successful run becomes current and the previous successful run becomes comparison baseline. A failed run never overwrites a good result.
6. Compare only equivalent metric fields. If JD or resume changed, show that context; JD changes are not evidence of resume improvement. Missing metrics have no numeric delta.
7. Reset clears document, extracted text, drafts, snapshots and object URLs. Refresh ends the session; explain this before users rely on persistence.

Use a reducer/context for the modest shared state; no Redux dependency needed. Keep PDF
bytes/text/JD/results in memory only. Do not store raw resumes in localStorage or analytics.
Abort or ignore superseded requests; a late response must not replace a newer result.
Browser-side abort does not guarantee server-side computation stopped.

## API and honest limitations
Reuse `/api/v1/documents/extract`, `/analyses`, `/analyses/bullet-quality`, `/analyses/jd-gap`,
`/analyses/interview-prep`, `/reports/pdf` and `/health`; request only what each interaction needs.
Reuse fields from the main analysis instead of refetching when available. Check actual schemas before implementation.
The report endpoint currently recomputes from inputs: do not promise a byte-for-byte or
exact historical snapshot export. If exact snapshot export becomes required, plan a separate validated backend change.
Scores are heuristic structure checks / semantic similarities, not hiring predictions or guaranteed ATS acceptance.
No shared API secret in browser bundles. Use same-origin routing/proxy for local and deployed operation; resolve any protected deployment access before release.

## Delivery sequence and done gates
- Phase 1: responsive input workspace + API boundary + session state. Gate: real PDF upload → extraction → analysis; invalid PDF, missing JD and offline behavior are clear.
- Phase 2: result sections, evidence-backed keyword gaps, improvement guidance and report download. Gate: actual backend data, missing-model fallback and download checked.
- Phase 3: edit/re-run and two-result comparison. Gate: changing JD needs no re-upload, PDF replacement refreshes extraction, failed/late responses preserve the valid result, Reset clears state.
- Phase 4: browser verification and release integration. Gate: widths from design.md, keyboard and zoom checks, production build/lint, meaningful session regression checks, Streamlit still starts.

Use existing main; no unnecessary branches or test scaffolding. Add focused tests for
session invalidation, stale responses and comparison correctness only when implementing those behaviors.
Update the canonical trackers after each phase and show the user the first rendered screen
before expanding its visual pattern across all result views.

## Scope limits
Keep original Streamlit intact through the transition. No resume builder, real-time mock
interviews, jobs marketplace, accounts, billing, activity dashboard, persistent history,
new AI provider or fabricated performance metrics in this frontend milestone.
Analytics/database migration remains separate unfinished backend work.
The responsive input workspace, API health state, bounded PDF validation, extraction reuse,
stale-request protection, four real-data result sections and PDF report download are
implemented. Advanced evidence filtering, interview-prep grouping, two-run comparison,
repeated/failure/late-response and zoom verification, and release integration remain planned.

## 2026-09-24 product-workspace update
The analysis views are exclusive keyboard-operable tabs, not long-document anchor links.
ATS checks use grouped disclosures. Suggestion drafts support editing/copying and skip/undo;
these are local text drafts, not PDF editing. Desktop context is secondary, not a permanent
50/50 PDF split. Two-run comparison and advanced filtering remain future work.
