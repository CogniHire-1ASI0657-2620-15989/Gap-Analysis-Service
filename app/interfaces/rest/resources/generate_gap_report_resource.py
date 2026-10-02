from pydantic import BaseModel, Field


class GenerateGapReportResource(BaseModel):
    job_id: int = Field(gt=0)
