"""
schemas.py – Pydantic schemas for request / response validation
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

class AnalyseRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Article text or claim to analyse")
    url: Optional[str] = Field(None, description="Source URL (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Scientists discover that the moon is made of cheese.",
                "url": "https://example.com/article",
            }
        }


class AnalyseResponse(BaseModel):
    verdict: str = Field(..., description="FAKE | UNVERIFIED | CREDIBLE")
    confidence: float = Field(..., ge=0.0, le=1.0)
    credibility_score: float = Field(..., ge=0.0, le=1.0)
    label: Optional[str] = None
    claims: Optional[List[ClaimOut]] = None


# ---------------------------------------------------------------------------
# Articles
# ---------------------------------------------------------------------------

class ArticleCreate(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    credibility_score: Optional[float] = None
    verdict: Optional[str] = None


class ArticleOut(ArticleCreate):
    id: UUID
    analysed_at: datetime
    claims: List[ClaimOut] = []

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Claims
# ---------------------------------------------------------------------------

class ClaimCreate(BaseModel):
    claim_text: str
    score: Optional[float] = None
    explanation: Optional[str] = None
    sources_checked: Optional[List[Any]] = []


class ClaimOut(ClaimCreate):
    id: UUID
    article_id: UUID

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    extension_token: Optional[str] = None


class UserOut(BaseModel):
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Generic responses
# ---------------------------------------------------------------------------

class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str


# Resolve forward references
AnalyseResponse.model_rebuild()
ArticleOut.model_rebuild()
