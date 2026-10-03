"""Pydantic request/response schemas for the AI service."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=200_000)
    document_type: str = Field(default="document", max_length=32)


class MatchRequest(BaseModel):
    cv_text: Optional[str] = Field(default=None, max_length=200_000)
    jd_text: Optional[str] = Field(default=None, max_length=200_000)
    cv_entities: Optional[Dict[str, List[str]]] = None
    jd_entities: Optional[Dict[str, List[str]]] = None
    alpha: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    include_entities: bool = True


class RankJob(BaseModel):
    job_id: str = Field(..., min_length=1, max_length=128)
    jd_text: Optional[str] = Field(default=None, max_length=200_000)
    jd_entities: Optional[Dict[str, List[str]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RankRequest(BaseModel):
    cv_text: Optional[str] = Field(default=None, max_length=200_000)
    cv_entities: Optional[Dict[str, List[str]]] = None
    jobs: List[RankJob] = Field(..., min_length=1, max_length=100)
    alpha: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    include_entities: bool = False


class EntityResponse(BaseModel):
    document_type: str
    entities: Dict[str, List[str]]
    entity_count: int


class ErrorResponse(BaseModel):
    detail: str
