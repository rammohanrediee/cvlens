"""Existing v1 workflows exposed through FastAPI."""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Response, UploadFile
from starlette.concurrency import run_in_threadpool

from ...core.resume_analysis import (
    analyze_bullet_quality,
    build_gap_explainer,
    build_pdf_report_bytes,
    generate_interview_prep,
)
from ...schemas.analysis import AnalysisRequest, AnalysisResponse, GapRequest, InterviewRequest, ResumeTextRequest
from ...services.analysis_service import analyze_resume
from ...services.pdf_extraction import MAX_PDF_BYTES, PDFExtractionError, extract_resume_text

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health():
    return {"data": {"status": "ok", "service": "cvlens-api", "version": "v1"}}


@router.post("/analyses", response_model=AnalysisResponse)
def analyze(body: AnalysisRequest):
    return analyze_resume(body)


@router.post("/documents/extract", response_model=AnalysisResponse)
async def extract_document(file: Annotated[UploadFile, File()]):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=415,
            detail={"code": "unsupported_media_type", "message": "Upload a PDF resume."},
        )
    content = await file.read(MAX_PDF_BYTES + 1)
    await file.close()
    try:
        extraction = await run_in_threadpool(extract_resume_text, content)
    except PDFExtractionError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail={"code": error.code, "message": error.message},
        ) from error
    return AnalysisResponse(data=extraction.to_dict())


@router.post("/analyses/bullet-quality", response_model=AnalysisResponse)
def bullet_quality(body: ResumeTextRequest):
    return AnalysisResponse(data=analyze_bullet_quality(body.resume_text))


@router.post("/analyses/jd-gap", response_model=AnalysisResponse)
def jd_gap(body: GapRequest):
    return AnalysisResponse(data=build_gap_explainer(body.job_description, body.resume_text, body.resume_skills))


@router.post("/analyses/interview-prep", response_model=AnalysisResponse)
def interview_prep(body: InterviewRequest):
    return AnalysisResponse(data=generate_interview_prep(body.job_description, body.resume_skills, body.role_title))


@router.post("/reports/pdf", response_class=Response, responses={200: {"content": {"application/pdf": {}}}})
def pdf_report(body: AnalysisRequest):
    report = build_pdf_report_bytes("Resume Analysis Report", analyze_resume(body).data)
    return Response(
        report,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="resume-analysis-report.pdf"'},
    )
