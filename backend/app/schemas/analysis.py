"""Validated public API inputs; field names preserve the v1 client contract."""

from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

MAX_RESUME_CHARACTERS = 200_000
MAX_JOB_DESCRIPTION_CHARACTERS = 50_000
MAX_RESUME_SKILLS = 100
MAX_SKILL_CHARACTERS = 100
MAX_NAME_CHARACTERS = 200

ResumeText = Annotated[str, Field(min_length=1, max_length=MAX_RESUME_CHARACTERS)]
RequiredJobDescription = Annotated[str, Field(min_length=1, max_length=MAX_JOB_DESCRIPTION_CHARACTERS)]
OptionalJobDescription = Annotated[str, Field(max_length=MAX_JOB_DESCRIPTION_CHARACTERS)]
SkillText = Annotated[str, Field(min_length=1, max_length=MAX_SKILL_CHARACTERS)]
SkillList = Annotated[list[SkillText], Field(max_length=MAX_RESUME_SKILLS)]
ShortText = Annotated[str, Field(max_length=MAX_NAME_CHARACTERS)]


class ResumeTextRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    resume_text: ResumeText


class AnalysisRequest(ResumeTextRequest):
    candidate_name: ShortText = ""
    resume_skills: SkillList = Field(default_factory=list)
    job_description: OptionalJobDescription = ""
    page_count: Annotated[int, Field(ge=1, le=20)] | None = None
    use_ai_analysis: bool = False


class GapRequest(AnalysisRequest):
    job_description: RequiredJobDescription


class InterviewRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    job_description: RequiredJobDescription
    resume_skills: SkillList = Field(default_factory=list)
    role_title: ShortText = "target role"


@dataclass(slots=True)
class AnalysisResponse:
    data: dict
