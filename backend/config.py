"""
Application configuration — reads from environment variables with sane defaults.
Call check_keys() at startup to verify required settings are present.
"""

import os
from pydantic import validator
from pydantic_settings import BaseSettings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    """
    All application settings. Values are loaded from environment variables
    (case-insensitive) or .env file via python-dotenv.
    """

    # ── Server ────────────────────────────────────────────────
    APP_ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # ── CORS ──────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] | str = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # ── Model ─────────────────────────────────────────────────
    MODEL_PATH: str = "backend/model/model.pkl"
    FEATURE_NAMES_PATH: str = "backend/model/feature_names.pkl"

    # ── Risk thresholds (%) ───────────────────────────────────
    SAFE_THRESHOLD: float = 30.0        # below 30 → SAFE
    SUSPICIOUS_THRESHOLD: float = 65.0  # 30–65  → SUSPICIOUS, ≥65 → PHISHING

    # ── Logging ───────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def check_keys() -> bool:
    """
    Validate that required configuration values are present and sensible.

    Returns:
        True if all checks pass.

    Raises:
        ValueError: If a critical config value is missing or invalid.

    Example:
        >>> from backend.config import check_keys
        >>> check_keys()
        True
    """
    errors: list[str] = []

    if not (0 < settings.SAFE_THRESHOLD < settings.SUSPICIOUS_THRESHOLD <= 100):
        errors.append(
            f"Invalid threshold order: SAFE={settings.SAFE_THRESHOLD}, "
            f"SUSPICIOUS={settings.SUSPICIOUS_THRESHOLD}"
        )

    if settings.APP_ENV not in {"development", "staging", "production"}:
        errors.append(f"Unknown APP_ENV: {settings.APP_ENV}")

    if errors:
        for err in errors:
            logger.error("Config error: %s", err)
        raise ValueError("Configuration validation failed:\n" + "\n".join(errors))

    logger.info("✅ Config OK — env=%s thresholds=%.0f/%.0f",
                settings.APP_ENV, settings.SAFE_THRESHOLD, settings.SUSPICIOUS_THRESHOLD)
    return True
