"""
backend/tests/test_model.py
Unit tests for feature extractor and URL validator.

Run with:
    pytest backend/tests/test_model.py -v
"""

import pytest
from backend.utils.feature_extractor import extract_features
from backend.utils.url_validator import validate_url


class TestURLValidator:
    def test_valid_https_url(self):
        ok, msg = validate_url("https://www.google.com")
        assert ok is True
        assert msg == ""

    def test_valid_http_url(self):
        ok, msg = validate_url("http://example.com/path")
        assert ok is True

    def test_empty_string(self):
        ok, msg = validate_url("")
        assert ok is False
        assert "empty" in msg.lower()

    def test_whitespace_only(self):
        ok, msg = validate_url("   ")
        assert ok is False

    def test_missing_scheme(self):
        ok, msg = validate_url("www.google.com")
        assert ok is False
        assert "http" in msg.lower()

    def test_url_with_spaces(self):
        ok, msg = validate_url("https://go ogle.com")
        assert ok is False

    def test_url_too_long(self):
        long_url = "https://example.com/" + "a" * 3000
        ok, msg = validate_url(long_url)
        assert ok is False
        assert "length" in msg.lower()

    def test_ftp_url_accepted(self):
        ok, _ = validate_url("ftp://files.example.com/resource.zip")
        assert ok is True


class TestFeatureExtractor:
    def test_returns_all_expected_keys(self):
        expected = {
            "url_length", "valid_url", "at_symbol", "sensitive_words_count",
            "path_length", "isHttps", "nb_dots", "nb_hyphens", "nb_and",
            "nb_or", "nb_www", "nb_com", "nb_underscore",
        }
        feats = extract_features("https://www.example.com/path")
        assert set(feats.keys()) == expected

    def test_https_flag_true(self):
        feats = extract_features("https://example.com")
        assert feats["isHttps"] == 1.0

    def test_http_flag_false(self):
        feats = extract_features("http://example.com")
        assert feats["isHttps"] == 0.0

    def test_at_symbol_detected(self):
        feats = extract_features("http://real.com@evil.com/path")
        assert feats["at_symbol"] == 1.0

    def test_at_symbol_absent(self):
        feats = extract_features("https://example.com")
        assert feats["at_symbol"] == 0.0

    def test_sensitive_words_counted(self):
        feats = extract_features("http://secure-login-verify.evil.ru")
        assert feats["sensitive_words_count"] >= 2

    def test_url_length_correct(self):
        url = "https://example.com"
        feats = extract_features(url)
        assert feats["url_length"] == float(len(url))

    def test_dot_count(self):
        feats = extract_features("https://a.b.c.d.example.com")
        assert feats["nb_dots"] == 6.0

    def test_hyphen_count(self):
        feats = extract_features("https://fake-login-secure-bank.com")
        assert feats["nb_hyphens"] == 3.0

    def test_www_count(self):
        feats = extract_features("https://www.example.com")
        assert feats["nb_www"] == 1.0

    def test_com_count(self):
        feats = extract_features("https://www.example.com")
        assert feats["nb_com"] == 1.0

    def test_query_params_and_count(self):
        feats = extract_features("https://example.com/?a=1&b=2&c=3")
        assert feats["nb_and"] == 2.0

    def test_values_are_floats(self):
        feats = extract_features("https://example.com")
        for k, v in feats.items():
            assert isinstance(v, float), f"{k} should be float, got {type(v)}"
