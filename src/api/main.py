"""FastAPI entrypoint for the Candidate-Job Matching AI service.

Run from the repository root:
    python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import ExtractRequest, MatchRequest, RankRequest
from src.api.service import AIService, ModelUnavailableError

logger = logging.getLogger("cjm.ai-service")
service = AIService()


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    return [item.strip() for item in raw.split(",") if item.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI):
    if os.getenv("AI_SERVICE_EAGER_LOAD", "false").lower() == "true":
        try:
            _ = service.predictor
        except ModelUnavailableError:
            logger.warning("AI model chưa sẵn sàng; extraction vẫn hoạt động.")
    yield


app = FastAPI(
    title="Candidate-Job Matching AI Service",
    version="1.0.0",
    description="Entity extraction, SBERT embedding, GCN matching and ranking service.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _service_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ModelUnavailableError):
        return HTTPException(status_code=503, detail=str(exc))
    if isinstance(exc, (FileNotFoundError, ValueError)):
        return HTTPException(status_code=400, detail=str(exc))
    logger.exception("AI service request failed")
    return HTTPException(status_code=500, detail="AI service xử lý thất bại.")


@app.get("/health/live", tags=["health"])
def liveness() -> dict:
    return {"status": "ok", "service": "cjm-ai"}


@app.get("/health/ready", tags=["health"])
def readiness() -> dict:
    ready = service.is_ready()
    payload = {
        "status": "ready" if ready else "not_ready",
        "service": "cjm-ai",
        "model_available": ready,
        "model_path": service.model_path,
    }
    if not ready:
        raise HTTPException(status_code=503, detail=payload)
    return payload


@app.get("/v1/meta", tags=["health"])
def metadata() -> dict:
    return service.metadata()


@app.post("/v1/entities/extract", tags=["extraction"])
def extract(request: ExtractRequest) -> dict:
    try:
        return service.extract(request.text, request.document_type)
    except Exception as exc:
        raise _service_error(exc) from exc


@app.post("/v1/match", tags=["matching"])
def match(request: MatchRequest) -> dict:
    if request.cv_text is None and request.cv_entities is None:
        raise HTTPException(status_code=422, detail="Thiếu cv_text hoặc cv_entities.")
    if request.jd_text is None and request.jd_entities is None:
        raise HTTPException(status_code=422, detail="Thiếu jd_text hoặc jd_entities.")
    try:
        return service.match_text(
            request.cv_text,
            request.jd_text,
            request.cv_entities,
            request.jd_entities,
            request.alpha,
            request.include_entities,
        )
    except Exception as exc:
        raise _service_error(exc) from exc


@app.post("/v1/rank", tags=["ranking"])
def rank(request: RankRequest) -> dict:
    if request.cv_text is None and request.cv_entities is None:
        raise HTTPException(status_code=422, detail="Thiếu cv_text hoặc cv_entities.")
    for job in request.jobs:
        if job.jd_text is None and job.jd_entities is None:
            raise HTTPException(
                status_code=422,
                detail=f"Job {job.job_id} thiếu jd_text hoặc jd_entities.",
            )
    try:
        jobs = [job.model_dump() for job in request.jobs]
        return service.rank(
            request.cv_text,
            request.cv_entities,
            jobs,
            request.alpha,
            request.include_entities,
        )
    except Exception as exc:
        raise _service_error(exc) from exc


@app.post("/v1/match/files", tags=["matching"])
async def match_files(
    cv_file: UploadFile = File(...),
    jd_file: UploadFile = File(...),
    alpha: float | None = None,
    include_entities: bool = False,
) -> dict:
    if alpha is not None and not 0.0 <= alpha <= 1.0:
        raise HTTPException(status_code=422, detail="alpha phải nằm trong [0, 1].")
    try:
        cv_content = await cv_file.read()
        jd_content = await jd_file.read()
        return service.match_uploaded_files(
            cv_file.filename or "cv.txt",
            cv_content,
            jd_file.filename or "jd.txt",
            jd_content,
            alpha,
            include_entities,
        )
    except Exception as exc:
        raise _service_error(exc) from exc
