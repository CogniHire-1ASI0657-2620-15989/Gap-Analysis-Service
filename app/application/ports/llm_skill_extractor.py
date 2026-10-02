from abc import ABC, abstractmethod

from app.application.ports.job_offer_client import JobOffer
from app.domain.model.entities.skill_definition import SkillDefinition


class LlmUnavailable(Exception):
    """Raised when the optional LLM provider cannot return a valid response."""


class LlmSkillExtractor(ABC):
    @abstractmethod
    async def extract_required_skills(self, job: JobOffer, catalog: list[SkillDefinition]) -> list[str]: ...
