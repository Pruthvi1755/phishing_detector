"""
Explanations Engine - Generates human-readable risk explanations based on URL features.
"""

def generate_explanations(features: dict, status: str, risk_score: float) -> list[str]:
    """
    Generate a list of human-readable explanations for the given features and status.
    """
    msgs = []

    # ── High Priority Indicators ──
    if features.get("is_ip_address", 0) > 0:
        msgs.append("🚨 Detected IP address instead of a legitimate domain name.")
    
    if features.get("punycode_detected", 0) > 0:
        msgs.append("🚨 Unicode/Punycode detected — common technique for homograph impersonation.")

    if features.get("brand_impersonation", 0) >= 1.0:
        msgs.append("🚨 URL attempts brand impersonation by using a trusted name (e.g., 'paypal') in a suspicious context.")

    # ── Medium Priority Indicators ──
    if features.get("at_symbol", 0) > 0:
        msgs.append("⚠️ URL contains '@' symbol — often used to disguise the real destination.")

    if features.get("isHttps", 1) == 0:
        msgs.append("🔓 No HTTPS detected — connection is unencrypted and potentially unsafe.")

    if features.get("suspicious_tld_score", 0) > 0.5:
        msgs.append("⚠️ Domain uses a TLD frequently associated with phishing campaigns.")

    if features.get("sensitive_words_count", 0) > 0:
        cnt = int(features["sensitive_words_count"])
        msgs.append(f"⚠️ URL contains {cnt} sensitive keyword(s) (e.g., 'login', 'verify', 'secure').")

    # ── Structural Indicators ──
    if features.get("nb_subdomains", 0) > 3:
        msgs.append(f"📏 Excessive subdomain nesting ({int(features['nb_subdomains'])} subdomains) detected.")

    if features.get("url_entropy", 0) > 4.5:
        msgs.append("🧩 URL contains random-looking character patterns typical of generated malicious links.")

    if features.get("url_length", 0) > 100:
        msgs.append(f"📏 Unusually long URL ({int(features['url_length'])} chars) — may hide the real destination.")

    # ── Positive Reinforcement ──
    if status == "SAFE":
        if not msgs:
            msgs.append("✅ No suspicious indicators found. URL appears legitimate.")
        else:
            msgs.insert(0, "🛡️ Domain is recognized as highly trusted, overriding minor anomalies.")

    if not msgs and status != "SAFE":
        msgs.append("⚠️ Combination of multiple mild risk factors elevated the suspicion level.")

    return msgs
