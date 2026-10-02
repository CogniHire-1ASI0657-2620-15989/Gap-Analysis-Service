from datetime import datetime

from pydantic import BaseModel


class SkillGapResource(BaseModel):
    name: str
    skill_type: str


class GapReportResource(BaseModel):
    id: int
    job_id: int
    job_title: str
    job_description_snippet: str | None = None
    match_percentage: int
    matched_hard_skills: list[SkillGapResource]
    missing_hard_skills: list[SkillGapResource]
    matched_soft_skills: list[SkillGapResource]
    missing_soft_skills: list[SkillGapResource]
    analysis_source: str
    analysis_status: str
    analysis_engine: str
    created_at: datetime
    updated_at: datetime
