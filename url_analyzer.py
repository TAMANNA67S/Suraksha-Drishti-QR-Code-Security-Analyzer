
import re
import socket
import ssl
import logging
import requests
import whois 
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'payment', 'bank', 'update', 'account',
    'otp', 'reward', 'gift', 'free', 'secure', 'confirm', 'signin',
    'invoice', 'urgent', 'alert', 'suspend', 'validate'
]

SHORTENING_SERVICES = [
    'bit.ly', 'tinyurl.com', 't.co', 'cutt.ly', 'rebrand.ly',
    'goo.gl', 'ow.ly', 'is.gd', 'buff.ly', 'adf.ly'
]

TYPOSQUAT_CHARS = {'0': 'o', '1': 'l', '3': 'e', '5': 's', '@': 'a', '4': 'a'}


def is_typosquatted(domain: str) -> bool:
    """Detects common character substitutions used in typosquatting."""
    return any(ch in domain for ch in TYPOSQUAT_CHARS)


def get_domain_age(domain: str) -> int:

    """

    Returns domain age in days via WHOIS.

    Returns -1 on failure.

    """

    try:
        w = whois.whois(domain)
        creation = w.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        if creation and isinstance(creation, datetime):
            return (datetime.now() - creation).days
    except Exception as e:
        logger.debug(f"WHOIS error for {domain}: {e}")
    return -1

def check_ssl_certificate(domain: str) -> bool:
    """Returns True when a valid SSL cert is present on port 443."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                return bool(ssock.getpeercert())
    except Exception as e:
        logger.debug(f"SSL check error for {domain}: {e}")
        return False


def check_url_reputation(url: str) -> str:
    """
    Lightweight reachability probe.
    Returns 'Reachable', 'Suspicious', or 'Unreachable'.
    """
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        return "Reachable" if r.status_code < 400 else "Suspicious"
    except Exception as e:
        logger.debug(f"Reputation check error for {url}: {e}")
        return "Unreachable"


def extract_features(url: str) -> dict:
    """
    Analyses a URL and returns a comprehensive security feature dict.
    Used by the full risk pipeline (url_analyzer → risk_engine).
    """
    try:
        safe_url = url if "://" in url else f"http://{url}"
        parsed = urlparse(safe_url)
        domain = parsed.netloc.lower().split(':')[0]  

        domain_parts = [p for p in domain.split('.') if p]
        num_subdomains = max(0, len(domain_parts) - 2)

        features = {
            "url":                      url,
            "url_length":               len(url),
            "is_https":                 parsed.scheme == 'https',
            "has_ip_address":           bool(re.search(r'\d{1,3}(?:\.\d{1,3}){3}', domain)),
            "num_subdomains":           num_subdomains,
            "is_shortened":             any(s in domain for s in SHORTENING_SERVICES),
            "is_typosquatted":          is_typosquatted(domain),
            "special_char_count":       len(re.findall(r'[@#$%^&*()!+=~`]', url)),
            "suspicious_keywords_found": [kw for kw in SUSPICIOUS_KEYWORDS if kw in url.lower()],
            "domain_age_days":          get_domain_age(domain),
            "ssl_valid":                check_ssl_certificate(domain),
            "url_reputation":           check_url_reputation(url),
        }
        return features

    except Exception as e:
        logger.error(f"Feature extraction failed for '{url}': {e}")
        return {"error": f"Analysis failed: {str(e)}"}
