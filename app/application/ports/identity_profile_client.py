from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateProfile:
    user_id: int
    hard_skills: list[dict]
    soft_skills: list[dict]


class IdentityProfileClient(ABC):
    @abstractmethod
    async def get_job_profile(self, user_id: int) -> CandidateProfile: ...
