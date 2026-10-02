import httpx

from app.application.ports.identity_profile_client import CandidateProfile, IdentityProfileClient


class IdentityServiceClient(IdentityProfileClient):
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    async def get_job_profile(self, user_id: int) -> CandidateProfile:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(1.0)) as client:
                response = await client.get(f"{self._base_url}/api/v1/internal/users/{user_id}/job-profile")
            if response.status_code == 404:
                raise ValueError("User profile not found.")
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("Identity Service is unavailable.") from exc
        return CandidateProfile(
            user_id=int(body["id"]),
            hard_skills=list(body.get("hard_skills") or []),
            soft_skills=list(body.get("soft_skills") or []),
        )
