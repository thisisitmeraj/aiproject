"""
routers/analyse.py – Extended analysis endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import AnalyseRequest, AnalyseResponse, ArticleCreate
from backend import models

router = APIRouter()


@router.post("/analyse", response_model=AnalyseResponse)
async def analyse_text(request: AnalyseRequest, db: Session = Depends(get_db)):
    """
    Analyse text for misinformation.
    Stores the result as an Article record in the database.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Lazy-load predictor
    try:
        from ml.predict import load_model, predict
        load_model()
        result = predict(request.text)
    except Exception:
        result = {
            "verdict": "UNVERIFIED",
            "confidence": 0.5,
            "credibility_score": 0.5,
            "label": "half-true",
        }

    label = result.get("label", "half-true")
    confidence = float(result.get("confidence", 0.5))
    credibility_score = float(result.get("credibility_score", confidence))

    label_to_verdict = {
        "false": "FAKE",
        "pants-fire": "FAKE",
        "barely-true": "UNVERIFIED",
        "half-true": "UNVERIFIED",
        "mostly-true": "CREDIBLE",
        "true": "CREDIBLE",
    }
    verdict = label_to_verdict.get(label, "UNVERIFIED")

    # Persist to DB
    try:
        article = models.Article(
            url=request.url,
            content=request.text,
            credibility_score=credibility_score,
            verdict=verdict,
        )
        db.add(article)
        db.commit()
        db.refresh(article)
    except Exception as e:
        db.rollback()
        # Non-fatal: still return result even if DB write fails
        print(f"[WARN] DB write failed: {e}")

    return AnalyseResponse(
        verdict=verdict,
        confidence=round(confidence, 4),
        credibility_score=round(credibility_score, 4),
        label=label,
    )
