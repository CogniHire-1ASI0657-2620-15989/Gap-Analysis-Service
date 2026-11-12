from contextlib import asynccontextmanager
from secrets import compare_digest

from fastapi import FastAPI, Request

from app.infrastructure.configuration.settings import get_settings
from app.interfaces.rest.controller.gap_analysis_controller import router as gap_reports_router
from app.observability import install_observability, problem_response


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


@app.middleware("http")
async def require_internal_api_key(request: Request, call_next):
    if request.url.path == "/health":
        return await call_next(request)
    if not compare_digest(request.headers.get("X-Internal-Api-Key", ""), get_settings().internal_api_key):
        return problem_response(
            request,
            status_code=401,
            title="Unauthorized",
            detail="Unauthorized service request.",
            problem_type="urn:pathbridge:problem:http-401",
        )
    return await call_next(request)


install_observability(app, "gap-analysis-service")


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"service": "gap-analysis", "status": "healthy"}
