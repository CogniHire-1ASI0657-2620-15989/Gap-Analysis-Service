from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.infrastructure.persistence.sqlalchemy.database import Base


class GapReportModel(Base):
    __tablename__ = "gap_reports"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_gap_report_user_job"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    job_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    job_title: Mapped[str] = mapped_column(String(300), nullable=False)
    job_description_snippet: Mapped[str | None] = mapped_column(Text)
    match_percentage: Mapped[int] = mapped_column(Integer, nullable=False)
    matched_hard_skills: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    missing_hard_skills: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    matched_soft_skills: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    missing_soft_skills: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    analysis_source: Mapped[str] = mapped_column(String(100), nullable=False)
    analysis_status: Mapped[str] = mapped_column(String(100), nullable=False)
    analysis_engine: Mapped[str] = mapped_column(String(100), nullable=False, default="rule_based")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
