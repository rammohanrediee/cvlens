from ..core.resume_analysis import build_api_payload

from ..schemas.analysis import AnalysisRequest, AnalysisResponse


def analyze_resume(request: AnalysisRequest) -> AnalysisResponse:
    return AnalysisResponse(
        data=build_api_payload(
            resume_text=request.resume_text,
            resume_skills=request.resume_skills,
            job_description=request.job_description,
            candidate_name=request.candidate_name,
            page_count=request.page_count,
            use_ai_analysis=request.use_ai_analysis,
        )
    )
