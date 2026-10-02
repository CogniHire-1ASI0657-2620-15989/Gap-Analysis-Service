from abc import ABC, abstractmethod

from app.domain.model.aggregates.gap_report import GapReport
from app.domain.model.commands.generate_gap_report_command import GenerateGapReportCommand


class GapAnalysisCommandService(ABC):
    @abstractmethod
    async def handle_generate(self, command: GenerateGapReportCommand) -> GapReport: ...
