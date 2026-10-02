from collections.abc import AsyncGenerator

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.internal.command_services.default_gap_analysis_command_service import DefaultGapAnalysisCommandService
from app.application.internal.query_service.default_gap_analysis_query_service import DefaultGapAnalysisQueryService
from app.infrastructure.clients.identity_service_client import IdentityServiceClient
from app.infrastructure.clients.job_discovery_service_client import JobDiscoveryServiceClient
from app.infrastructure.clients.groq_llm_skill_extractor import GroqLlmSkillExtractor
from app.infrastructure.configuration.settings import get_settings
from app.infrastructure.matching.rule_based_skill_strategy import RuleBasedSkillStrategy
from app.infrastructure.persistence.sqlalchemy.database import get_session
from app.infrastructure.persistence.sqlalchemy.repositories.sqlalchemy_gap_report_repository import SQLAlchemyGapReportRepository
from app.infrastructure.persistence.sqlalchemy.repositories.sqlalchemy_skill_catalog_repository import SQLAlchemySkillCatalogRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_current_user_id(request: Request) -> int:
    header = get_settings().gateway_user_id_header
    raw_user_id = request.headers.get(header)
    if raw_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Missing gateway identity header: {header}")
    try:
        user_id = int(raw_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid gateway user identifier.") from exc
    if user_id <= 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid gateway user identifier.")
    return user_id


def get_gap_analysis_command_service(session: AsyncSession) -> DefaultGapAnalysisCommandService:
    settings = get_settings()
    llm_skill_extractor = GroqLlmSkillExtractor(settings.groq_api_key, settings.groq_model) if settings.groq_api_key else None
    return DefaultGapAnalysisCommandService(
        profile_client=IdentityServiceClient(settings.identity_service_url),
        job_client=JobDiscoveryServiceClient(settings.job_discovery_service_url, settings.gateway_user_id_header),
        strategy=RuleBasedSkillStrategy(),
        repository=SQLAlchemyGapReportRepository(session),
        skill_catalog_repository=SQLAlchemySkillCatalogRepository(session),
        llm_skill_extractor=llm_skill_extractor,
        commit=session.commit,
    )


def get_gap_analysis_query_service(session: AsyncSession) -> DefaultGapAnalysisQueryService:
    return DefaultGapAnalysisQueryService(SQLAlchemyGapReportRepository(session))
