import json

import httpx

from app.application.ports.job_offer_client import JobOffer
from app.application.ports.llm_skill_extractor import LlmSkillExtractor, LlmUnavailable
from app.domain.model.entities.skill_definition import SkillDefinition


class GroqLlmSkillExtractor(LlmSkillExtractor):
    _URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str, model: str):
        self._api_key = api_key
        self._model = model

    async def extract_required_skills(self, job: JobOffer, catalog: list[SkillDefinition]) -> list[str]:
        allowed_skills = [skill.name for skill in catalog]
        payload = {
            "model": self._model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": "Extract only skills explicitly required or strongly implied by the job text. Return only names from the supplied catalog. Do not infer years of experience, salary, education, or skills outside the catalog.",
                },
                {
                    "role": "user",
                    "content": f"Catalog: {json.dumps(allowed_skills, ensure_ascii=False)}\nJob title: {job.title}\nJob snippet: {job.description_snippet or ''}",
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "required_skills",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {"required_skills": {"type": "array", "items": {"type": "string", "enum": allowed_skills}}},
                        "required": ["required_skills"],
                        "additionalProperties": False,
                    },
                },
            },
        }
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(3.0)) as client:
                response = await client.post(self._URL, headers={"Authorization": f"Bearer {self._api_key}"}, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            extracted = json.loads(content)["required_skills"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise LlmUnavailable("Groq did not return a valid skill extraction.") from exc
        return [name for name in extracted if name in allowed_skills]
