from app.domain.model.commands.generate_gap_report_command import GenerateGapReportCommand
from app.interfaces.rest.resources.generate_gap_report_resource import GenerateGapReportResource


class GenerateGapReportCommandFromResourceAssembler:
    @staticmethod
    def to_command(user_id: int, resource: GenerateGapReportResource) -> GenerateGapReportCommand:
        return GenerateGapReportCommand(user_id=user_id, job_id=resource.job_id)
