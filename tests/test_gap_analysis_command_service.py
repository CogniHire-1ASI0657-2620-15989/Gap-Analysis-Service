from datetime import datetime, timezone

import pytest

from app.application.internal.command_services.default_gap_analysis_command_service import (
    DefaultGapAnalysisCommandService,
)
from app.application.ports.identity_profile_client import CandidateProfile
from app.application.ports.job_offer_client import JobOffer
from app.application.ports.llm_skill_extractor import LlmUnavailable
from app.domain.model.aggregates.gap_report import GapReport
from app.domain.model.commands.generate_gap_report_command import GenerateGapReportCommand
from app.domain.model.entities.skill_definition import SkillDefinition
from app.infrastructure.matching.rule_based_skill_strategy import RuleBasedSkillStrategy

pytestmark = pytest.mark.asyncio

CREATED_AT = datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc)

EXISTING_REPORT = GapReport(
    id=7,
    user_id=1,
    job_id=10,
    job_title="Desarrollador Python",
    job_description_snippet=None,
    match_percentage=100,
    matched_hard_skills=[],
    missing_hard_skills=[],
    matched_soft_skills=[],
    missing_soft_skills=[],
    analysis_source="title_and_description_snippet",
    analysis_status="completed",
    analysis_engine="rule_based",
    created_at=CREATED_AT,
    updated_at=CREATED_AT,
)


class ProfileClientStub:
    async def get_job_profile(self, user_id: int) -> CandidateProfile:
        return CandidateProfile(
            user_id=user_id,
            hard_skills=[{"name": "Python"}],
            soft_skills=[],
        )


class JobClientStub:
    async def get_job(self, user_id: int, job_id: int) -> JobOffer:
        return JobOffer(
            id=job_id,
            title="Desarrollador Python",
            description_snippet="Experiencia con Python y FastAPI.",
        )


class SkillCatalogStub:
    async def list_active(self) -> list[SkillDefinition]:
        return [
            SkillDefinition(1, "Python", "hard", ["python"]),
            SkillDefinition(2, "FastAPI", "hard", ["fastapi"]),
        ]


class UnavailableLlmStub:
    async def extract_required_skills(self, job, catalog):
        raise LlmUnavailable()


class GapReportRepositoryStub:
    def __init__(self, existing: GapReport | None) -> None:
        self._existing = existing
        self.upsert_calls: list[GapReport] = []

    async def find_by_user_and_job(self, user_id: int, job_id: int):
        return self._existing

    async def find_by_user(self, user_id: int):
        return [self._existing] if self._existing else []

    async def upsert(self, report: GapReport) -> GapReport:
        self.upsert_calls.append(report)
        return GapReport(**{**report.__dict__, "id": report.id or 1})


async def commit():
    return None


async def test_handle_generate_falls_back_to_rule_based_when_llm_is_unavailable():
    # Arrange
    repository = GapReportRepositoryStub(existing=EXISTING_REPORT)
    service = DefaultGapAnalysisCommandService(
        profile_client=ProfileClientStub(),
        job_client=JobClientStub(),
        strategy=RuleBasedSkillStrategy(),
        repository=repository,
        skill_catalog_repository=SkillCatalogStub(),
        commit=commit,
        llm_skill_extractor=UnavailableLlmStub(),
    )
    command = GenerateGapReportCommand(user_id=1, job_id=10)

    # Act
    report = await service.handle_generate(command)

    # Assert
    assert report.analysis_engine == "rule_based_fallback"
    assert report.analysis_status == "completed"
    assert report.match_percentage == 50
    assert [skill.name for skill in report.matched_hard_skills] == ["Python"]
    assert [skill.name for skill in report.missing_hard_skills] == ["FastAPI"]
    assert report.created_at == CREATED_AT
    assert report.updated_at >= report.created_at
    assert len(repository.upsert_calls) == 1
