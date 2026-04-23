"""
Model loading utility with diagnostics and graceful failure.
"""
import os
import joblib
import sklearn
import numpy as np
from pathlib import Path
from backend.utils.logger import get_logger

from backend.config import settings

logger = get_logger(__name__)

def load_model_state():
    """
    Load ML model and feature names with detailed diagnostics.
    Returns:
        tuple: (model, feature_names) or (None, None)
    """
    # 1. Diagnostics
    logger.info("🔍 STARTUPUP DIAGNOSTICS:")
    logger.info("   CWD: %s", os.getcwd())
    logger.info("   Python Path: %s", os.getenv("PYTHONPATH", "Not set"))
    logger.info("   Sklearn: %s", sklearn.__version__)
    
    # 2. Path Resolution (Using settings)
    model_path = Path(settings.MODEL_PATH)
    feat_path = Path(settings.FEATURE_NAMES_PATH)

    logger.info("   Target Model Path: %s", model_path)
    logger.info("   Target Feature Path: %s", feat_path)
    logger.info("   Model file exists: %s", model_path.exists())

    model = None
    feature_names = None

    # 3. Model Loading
    try:
        if model_path.exists():
            model = joblib.load(model_path)
            logger.info("✅ SUCCESS: ML model loaded successfully.")
        else:
            # Try a relative path search as fallback
            rel_path = Path("backend/model/model.pkl")
            if rel_path.exists():
                model = joblib.load(rel_path)
                logger.info("✅ SUCCESS: ML model loaded via relative path.")
            else:
                logger.error("❌ FAILURE: Model file not found.")
            
        if feat_path.exists():
            feature_names = joblib.load(feat_path)
            logger.info("✅ SUCCESS: Feature names loaded.")
        else:
            # Fallback feature names from training
            feature_names = [
                "url_length", "valid_url", "at_symbol", "sensitive_words_count",
                "path_length", "isHttps", "nb_dots", "nb_hyphens", "nb_and",
                "nb_or", "nb_www", "nb_com", "nb_underscore", "url_entropy",
                "nb_subdomains", "is_ip_address", "punycode_detected",
                "brand_impersonation", "suspicious_tld_score", "random_patterns",
                "url_encoding_count"
            ]
            logger.warning("⚠️ WARNING: Feature names file not found. Using defaults.")
            
    except Exception as exc:
        logger.exception("❌ CRITICAL: Model loading failed: %s", exc)
        return None, None

    return model, feature_names
