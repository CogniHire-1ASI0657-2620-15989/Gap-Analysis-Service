import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    identity_service_url: str
    job_discovery_service_url: str
    groq_api_key: str | None
    groq_model: str
    gateway_user_id_header: str


@lru_cache
def get_settings() -> Settings:
    values = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "IDENTITY_SERVICE_URL": os.getenv("IDENTITY_SERVICE_URL"),
        "JOB_DISCOVERY_SERVICE_URL": os.getenv("JOB_DISCOVERY_SERVICE_URL"),
        "GATEWAY_USER_ID_HEADER": os.getenv("GATEWAY_USER_ID_HEADER"),
    }
    missing = [name for name, value in values.items() if not value or not value.strip()]
    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")
    return Settings(
        database_url=values["DATABASE_URL"].strip(),
        identity_service_url=values["IDENTITY_SERVICE_URL"].rstrip("/"),
        job_discovery_service_url=values["JOB_DISCOVERY_SERVICE_URL"].rstrip("/"),
        groq_api_key=os.getenv("GROQ_API_KEY") or None,
        groq_model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip(),
        gateway_user_id_header=values["GATEWAY_USER_ID_HEADER"].strip(),
    )
