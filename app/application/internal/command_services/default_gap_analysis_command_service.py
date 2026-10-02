from datetime import datetime, timezone

from app.application.ports.identity_profile_client import IdentityProfileClient
from app.application.ports.job_offer_client import JobOfferClient
from app.application.ports.llm_skill_extractor import LlmSkillExtractor, LlmUnavailable
from app.application.ports.match_calculation_strategy import MatchCalculationStrategy
from app.domain.model.aggregates.gap_report import GapReport
from app.domain.model.commands.generate_gap_report_command import GenerateGapReportCommand
from app.domain.repositories.gap_report_repository import GapReportRepository
from app.domain.repositories.skill_catalog_repository import SkillCatalogRepository
from app.domain.services.gap_analysis_command_service import GapAnalysisCommandService


class DefaultGapAnalysisCommandService(GapAnalysisCommandService):
    def __init__(self, profile_client: IdentityProfileClient, job_client: JobOfferClient, strategy: MatchCalculationStrategy, repository: GapReportRepository, skill_catalog_repository: SkillCatalogRepository, commit, llm_skill_extractor: LlmSkillExtractor | None = None):
        self._profile_client = profile_client
        self._job_client = job_client
        self._strategy = strategy
        self._repository = repository
        self._skill_catalog_repository = skill_catalog_repository
        self._llm_skill_extractor = llm_skill_extractor
        self._commit = commit

    async def handle_generate(self, command: GenerateGapReportCommand) -> GapReport:
        profile = await self._profile_client.get_job_profile(command.user_id)
        job = await self._job_client.get_job(command.user_id, command.job_id)
        catalog = await self._skill_catalog_repository.list_active()
        analysis_engine = "rule_based"
        try:
            required_skill_names = await self._llm_skill_extractor.extract_required_skills(job, catalog) if self._llm_skill_extractor else None
            if self._llm_skill_extractor:
                analysis_engine = "groq_llm"
        except LlmUnavailable:
            required_skill_names = None
            analysis_engine = "rule_based_fallback"
        result = self._strategy.calculate(profile, job, catalog, required_skill_names)
        now = datetime.now(timezone.utc)
        existing = await self._repository.find_by_user_and_job(command.user_id, command.job_id)
        report = GapReport(
            id=existing.id if existing else None,
            user_id=command.user_id,
            job_id=job.id,
            job_title=job.title,
            job_description_snippet=job.description_snippet,
            match_percentage=result.match_percentage,
            matched_hard_skills=result.matched_hard_skills,
            missing_hard_skills=result.missing_hard_skills,
            matched_soft_skills=result.matched_soft_skills,
            missing_soft_skills=result.missing_soft_skills,
            analysis_source="title_and_description_snippet",
            analysis_status=result.analysis_status,
            analysis_engine=analysis_engine,
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        saved = await self._repository.upsert(report)
        await self._commit()
        return saved
