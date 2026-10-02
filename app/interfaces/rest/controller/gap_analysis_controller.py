from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.internal.command_services.default_gap_analysis_command_service import DefaultGapAnalysisCommandService
from app.application.internal.query_service.default_gap_analysis_query_service import DefaultGapAnalysisQueryService
from app.dependencies import get_current_user_id, get_db_session, get_gap_analysis_command_service, get_gap_analysis_query_service
from app.domain.model.queries.get_gap_report_by_job_query import GetGapReportByJobQuery
from app.domain.model.queries.get_gap_reports_by_user_query import GetGapReportsByUserQuery
from app.interfaces.rest.resources.gap_report_resource import GapReportResource
from app.interfaces.rest.resources.generate_gap_report_resource import GenerateGapReportResource
from app.interfaces.rest.transform.gap_report_resource_from_entity_assembler import GapReportResourceFromEntityAssembler
from app.interfaces.rest.transform.generate_gap_report_command_from_resource_assembler import GenerateGapReportCommandFromResourceAssembler


router = APIRouter(prefix="/api/v1/gap-reports", tags=["Gap Analysis"])


@router.post("", response_model=GapReportResource, status_code=status.HTTP_201_CREATED)
async def generate_report(resource: GenerateGapReportResource, user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_db_session)) -> GapReportResource:
    service: DefaultGapAnalysisCommandService = get_gap_analysis_command_service(session)
    command = GenerateGapReportCommandFromResourceAssembler.to_command(user_id, resource)
    try:
        report = await service.handle_generate(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    return GapReportResourceFromEntityAssembler.to_resource(report)


@router.get("/{job_id}", response_model=GapReportResource)
async def get_report(job_id: int, user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_db_session)) -> GapReportResource:
    service: DefaultGapAnalysisQueryService = get_gap_analysis_query_service(session)
    report = await service.handle_get_by_job(GetGapReportByJobQuery(user_id=user_id, job_id=job_id))
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gap report not found.")
    return GapReportResourceFromEntityAssembler.to_resource(report)


@router.get("", response_model=list[GapReportResource])
async def list_reports(user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_db_session)) -> list[GapReportResource]:
    service: DefaultGapAnalysisQueryService = get_gap_analysis_query_service(session)
    reports = await service.handle_list_by_user(GetGapReportsByUserQuery(user_id=user_id))
    return [GapReportResourceFromEntityAssembler.to_resource(report) for report in reports]
