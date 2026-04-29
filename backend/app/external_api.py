from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel, Field, conint
from typing import List, Optional, Literal, Annotated
from datetime import datetime
import os

router = APIRouter(prefix="/api/external", tags=["external"])
EXTERNAL_RENDER_ENABLED = os.getenv("EXTERNAL_RENDER_ENABLED", "false").lower() == "true"
FACELESSFORGE_API_KEY = os.getenv("FACELESSFORGE_API_KEY", "")

RenderStatus = Literal["queued","rendering","completed","failed","cancelled","expired_artifact","not_found","error","unknown"]
JobId = Annotated[str, Field(min_length=8, max_length=64)]
ProgressPercent = conint(ge=0, le=100)

class ExternalBatchStatusRequest(BaseModel):
    job_ids: List[JobId] = Field(..., min_length=1, max_length=50)

class ExternalBatchStatusItem(BaseModel):
    job_id: str; project_id: Optional[str] = None; status: RenderStatus
    progress: Optional[ProgressPercent] = None; error: Optional[str] = None
    updated_at: Optional[datetime] = None; artifact_url: Optional[str] = None
    duration_sec: Optional[float] = None

class ExternalBatchStatusResponse(BaseModel):
    jobs: List[ExternalBatchStatusItem]

def verify_external_key(x_facelessforge_key: str = Header(..., alias="X-FacelessForge-Key")):
    if not EXTERNAL_RENDER_ENABLED: raise HTTPException(404, "External API disabled")
    if not FACELESSFORGE_API_KEY or x_facelessforge_key!= FACELESSFORGE_API_KEY: raise HTTPException(401, "Invalid API key")
    return True

def _get_render_service():
    try:
        from app.services.render_service import render_service

        return render_service
    except ImportError:
        return None


@router.post("/render-video-status/batch", response_model=ExternalBatchStatusResponse)
async def get_batch_render_status(payload: ExternalBatchStatusRequest, _: bool = Depends(verify_external_key)):
    render_service = _get_render_service()
    if render_service is None:
        return ExternalBatchStatusResponse(
            jobs=[
                ExternalBatchStatusItem(
                    job_id=job_id,
                    status="error",
                    error="Render service is not configured",
                )
                for job_id in payload.job_ids
            ]
        )
    jobs = []
    for job_id in payload.job_ids:
        try:
            s = await render_service.get_render_status(job_id)
            if not s: jobs.append(ExternalBatchStatusItem(job_id=job_id, status="not_found", error="Job not found")); continue
            m = {"pending":"queued","processing":"rendering","in_progress":"rendering","done":"completed","success":"completed","error":"failed","canceled":"cancelled"}
            jobs.append(ExternalBatchStatusItem(job_id=job_id, project_id=s.get("project_id"), status=m.get(str(s.get("status","")).lower(), str(s.get("status","unknown")).lower()), progress=s.get("progress"), error=s.get("error")))
        except Exception as e: jobs.append(ExternalBatchStatusItem(job_id=job_id, status="error", error=str(e)[:200]))
    return ExternalBatchStatusResponse(jobs=jobs)
