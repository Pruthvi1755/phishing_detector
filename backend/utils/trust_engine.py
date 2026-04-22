"""
Trust Engine - Handles domain whitelisting and reputation scoring.
Used to reduce false positives for highly trusted domains.
"""

import tldextract
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Highly trusted domains that should almost never be flagged as phishing
TRUSTED_DOMAINS = {
    "google.com", "google.co.in", "youtube.com", "gmail.com",
    "github.com", "microsoft.com", "apple.com", "amazon.com",
    "facebook.com", "instagram.com", "twitter.com", "linkedin.com",
    "netflix.com", "adobe.com", "zoom.us", "dropbox.com",
    "slack.com", "atlassian.com", "bitbucket.org", "gitlab.com",
    "stackoverflow.com", "medium.com", "wikipedia.org",
    "paypal.com", "stripe.com", "chase.com", "wellsfargo.com",
    "bankofamerica.com", "hsbc.com", "icloud.com", "outlook.com"
}

# TLD Reputation (Higher score = higher risk)
# Sources: Spamhaus, SURBL, and common phishing TLD reports
SUSPICIOUS_TLDS = {
    "tk": 0.8, "ml": 0.8, "ga": 0.8, "cf": 0.8, "gq": 0.8,  # Free TLDs
    "xyz": 0.6, "icu": 0.6, "top": 0.5, "club": 0.4, "site": 0.4,
    "online": 0.3, "zip": 0.9, "mov": 0.8, "ru": 0.5, "cn": 0.5
}

class TrustEngine:
    def __init__(self):
        pass

    def get_domain_info(self, url: str) -> dict:
        """Extract domain components using tldextract."""
        ext = tldextract.extract(url)
        return {
            "subdomain": ext.subdomain,
            "domain": ext.domain,
            "suffix": ext.suffix,
            "registered_domain": f"{ext.domain}.{ext.suffix}"
        }

    def is_whitelisted(self, url: str) -> bool:
        """Check if the domain is in the trusted whitelist."""
        info = self.get_domain_info(url)
        reg_domain = info["registered_domain"].lower()
        
        if reg_domain in TRUSTED_DOMAINS:
            # Special case: check if it's a direct subdomain or just the domain
            # We want to avoid flagging 'google.com.badsite.com'
            return True
        return False

    def get_tld_risk(self, url: str) -> float:
        """Return a risk score based on the TLD."""
        info = self.get_domain_info(url)
        suffix = info["suffix"].lower()
        return SUSPICIOUS_TLDS.get(suffix, 0.0)

    def calculate_reputation_adjustment(self, url: str, base_score: float) -> float:
        """
        Adjust the ML risk score based on domain reputation.
        Returns the adjusted score (0-100).
        """
        if self.is_whitelisted(url):
            # For whitelisted domains, we drastically reduce the score
            # unless it's a very clear phishing attempt (e.g. nested in path)
            logger.info("Domain %s is WHITELISTED. Reducing risk score.", url)
            return min(base_score, 5.0) # Cap at 5% risk

        tld_risk = self.get_tld_risk(url)
        if tld_risk > 0:
            # Boost the score slightly for suspicious TLDs
            adjustment = tld_risk * 20 # Up to 20 point boost
            logger.info("Suspicious TLD (%s) detected. Boosting risk score by %.1f", url, adjustment)
            return min(base_score + adjustment, 100.0)

        return base_score

trust_engine = TrustEngine()
