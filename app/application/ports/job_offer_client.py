from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class JobOffer:
    id: int
    title: str
    description_snippet: str | None


class JobOfferClient(ABC):
    @abstractmethod
    async def get_job(self, user_id: int, job_id: int) -> JobOffer: ...
