from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.application.ports.identity_profile_client import CandidateProfile
from app.application.ports.job_offer_client import JobOffer
from app.domain.model.entities.skill_definition import SkillDefinition
from app.domain.model.value_objects.skill_gap import SkillGap


@dataclass(frozen=True)
class MatchCalculationResult:
    match_percentage: int
    matched_hard_skills: list[SkillGap]
    missing_hard_skills: list[SkillGap]
    matched_soft_skills: list[SkillGap]
    missing_soft_skills: list[SkillGap]
    analysis_status: str


class MatchCalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, profile: CandidateProfile, job: JobOffer, catalog: list[SkillDefinition], required_skill_names: list[str] | None = None) -> MatchCalculationResult: ...
