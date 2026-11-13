from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.internal.command_services.default_gap_analysis_command_service import DefaultGapAnalysisCommandService
from app.application.internal.query_service.default_gap_analysis_query_service import DefaultGapAnalysisQueryService
from app.dependencies import get_current_user_id, get_db_session, get_gap_analysis_command_service, get_gap_analysis_query_service, get_gap_report_publisher, get_redis_cache
from app.infrastructure.cache.redis_json_cache import RedisJsonCache
from app.infrastructure.messaging.gap_report_publisher import GapReportPublisher
from app.domain.model.queries.get_gap_report_by_job_query import GetGapReportByJobQuery
from app.domain.model.queries.get_gap_reports_by_user_query import GetGapReportsByUserQuery
from app.interfaces.rest.resources.gap_report_resource import GapReportResource
from app.interfaces.rest.resources.generate_gap_report_resource import GenerateGapReportResource
from app.interfaces.rest.transform.gap_report_resource_from_entity_assembler import GapReportResourceFromEntityAssembler
from app.interfaces.rest.transform.generate_gap_report_command_from_resource_assembler import GenerateGapReportCommandFromResourceAssembler


router = APIRouter(prefix="/api/v1/gap-reports", tags=["Gap Analysis"])


def _report_cache_key(user_id: int, job_id: int) -> str:
    return f"gap-analysis:v1:report:{user_id}:{job_id}"


@router.post("", response_model=GapReportResource, status_code=status.HTTP_201_CREATED)
async def generate_report(resource: GenerateGapReportResource, user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_db_session), cache: RedisJsonCache = Depends(get_redis_cache), publisher: GapReportPublisher = Depends(get_gap_report_publisher)) -> GapReportResource:
    service: DefaultGapAnalysisCommandService = get_gap_analysis_command_service(session)
    command = GenerateGapReportCommandFromResourceAssembler.to_command(user_id, resource)
    try:
        report = await service.handle_generate(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    response = GapReportResourceFromEntityAssembler.to_resource(report)
    cache_key = _report_cache_key(user_id, response.job_id)
    await cache.delete(cache_key)
    await cache.set(cache_key, response.model_dump(mode="json"), ttl_seconds=300)
    await publisher.publish(report)
    return response


@router.get("/{job_id}", response_model=GapReportResource)
async def get_report(job_id: int, user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_db_session), cache: RedisJsonCache = Depends(get_redis_cache)) -> GapReportResource:
    cache_key = _report_cache_key(user_id, job_id)
    cached = await cache.get(cache_key)
    if cached is not None:
        try:
            return GapReportResource.model_validate(cached)
        except ValidationError:
            await cache.delete(cache_key)
    service: DefaultGapAnalysisQueryService = get_gap_analysis_query_service(session)
    report = await service.handle_get_by_job(GetGapReportByJobQuery(user_id=user_id, job_id=job_id))
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gap report not found.")
    response = GapReportResourceFromEntityAssembler.to_resource(report)
    await cache.set(cache_key, response.model_dump(mode="json"), ttl_seconds=300)
    return response


@router.get("", response_model=list[GapReportResource])
async def list_reports(user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_db_session)) -> list[GapReportResource]:
    service: DefaultGapAnalysisQueryService = get_gap_analysis_query_service(session)
    reports = await service.handle_list_by_user(GetGapReportsByUserQuery(user_id=user_id))
    return [GapReportResourceFromEntityAssembler.to_resource(report) for report in reports]
