from abc import ABC, abstractmethod

from app.domain.model.entities.skill_definition import SkillDefinition


class SkillCatalogRepository(ABC):
    @abstractmethod
    async def list_active(self) -> list[SkillDefinition]: ...
