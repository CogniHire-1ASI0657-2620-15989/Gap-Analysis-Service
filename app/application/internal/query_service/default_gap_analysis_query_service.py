from app.domain.model.aggregates.gap_report import GapReport
from app.domain.model.queries.get_gap_report_by_job_query import GetGapReportByJobQuery
from app.domain.model.queries.get_gap_reports_by_user_query import GetGapReportsByUserQuery
from app.domain.repositories.gap_report_repository import GapReportRepository
from app.domain.services.gap_analysis_query_service import GapAnalysisQueryService


class DefaultGapAnalysisQueryService(GapAnalysisQueryService):
    def __init__(self, repository: GapReportRepository):
        self._repository = repository

    async def handle_get_by_job(self, query: GetGapReportByJobQuery) -> GapReport | None:
        return await self._repository.find_by_user_and_job(query.user_id, query.job_id)

    async def handle_list_by_user(self, query: GetGapReportsByUserQuery) -> list[GapReport]:
        return await self._repository.find_by_user(query.user_id)
