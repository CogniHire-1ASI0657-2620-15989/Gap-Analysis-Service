from dataclasses import dataclass


@dataclass(frozen=True)
class GetGapReportsByUserQuery:
    user_id: int
