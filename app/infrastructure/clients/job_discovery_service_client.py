import httpx

from app.application.ports.job_offer_client import JobOffer, JobOfferClient


class JobDiscoveryServiceClient(JobOfferClient):
    def __init__(self, base_url: str, user_id_header: str):
        self._base_url = base_url.rstrip("/")
        self._user_id_header = user_id_header

    async def get_job(self, user_id: int, job_id: int) -> JobOffer:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(1.0)) as client:
                response = await client.get(
                    f"{self._base_url}/api/v1/jobs/{job_id}",
                    headers={self._user_id_header: str(user_id)},
                )
            if response.status_code == 404:
                raise ValueError("Job offer not found.")
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("Job Discovery Service is unavailable.") from exc
        return JobOffer(
            id=int(body["id"]),
            title=str(body["title"]),
            description_snippet=body.get("description_snippet"),
        )
