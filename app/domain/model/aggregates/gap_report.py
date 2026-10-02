from dataclasses import dataclass
from datetime import datetime

from app.domain.model.value_objects.skill_gap import SkillGap


@dataclass
class GapReport:
    id: int | None
    user_id: int
    job_id: int
    job_title: str
    job_description_snippet: str | None
    match_percentage: int
    matched_hard_skills: list[SkillGap]
    missing_hard_skills: list[SkillGap]
    matched_soft_skills: list[SkillGap]
    missing_soft_skills: list[SkillGap]
    analysis_source: str
    analysis_status: str
    analysis_engine: str
    created_at: datetime
    updated_at: datetime
