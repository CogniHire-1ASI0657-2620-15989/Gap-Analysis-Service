from app.application.ports.identity_profile_client import CandidateProfile
from app.application.ports.job_offer_client import JobOffer
from app.domain.model.entities.skill_definition import SkillDefinition
from app.infrastructure.matching.rule_based_skill_strategy import RuleBasedSkillStrategy


CATALOG = [
    SkillDefinition(1, "Python", "hard", ["python"]),
    SkillDefinition(2, "FastAPI", "hard", ["fastapi"]),
    SkillDefinition(3, "PostgreSQL", "hard", ["postgresql", "postgres"]),
    SkillDefinition(4, "AWS", "hard", ["aws"]),
    SkillDefinition(5, "Trabajo en equipo", "soft", ["trabajo en equipo"]),
]


def test_calculates_match_and_missing_skills() -> None:
    profile = CandidateProfile(
        user_id=1,
        hard_skills=[{"name": "Python"}, {"name": "Postgres"}],
        soft_skills=[{"name": "Comunicación"}],
    )
    job = JobOffer(1, "Backend Developer", "Python, FastAPI, PostgreSQL, AWS y trabajo en equipo.")

    result = RuleBasedSkillStrategy().calculate(profile, job, CATALOG)

    assert result.match_percentage == 40
    assert [skill.name for skill in result.matched_hard_skills] == ["Python", "PostgreSQL"]
    assert [skill.name for skill in result.missing_hard_skills] == ["FastAPI", "AWS"]
    assert [skill.name for skill in result.missing_soft_skills] == ["Trabajo en equipo"]
    assert result.analysis_status == "completed"


def test_marks_report_when_job_has_no_catalog_skills() -> None:
    profile = CandidateProfile(user_id=1, hard_skills=[], soft_skills=[])
    job = JobOffer(1, "Especialista", "Una posición con requisitos no estructurados.")

    result = RuleBasedSkillStrategy().calculate(profile, job, CATALOG)

    assert result.match_percentage == 0
    assert result.analysis_status == "insufficient_job_data"
