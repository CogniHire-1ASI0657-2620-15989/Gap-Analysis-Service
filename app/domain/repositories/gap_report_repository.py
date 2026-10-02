from abc import ABC, abstractmethod

from app.domain.model.aggregates.gap_report import GapReport


class GapReportRepository(ABC):
    @abstractmethod
    async def upsert(self, report: GapReport) -> GapReport: ...

    @abstractmethod
    async def find_by_user_and_job(self, user_id: int, job_id: int) -> GapReport | None: ...

    @abstractmethod
    async def find_by_user(self, user_id: int) -> list[GapReport]: ...
