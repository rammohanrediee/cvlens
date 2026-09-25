from dataclasses import dataclass


@dataclass(slots=True)
class AnalysisRecord:
    """Persistable metadata for one resume analysis."""

    candidate_name: str
    resume_score: int | None = None
    predicted_field: str | None = None
