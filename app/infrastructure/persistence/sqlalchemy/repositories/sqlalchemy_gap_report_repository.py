from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.model.aggregates.gap_report import GapReport
from app.domain.model.value_objects.skill_gap import SkillGap
from app.domain.repositories.gap_report_repository import GapReportRepository
from app.infrastructure.persistence.sqlalchemy.models.gap_report_model import GapReportModel


class SQLAlchemyGapReportRepository(GapReportRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, report: GapReport) -> GapReport:
        model = None
        if report.id is not None:
            model = await self._session.get(GapReportModel, report.id)
        if model is None:
            model = GapReportModel(user_id=report.user_id, job_id=report.job_id)
            self._session.add(model)
        self._copy_to_model(report, model)
        await self._session.flush()
        return self._to_entity(model)

    async def find_by_user_and_job(self, user_id: int, job_id: int) -> GapReport | None:
        result = await self._session.execute(select(GapReportModel).where(GapReportModel.user_id == user_id, GapReportModel.job_id == job_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_user(self, user_id: int) -> list[GapReport]:
        result = await self._session.execute(select(GapReportModel).where(GapReportModel.user_id == user_id).order_by(GapReportModel.updated_at.desc()))
        return [self._to_entity(model) for model in result.scalars().all()]

    @staticmethod
    def _copy_to_model(report: GapReport, model: GapReportModel) -> None:
        model.job_title = report.job_title
        model.job_description_snippet = report.job_description_snippet
        model.match_percentage = report.match_percentage
        model.matched_hard_skills = [item.__dict__ for item in report.matched_hard_skills]
        model.missing_hard_skills = [item.__dict__ for item in report.missing_hard_skills]
        model.matched_soft_skills = [item.__dict__ for item in report.matched_soft_skills]
        model.missing_soft_skills = [item.__dict__ for item in report.missing_soft_skills]
        model.analysis_source = report.analysis_source
        model.analysis_status = report.analysis_status
        model.analysis_engine = report.analysis_engine
        model.created_at = report.created_at
        model.updated_at = report.updated_at

    @staticmethod
    def _to_entity(model: GapReportModel) -> GapReport:
        skills = lambda values: [SkillGap(**value) for value in values]
        return GapReport(model.id, model.user_id, model.job_id, model.job_title, model.job_description_snippet, model.match_percentage, skills(model.matched_hard_skills), skills(model.missing_hard_skills), skills(model.matched_soft_skills), skills(model.missing_soft_skills), model.analysis_source, model.analysis_status, model.analysis_engine, model.created_at, model.updated_at)
