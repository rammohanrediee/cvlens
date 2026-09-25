"""Validated public API inputs; field names preserve the v1 client contract."""

from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

RequiredText = Annotated[str, Field(min_length=1)]


class ResumeTextRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    resume_text: RequiredText


class AnalysisRequest(ResumeTextRequest):
    candidate_name: str = "Candidate"
    resume_skills: list[str] = Field(default_factory=list)
    job_description: str = ""
    page_count: Annotated[int, Field(ge=1, le=100)] | None = None


class GapRequest(AnalysisRequest):
    job_description: RequiredText


class InterviewRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    job_description: RequiredText
    resume_skills: list[str] = Field(default_factory=list)
    role_title: str = "target role"


@dataclass(slots=True)
class AnalysisResponse:
    data: dict
