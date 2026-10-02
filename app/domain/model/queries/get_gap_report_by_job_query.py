from dataclasses import dataclass


@dataclass(frozen=True)
class GetGapReportByJobQuery:
    user_id: int
    job_id: int
