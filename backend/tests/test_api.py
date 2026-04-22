"""
backend/tests/test_api.py
Integration tests for PhishGuard FastAPI endpoints.

Run with:
    pytest backend/tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import numpy as np


# ── Mock model before importing app ──────────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def mock_model_load():
    """Inject a mock ML model so tests don't need model.pkl on disk."""
    mock_clf = MagicMock()
    mock_clf.predict_proba.return_value = np.array([[0.9, 0.1]])  # 10% phishing

    feature_names = [
        "url_length", "valid_url", "at_symbol", "sensitive_words_count",
        "path_length", "isHttps", "nb_dots", "nb_hyphens", "nb_and",
        "nb_or", "nb_www", "nb_com", "nb_underscore",
    ]

    with patch("backend.main.model", mock_clf), \
         patch("backend.main.feature_names", feature_names):
        yield mock_clf


@pytest.fixture(scope="session")
def client():
    """Create a test client for the FastAPI app."""
    from backend.main import app
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_root_returns_ok(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_health_returns_model_loaded(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "model_loaded" in data
        assert "features" in data


class TestPredictEndpoint:
    def test_safe_url_returns_200(self, client):
        resp = client.post("/predict", json={"url": "https://www.google.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "risk_score" in data
        assert 0 <= data["risk_score"] <= 100

    def test_response_schema_complete(self, client):
        resp = client.post("/predict", json={"url": "https://example.com"})
        assert resp.status_code == 200
        data = resp.json()
        for key in ("url", "status", "risk_score", "confidence", "features", "explanations", "processing_time_ms"):
            assert key in data, f"Missing key: {key}"

    def test_status_is_valid_enum(self, client):
        resp = client.post("/predict", json={"url": "https://example.com/login"})
        assert resp.json()["status"] in {"SAFE", "SUSPICIOUS", "PHISHING"}

    def test_features_list_populated(self, client):
        resp = client.post("/predict", json={"url": "https://example.com"})
        data = resp.json()
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 0
        # Each feature has name, value, risk
        feat = data["features"][0]
        assert "name" in feat and "value" in feat and "risk" in feat

    def test_explanations_list_populated(self, client):
        resp = client.post("/predict", json={"url": "http://evil-login.suspicious.ru"})
        data = resp.json()
        assert isinstance(data["explanations"], list)
        assert len(data["explanations"]) > 0


class TestInputValidation:
    def test_empty_url_returns_422(self, client):
        resp = client.post("/predict", json={"url": ""})
        assert resp.status_code == 422

    def test_missing_url_field_returns_422(self, client):
        resp = client.post("/predict", json={})
        assert resp.status_code == 422

    def test_url_without_scheme_returns_422(self, client):
        resp = client.post("/predict", json={"url": "www.google.com"})
        assert resp.status_code == 422

    def test_url_with_spaces_returns_422(self, client):
        resp = client.post("/predict", json={"url": "https://go ogle.com"})
        assert resp.status_code == 422

    def test_plaintext_returns_422(self, client):
        resp = client.post("/predict", json={"url": "not-a-url-at-all"})
        assert resp.status_code == 422

    def test_very_long_url_returns_422(self, client):
        long_url = "https://example.com/" + "a" * 3000
        resp = client.post("/predict", json={"url": long_url})
        assert resp.status_code == 422


class TestURLVariants:
    @pytest.mark.parametrize("url", [
        "https://www.github.com",
        "http://example.com",
        "https://sub.domain.example.co.uk/path?q=1&r=2",
    ])
    def test_valid_urls_succeed(self, client, url):
        resp = client.post("/predict", json={"url": url})
        assert resp.status_code == 200
