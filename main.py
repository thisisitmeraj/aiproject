import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(
    title="Fake News & Misinformation Detector API",
    description="Real-time fake news detection using NLP and ML",
    version="1.0.0",
)

# CORS configuration - allow React frontend and Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "chrome-extension://*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Schemas (inline, smaller footprint for quick startup)
# ---------------------------------------------------------------------------

class AnalyseRequest(BaseModel):
    text: str

class AnalyseResponse(BaseModel):
    verdict: str
    confidence: float
    credibility_score: float
    label: Optional[str] = None


# ---------------------------------------------------------------------------
# Model loader (lazy – loaded once on first request)
# ---------------------------------------------------------------------------

_model_cache: dict = {}


def get_predictor():
    """Return the predict function, loading the model on first call."""
    if "predict" not in _model_cache:
        try:
            from ml.predict import load_model, predict as _predict
            load_model()
            _model_cache["predict"] = _predict
        except Exception as e:
            print(f"[WARN] Could not load ML model: {e}. Using placeholder predictor.")
            _model_cache["predict"] = _placeholder_predict
    return _model_cache["predict"]


def _placeholder_predict(text: str):
    """Placeholder used before the model is trained."""
    return {
        "verdict": "UNVERIFIED",
        "confidence": 0.5,
        "credibility_score": 0.5,
        "label": "half-true",
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"status": "Fake News Detector API running"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/analyse", response_model=AnalyseResponse)
async def analyse(request: AnalyseRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    predict_fn = get_predictor()
    result = predict_fn(request.text)

    # Normalise verdict label to uppercase display
    label = result.get("label", "unknown")
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

    return AnalyseResponse(
        verdict=verdict,
        confidence=round(confidence, 4),
        credibility_score=round(credibility_score, 4),
        label=label,
    )


# Include routers
from backend.routers import analyse as analyse_router
from backend.routers import articles as articles_router

app.include_router(analyse_router.router, prefix="/api/v1", tags=["analysis"])
app.include_router(articles_router.router, prefix="/api/v1", tags=["articles"])


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
