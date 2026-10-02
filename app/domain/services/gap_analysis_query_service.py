from abc import ABC, abstractmethod

from app.domain.model.aggregates.gap_report import GapReport
from app.domain.model.queries.get_gap_report_by_job_query import GetGapReportByJobQuery
from app.domain.model.queries.get_gap_reports_by_user_query import GetGapReportsByUserQuery


class GapAnalysisQueryService(ABC):
    @abstractmethod
    async def handle_get_by_job(self, query: GetGapReportByJobQuery) -> GapReport | None: ...

    @abstractmethod
    async def handle_list_by_user(self, query: GetGapReportsByUserQuery) -> list[GapReport]: ...
