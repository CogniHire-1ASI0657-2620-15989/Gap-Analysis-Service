import re
import unicodedata

from app.application.ports.identity_profile_client import CandidateProfile
from app.application.ports.job_offer_client import JobOffer
from app.application.ports.match_calculation_strategy import MatchCalculationResult, MatchCalculationStrategy
from app.domain.model.entities.skill_definition import SkillDefinition
from app.domain.model.value_objects.skill_gap import SkillGap


class RuleBasedSkillStrategy(MatchCalculationStrategy):
    def calculate(self, profile: CandidateProfile, job: JobOffer, catalog: list[SkillDefinition], required_skill_names: list[str] | None = None) -> MatchCalculationResult:
        job_text = self._normalize(f"{job.title} {job.description_snippet or ''}")
        if required_skill_names is None:
            required = [skill for skill in catalog if any(self._contains(job_text, alias) for alias in skill.aliases)]
        else:
            required_names = set(required_skill_names)
            required = [skill for skill in catalog if skill.name in required_names]
        if not required:
            return MatchCalculationResult(0, [], [], [], [], "insufficient_job_data")

        profile_skills = {self._normalize(str(item.get("name", ""))) for item in profile.hard_skills + profile.soft_skills}
        matched, missing = [], []
        for skill in required:
            gap = SkillGap(name=skill.name, skill_type=skill.skill_type)
            aliases = {self._normalize(alias) for alias in skill.aliases} | {self._normalize(skill.name)}
            (matched if aliases & profile_skills else missing).append(gap)

        percentage = round(len(matched) * 100 / len(required))
        return MatchCalculationResult(
            percentage,
            [item for item in matched if item.skill_type == "hard"],
            [item for item in missing if item.skill_type == "hard"],
            [item for item in matched if item.skill_type == "soft"],
            [item for item in missing if item.skill_type == "soft"],
            "completed",
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return "".join(char for char in unicodedata.normalize("NFD", value.lower()) if unicodedata.category(char) != "Mn")

    @classmethod
    def _contains(cls, text: str, alias: str) -> bool:
        return bool(re.search(rf"(?<!\w){re.escape(cls._normalize(alias))}(?!\w)", text))
