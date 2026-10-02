"""create gap report tables

Revision ID: 20260929_01
Revises:
Create Date: 2026-09-29
"""
from alembic import op
import sqlalchemy as sa


revision = "20260929_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gap_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("job_title", sa.String(length=300), nullable=False),
        sa.Column("job_description_snippet", sa.Text()),
        sa.Column("match_percentage", sa.Integer(), nullable=False),
        sa.Column("matched_hard_skills", sa.JSON(), nullable=False),
        sa.Column("missing_hard_skills", sa.JSON(), nullable=False),
        sa.Column("matched_soft_skills", sa.JSON(), nullable=False),
        sa.Column("missing_soft_skills", sa.JSON(), nullable=False),
        sa.Column("analysis_source", sa.String(length=100), nullable=False),
        sa.Column("analysis_status", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "job_id", name="uq_gap_report_user_job"),
    )
    op.create_index("ix_gap_reports_user_id", "gap_reports", ["user_id"])
    op.create_index("ix_gap_reports_job_id", "gap_reports", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_gap_reports_job_id", table_name="gap_reports")
    op.drop_index("ix_gap_reports_user_id", table_name="gap_reports")
    op.drop_table("gap_reports")
