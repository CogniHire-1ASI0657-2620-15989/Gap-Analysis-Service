from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.model.entities.skill_definition import SkillDefinition
from app.domain.repositories.skill_catalog_repository import SkillCatalogRepository
from app.infrastructure.persistence.sqlalchemy.models.skill_definition_model import SkillDefinitionModel


class SQLAlchemySkillCatalogRepository(SkillCatalogRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_active(self) -> list[SkillDefinition]:
        result = await self._session.execute(
            select(SkillDefinitionModel).where(SkillDefinitionModel.is_active.is_(True)).order_by(SkillDefinitionModel.name)
        )
        return [
            SkillDefinition(id=model.id, name=model.name, skill_type=model.skill_type, aliases=model.aliases, is_active=model.is_active)
            for model in result.scalars().all()
        ]
