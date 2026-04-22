"""
backend/model/train.py
Full ML training pipeline for phishing URL detection with advanced feature extraction.
"""

import argparse
import os
import joblib
import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, 
    roc_auc_score, f1_score, precision_score, recall_score
)
from backend.utils.feature_extractor import extract_features

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("train")

MODEL_DIR = os.path.dirname(__file__)

def load_and_preprocess(csv_path: str) -> tuple[pd.DataFrame, pd.Series]:
    """Load raw URLs and extract features."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    df = pd.read_csv(csv_path)
    logger.info("Loaded raw dataset: %d rows", len(df))

    if 'url' not in df.columns or 'target' not in df.columns:
        raise ValueError("Dataset must have 'url' and 'target' columns")

    logger.info("Extracting features for %d URLs... (this may take a minute)", len(df))
    
    feature_list = []
    for url in df['url']:
        try:
            feats = extract_features(str(url))
            feature_list.append(feats)
        except Exception as e:
            logger.warning("Failed to extract features for %s: %s", url, e)
            # Add a dummy record with zeros to maintain index
            dummy = {k: 0.0 for k in extract_features("https://example.com").keys()}
            feature_list.append(dummy)

    X = pd.DataFrame(feature_list)
    y = df['target']
    
    # Save feature names for inference
    feat_names_path = os.path.join(MODEL_DIR, "feature_names.pkl")
    joblib.dump(X.columns.tolist(), feat_names_path)
    logger.info("Saved feature names to %s", feat_names_path)
    
    return X, y

def evaluate(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Evaluate trained model and print detailed metrics including FPR."""
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc     = accuracy_score(y_test, y_pred)
    prec    = precision_score(y_test, y_pred)
    rec     = recall_score(y_test, y_pred)
    f1      = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)
    cm      = confusion_matrix(y_test, y_pred)
    
    # Calculate False Positive Rate
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

    logger.info("=" * 60)
    logger.info("DETAILED EVALUATION RESULTS")
    logger.info("-" * 60)
    logger.info("  Accuracy  : %.4f (%.2f%%)", acc, acc * 100)
    logger.info("  Precision : %.4f (how many flagged are actually phishing)", prec)
    logger.info("  Recall    : %.4f (how many phishing were caught)", rec)
    logger.info("  F1-Score  : %.4f", f1)
    logger.info("  ROC-AUC   : %.4f", roc_auc)
    logger.info("  FPR       : %.4f (False Positive Rate - LOWER IS BETTER)", fpr)
    logger.info("-" * 60)
    logger.info("Confusion Matrix:\n%s", cm)
    logger.info("-" * 60)
    logger.info("Classification Report:\n%s", classification_report(y_test, y_pred))
    logger.info("=" * 60)

    return {"accuracy": acc, "roc_auc": roc_auc, "fpr": fpr}

def train(csv_path: str, output_dir: str = MODEL_DIR) -> None:
    """Full training pipeline with feature extraction."""
    X, y = load_and_preprocess(csv_path)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GradientBoostingClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            random_state=42,
        )),
    ])

    logger.info("Training GradientBoosting model on %d samples...", len(X_train))
    pipeline.fit(X_train, y_train)

    evaluate(pipeline, X_test, y_test)

    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "model.pkl")
    joblib.dump(pipeline, model_path)
    logger.info("SUCCESS: Model saved to %s", model_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train phishing detection model")
    parser.add_argument("--data", default="backend/model/raw_urls.csv", help="Path to raw URL CSV")
    args = parser.parse_args()
    train(args.data)
