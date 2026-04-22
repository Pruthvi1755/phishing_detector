"""
URL Feature Extractor
Extracts numeric features from a raw URL string for phishing detection.
Features are matched to the training dataset columns.
"""

import re
import math
import tldextract
from urllib.parse import urlparse
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Keywords commonly found in phishing URLs
SENSITIVE_KEYWORDS = [
    "login", "signin", "verify", "secure", "account", "update",
    "confirm", "banking", "paypal", "password", "credential",
    "auth", "webscr", "ebayisapi", "payment", "billing", "wallet",
    "token", "crypto", "binance", "coinbase", "metamask"
]

# Common brand names for impersonation detection
COMMON_BRANDS = [
    "google", "microsoft", "apple", "amazon", "facebook", "instagram",
    "twitter", "linkedin", "netflix", "paypal", "stripe", "chase",
    "wellsfargo", "bankofamerica", "binance", "coinbase", "metamask"
]

def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0.0
    probs = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
    entropy = -sum([p * math.log(p) / math.log(2.0) for p in probs])
    return float(entropy)

def detect_brand_impersonation(url: str) -> float:
    """
    Detect if a brand name is used in a suspicious way.
    e.g., 'paypal-secure-login.com' is suspicious if 'paypal' is not the SLD.
    """
    ext = tldextract.extract(url)
    domain = ext.domain.lower()
    subdomain = ext.subdomain.lower()
    path = urlparse(url).path.lower()
    
    score = 0.0
    for brand in COMMON_BRANDS:
        # If brand is in subdomain or path, but NOT in the main domain
        if (brand in subdomain or brand in path) and brand not in domain:
            score += 1.0
        # If brand is in domain but it's part of a longer suspicious string
        elif brand in domain and domain != brand:
            score += 0.5
            
    return float(min(score, 5.0))

def extract_features(url: str) -> dict[str, float]:
    """
    Extract a comprehensive feature dictionary from a URL string.
    Includes original lexical features plus advanced security indicators.
    """
    url = url.strip()
    try:
        parsed = urlparse(url)
        ext = tldextract.extract(url)
    except Exception as exc:
        logger.warning("Parsing failed for '%s': %s", url, exc)
        # Return a "broken" feature set
        return {f: 0.0 for f in ["url_length", "valid_url", "at_symbol", "isHttps"]}

    url_lower = url.lower()
    domain = ext.domain.lower()
    
    # ── Original Features (Maintaining Compatibility) ──
    features = {
        "url_length":            float(len(url)),
        "valid_url":             float(bool(parsed.scheme and parsed.netloc)),
        "at_symbol":             float("@" in url),
        "sensitive_words_count": float(sum(1 for kw in SENSITIVE_KEYWORDS if kw in url_lower)),
        "path_length":           float(len(parsed.path)),
        "isHttps":               float(parsed.scheme.lower() == "https"),
        "nb_dots":               float(url.count(".")),
        "nb_hyphens":            float(url.count("-")),
        "nb_and":                float(url.count("&")),
        "nb_or":                 float(url.count("|")),
        "nb_www":                float(url_lower.count("www")),
        "nb_com":                float(url_lower.count(".com")),
        "nb_underscore":         float(url.count("_")),
    }

    # ── New Advanced Features ──
    
    # URL Entropy
    features["url_entropy"] = calculate_entropy(url)
    
    # Subdomain count (more accurate than nb_dots)
    features["nb_subdomains"] = float(len(ext.subdomain.split(".")) if ext.subdomain else 0)
    
    # IP Address detection
    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    features["is_ip_address"] = float(bool(re.match(ip_pattern, ext.domain)))
    
    # Unicode/Punycode detection (Homograph attacks)
    features["punycode_detected"] = float(domain.startswith("xn--") or "xn--" in url_lower)
    
    # Brand Impersonation
    features["brand_impersonation"] = detect_brand_impersonation(url)
    
    # Suspicious TLD Score (Simplified version for ML, trust_engine handles it for logic)
    from backend.utils.trust_engine import SUSPICIOUS_TLDS
    features["suspicious_tld_score"] = float(SUSPICIOUS_TLDS.get(ext.suffix.lower(), 0.0))
    
    # Random character pattern detection (e.g., "ajshd123")
    # Heuristic: high entropy in short strings
    features["random_patterns"] = float(1.0 if features["url_entropy"] > 4.5 and len(url) < 50 else 0.0)
    
    # URL Encoding count
    features["url_encoding_count"] = float(url.count("%"))

    logger.debug("Extracted %d features for '%s'", len(features), url[:60])
    return features
