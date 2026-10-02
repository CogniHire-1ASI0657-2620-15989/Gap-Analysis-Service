from app.domain.model.aggregates.gap_report import GapReport
from app.interfaces.rest.resources.gap_report_resource import GapReportResource, SkillGapResource


class GapReportResourceFromEntityAssembler:
    @staticmethod
    def to_resource(report: GapReport) -> GapReportResource:
        skills = lambda values: [SkillGapResource(name=value.name, skill_type=value.skill_type) for value in values]
        return GapReportResource(
            id=report.id,
            job_id=report.job_id,
            job_title=report.job_title,
            job_description_snippet=report.job_description_snippet,
            match_percentage=report.match_percentage,
            matched_hard_skills=skills(report.matched_hard_skills),
            missing_hard_skills=skills(report.missing_hard_skills),
            matched_soft_skills=skills(report.matched_soft_skills),
            missing_soft_skills=skills(report.missing_soft_skills),
            analysis_source=report.analysis_source,
            analysis_status=report.analysis_status,
            analysis_engine=report.analysis_engine,
            created_at=report.created_at,
            updated_at=report.updated_at,
        )
