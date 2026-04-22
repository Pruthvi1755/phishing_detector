"""
Model loading utility with diagnostics and graceful failure.
"""
import os
import joblib
import sklearn
import numpy as np
from pathlib import Path
from backend.utils.logger import get_logger

logger = get_logger(__name__)

def load_model_state():
    """
    Load ML model and feature names with detailed diagnostics.
    Returns:
        tuple: (model, feature_names) or (None, None)
    """
    # 1. Diagnostics
    cwd = os.getcwd()
    logger.info("🔍 DIAGNOSTICS: CWD=%s", cwd)
    logger.info("🔍 DIAGNOSTICS: Sklearn Version=%s", sklearn.__version__)
    logger.info("🔍 DIAGNOSTICS: Numpy Version=%s", np.__version__)

    # 2. Path Resolution
    # On Render, the structure is /opt/render/project/src/
    # This file is at /backend/utils/model_loader.py
    # Model is at /backend/model/model.pkl
    
    base_path = Path(__file__).parent.parent / "model"
    model_path = base_path / "model.pkl"
    feat_path = base_path / "feature_names.pkl"

    logger.info("🔍 DIAGNOSTICS: Looking for model at: %s", model_path.absolute())
    logger.info("🔍 DIAGNOSTICS: Path exists: %s", model_path.exists())

    model = None
    feature_names = None

    # 3. Model Loading
    try:
        if model_path.exists():
            model = joblib.load(model_path)
            logger.info("✅ SUCCESS: ML model loaded successfully.")
        else:
            logger.error("❌ FAILURE: Model file not found at %s", model_path)
            
        if feat_path.exists():
            feature_names = joblib.load(feat_path)
            logger.info("✅ SUCCESS: Feature names loaded.")
        else:
            # Fallback
            feature_names = [
                "url_length", "valid_url", "at_symbol", "sensitive_words_count",
                "path_length", "isHttps", "nb_dots", "nb_hyphens", "nb_and",
                "nb_or", "nb_www", "nb_com", "nb_underscore"
            ]
            logger.warning("⚠️ WARNING: Feature names file not found. Using defaults.")
            
    except Exception as exc:
        logger.exception("❌ CRITICAL: Model loading failed: %s", exc)
        # We return None, None so the app starts but the /predict endpoint handles it
        return None, None

    return model, feature_names
