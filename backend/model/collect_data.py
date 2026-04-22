"""
Data Collection Script - Sourcing raw URLs for model retraining.
"""

import pandas as pd
import requests
import os
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# List of possible dataset URLs
DATASET_URLS = [
    "https://raw.githubusercontent.com/zandatomas/phishing-url-detection/master/datasets/url_dataset.csv",
    "https://raw.githubusercontent.com/shreyas-dodamani/Phishing-URL-Detection/master/dataset.csv",
    "https://raw.githubusercontent.com/kirula0626/AI-Malicious-URL-Checker/main/phishing_database.csv"
]

def download_raw_data(output_path: str):
    """Download a dataset with raw URLs from multiple possible sources."""
    for url in DATASET_URLS:
        logger.info("Attempting to download dataset from %s", url)
        try:
            df = pd.read_csv(url)
            # Normalize column names
            df.columns = [c.lower() for c in df.columns]
            
            # Find the URL and Target columns
            url_col = next((c for c in df.columns if any(k in c for k in ['url', 'domain', 'link', 'address'])), None)
            target_col = next((c for c in df.columns if any(k in c for k in ['target', 'label', 'status', 'result', 'class'])), None)
            
            if url_col and target_col:
                logger.info("Found columns: URL='%s', Target='%s'", url_col, target_col)
                df = df[[url_col, target_col]].rename(columns={url_col: 'url', target_col: 'target'})
                
                # Convert target to numeric (0 or 1)
                if df['target'].dtype == object:
                    # Handle common string labels
                    df['target'] = df['target'].str.lower().map({
                        'legitimate': 0, 'phishing': 1, 'bad': 1, 'good': 0, 
                        'benign': 0, 'malicious': 1, '1': 1, '0': 0, 'spam': 1
                    }).fillna(0).astype(int)
                
                # Ensure it's balanced or at least has both classes
                if df['target'].nunique() < 2:
                    logger.warning("Dataset only has one class. Skipping.")
                    continue

                # Take a sample if too large
                if len(df) > 5000:
                    df = df.sample(5000, random_state=42)
                
                df.to_csv(output_path, index=False)
                logger.info("Dataset saved successfully. Shape: %s", df.shape)
                return df
        except Exception as e:
            logger.warning("Failed to download from %s: %s", url, e)
            continue
    return None

def create_curated_dataset(output_path: str):
    """
    Create a curated dataset by combining trusted sources.
    Used as a fallback or to ensure high quality on top domains.
    """
    legit_urls = [
        "https://www.google.com", "https://www.microsoft.com", "https://www.apple.com",
        "https://www.amazon.com", "https://www.facebook.com", "https://www.github.com",
        "https://www.wikipedia.org", "https://www.youtube.com", "https://www.linkedin.com",
        "https://www.netflix.com", "https://www.paypal.com", "https://www.chase.com",
        "https://www.bankofamerica.com", "https://www.wellsfargo.com", "https://www.hsbc.com",
        "https://www.binance.com", "https://www.coinbase.com", "https://www.metamask.io",
        "https://www.reddit.com", "https://www.nytimes.com", "https://www.bbc.com",
        "https://www.quora.com", "https://www.medium.com", "https://www.stackexchange.com",
        "https://www.dropbox.com", "https://www.slack.com", "https://www.zoom.us",
        "https://www.spotify.com", "https://www.adobe.com", "https://www.salesforce.com"
    ]
    
    phishing_urls = [
        "http://paypal-secure-update.com", "http://login-microsoft-auth.xyz",
        "http://secure-banking-verify.ru", "http://amazon-gift-card-claim.top",
        "http://apple-id-support-verify.ga", "http://facebook-login-help.cf",
        "http://chase-online-banking.ml", "http://hsbc-account-security.tk",
        "http://binance-login-secure.xyz", "http://coinbase-auth-verify.icu",
        "http://metamask-extension-update.net", "http://192.168.1.1/login.php",
        "http://xn--pypal-4ve.com", "http://google.com.security-check.ru",
        "http://login.microsoftonline.com-security.ga", "http://verify-identity-chase.com",
        "http://account-update-bankofamerica.ru", "http://secure-login-wellsfargo.xyz",
        "http://signin-ebay-com.tk", "http://update-paypal-info.ml",
        "http://verify-your-account-now.com", "http://login-credential-stolen.ga",
        "http://secure-auth-check.top", "http://identity-theft-prevention.ru",
        "http://random-phishing-site-1.xyz", "http://random-phishing-site-2.tk"
    ]
    
    data = []
    for u in legit_urls: data.append({"url": u, "target": 0})
    for u in phishing_urls: data.append({"url": u, "target": 1})
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    logger.info("Curated dataset created with %d URLs", len(df))
    return df

if __name__ == "__main__":
    # We will try to download a larger one first
    output = "backend/model/raw_urls.csv"
    df = download_raw_data(output)
    if df is None or 'url' not in df.columns:
        logger.warning("Falling back to curated dataset.")
        create_curated_dataset(output)
