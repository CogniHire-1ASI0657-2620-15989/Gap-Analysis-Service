from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateGapReportCommand:
    user_id: int
    job_id: int
