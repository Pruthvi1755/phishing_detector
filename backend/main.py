"""
AI Phishing Detection System - FastAPI Backend
Main application entry point with all API routes.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
import joblib
import os
import time
from contextlib import asynccontextmanager

from backend.config import settings
from backend.utils.feature_extractor import extract_features
from backend.utils.url_validator import validate_url
from backend.utils.logger import get_logger
from backend.utils.trust_engine import trust_engine
from backend.utils.explanations_engine import generate_explanations

from backend.utils.model_loader import load_model_state

logger = get_logger(__name__)

# ── Model state (Global) ──────────────────────────────────────────────────────
model = None
feature_names = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: Loads model on startup, cleans up on shutdown."""
    global model, feature_names
    
    logger.info("🚀 STARTUP: Initialising PhishGuard System...")
    
    # Load model state using the resilient utility
    model, feature_names = load_model_state()
    
    if model is None:
        logger.error("⚠️ APP STARTED WITHOUT MODEL: /predict will return 503 until resolved.")
    else:
        logger.info("✨ PhishGuard API is ready to serve predictions.")
        
    yield
    logger.info("🛑 SHUTDOWN: Cleaning up...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PhishGuard API",
    description="AI-powered phishing / fake website detection",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    url: str

    @validator("url")
    def url_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("URL must not be empty")
        return v.strip()


class FeatureDetail(BaseModel):
    name: str
    value: float
    risk: bool


class PredictResponse(BaseModel):
    url: str
    status: str          # "SAFE" | "SUSPICIOUS" | "PHISHING"
    risk_score: float    # 0–100
    confidence: float    # 0–100
    features: list[FeatureDetail]
    explanations: list[str]
    processing_time_ms: float


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "PhishGuard API", "version": "1.1.0"}


@app.get("/health", tags=["Health"])
async def health():
    """Detailed health check."""
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "features": feature_names,
    }


@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict(body: PredictRequest):
    """
    Analyse a URL and return a phishing risk assessment.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="ML model not loaded on server.")

    start = time.perf_counter()

    # 1. Validate URL format
    is_valid, error_msg = validate_url(body.url)
    if not is_valid:
        raise HTTPException(status_code=422, detail=error_msg)

    # 2. Extract features
    try:
        feat_dict = extract_features(body.url)
    except Exception as exc:
        logger.exception("Feature extraction failed for %s", body.url)
        raise HTTPException(status_code=500, detail=f"Feature extraction error: {exc}") from exc

    # 3. Build ordered feature vector for model
    try:
        import pandas as pd
        model_input_dict = {f: feat_dict.get(f, 0.0) for f in feature_names}
        feat_vector = pd.DataFrame([model_input_dict])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Data preparation error: {exc}") from exc

    # 4. Predict
    try:
        proba = model.predict_proba(feat_vector)[0]
        phishing_prob = float(proba[1])
        base_risk_score = phishing_prob * 100
        confidence = round(max(proba) * 100, 2)
    except Exception as exc:
        logger.exception("Model inference failed")
        raise HTTPException(status_code=500, detail=f"Inference error: {exc}") from exc

    # 5. Apply Domain Trust System (Adjustment)
    risk_score = trust_engine.calculate_reputation_adjustment(body.url, base_risk_score)
    risk_score = round(risk_score, 2)

    # 6. Smarter Classification Logic
    if trust_engine.is_whitelisted(body.url):
        status = "SAFE"
    elif risk_score < 25:
        status = "SAFE"
    elif risk_score < 60:
        if risk_score > 50 and confidence > 85:
            status = "PHISHING"
        else:
            status = "SUSPICIOUS"
    else:
        status = "PHISHING"

    # 7. Generate Human-Readable Explanations
    explanations = generate_explanations(feat_dict, status, risk_score)

    # 8. Feature detail list (for UI breakdown)
    feature_details = [
        FeatureDetail(
            name=f,
            value=feat_dict.get(f, 0.0),
            risk=_is_risky_feature(f, feat_dict.get(f, 0.0)),
        )
        for f in feat_dict.keys()
    ]

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info("Prediction: url=%s status=%s score=%.1f (base=%.1f) ms=%.1f", 
                body.url, status, risk_score, base_risk_score, elapsed_ms)

    return PredictResponse(
        url=body.url,
        status=status,
        risk_score=risk_score,
        confidence=confidence,
        features=feature_details,
        explanations=explanations,
        processing_time_ms=elapsed_ms,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────
def _is_risky_feature(name: str, value: float) -> bool:
    """Return True if this feature value is suspicious."""
    risky_map = {
        "at_symbol":            lambda v: v > 0,
        "isHttps":              lambda v: v == 0,
        "sensitive_words_count":lambda v: v > 0,
        "nb_hyphens":           lambda v: v > 3,
        "url_length":           lambda v: v > 100,
        "nb_dots":              lambda v: v > 5,
        "nb_subdomains":        lambda v: v > 3,
        "is_ip_address":        lambda v: v > 0,
        "punycode_detected":    lambda v: v > 0,
        "brand_impersonation":  lambda v: v >= 1.0,
        "suspicious_tld_score": lambda v: v > 0.5,
        "url_entropy":          lambda v: v > 4.5,
    }
    fn = risky_map.get(name)
    return fn(value) if fn else False


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s", request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )
