from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.configuration.settings import get_settings
from app.interfaces.rest.controller.gap_analysis_controller import router as gap_reports_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_settings()
    yield


app = FastAPI(
    title="Gap Analysis Service",
    description="Calculates deterministic job-profile compatibility reports.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(gap_reports_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"service": "gap-analysis", "status": "healthy"}
