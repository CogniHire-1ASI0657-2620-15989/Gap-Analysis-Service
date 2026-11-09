import os
import re
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
    internal_api_key: str
    database_schema: str


@lru_cache
def get_settings() -> Settings:
    values = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "IDENTITY_SERVICE_URL": os.getenv("IDENTITY_SERVICE_URL"),
        "JOB_DISCOVERY_SERVICE_URL": os.getenv("JOB_DISCOVERY_SERVICE_URL"),
        "GATEWAY_USER_ID_HEADER": os.getenv("GATEWAY_USER_ID_HEADER"),
        "INTERNAL_API_KEY": os.getenv("INTERNAL_API_KEY"),
    }
    missing = [name for name, value in values.items() if not value or not value.strip()]
    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")
    database_schema = os.getenv("DATABASE_SCHEMA", "gap_analysis").strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", database_schema):
        raise RuntimeError("DATABASE_SCHEMA must be a valid PostgreSQL identifier.")

    return Settings(
        database_url=values["DATABASE_URL"].strip(),
        identity_service_url=values["IDENTITY_SERVICE_URL"].rstrip("/"),
        job_discovery_service_url=values["JOB_DISCOVERY_SERVICE_URL"].rstrip("/"),
        groq_api_key=os.getenv("GROQ_API_KEY") or None,
        groq_model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip(),
        gateway_user_id_header=values["GATEWAY_USER_ID_HEADER"].strip(),
        internal_api_key=values["INTERNAL_API_KEY"].strip(),
        database_schema=database_schema,
    )
