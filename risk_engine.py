
import re
import logging

logger = logging.getLogger(__name__)


RISK_WEIGHTS = {
    "is_https": {
        "weight": 25,
        "reason": "Missing HTTPS encryption — data is transmitted in plaintext."
    },
    "has_ip_address": {
        "weight": 30,
        "reason": "URL uses a raw IP address instead of a domain name."
    },
    "is_shortened": {
        "weight": 15,
        "reason": "URL uses a shortening service — final destination is hidden."
    },
    "is_typosquatted": {
        "weight": 20,
        "reason": "Domain contains character substitutions typical of typosquatting."
    },
    "suspicious_keywords_found": {
        "weight": 20,
        "reason": "Suspicious keywords detected: {values}."
    },
    "special_char_count": {
        "weight": 10,
        "threshold": 15,
        "reason": "Excessive special characters detected — possible URL obfuscation."
    },
    "num_subdomains": {
        "weight": 10,
        "threshold": 3,
        "reason": "Unusually high number of subdomains detected."
    },
}


THRESHOLDS = {"Safe": 30, "Moderate": 60}

def get_risk_category(score: int) -> str:
    if score <= THRESHOLDS["Safe"]:
        return "Safe"
    if score <= THRESHOLDS["Moderate"]:
        return "Moderate"
    return "Dangerous"


def calculate_risk_score(features: dict) -> dict:
    """
    Calculates a 0-100 risk score from a feature dict.
    Returns: { risk_score, risk_category, reasons }
    """
    score = 0
    reasons = []

    for feature, config in RISK_WEIGHTS.items():
        val = features.get(feature)

        if feature == "is_https":
            if not val:
                score += config["weight"]
                reasons.append(config["reason"])

        
        elif feature == "suspicious_keywords_found":
            if val:
                score += config["weight"]
                reasons.append(config["reason"].format(values=", ".join(val)))

        
        elif "threshold" in config:
            if isinstance(val, (int, float)) and val > config["threshold"]:
                score += config["weight"]
                reasons.append(config["reason"])


        elif val is True:
            score += config["weight"]
            reasons.append(config["reason"])

    final_score = max(0, min(score, 100))

    return {
        "risk_score":    final_score,
        "risk_category": get_risk_category(final_score),
        "reasons":       reasons,
    }



def analyze_url(url: str) -> dict:
    """
    Lightweight wrapper used by the Streamlit UI.
    Extracts simple features inline (no WHOIS / SSL call for speed).
    For deep analysis the full url_analyzer.extract_features() pipeline
    can replace this function.
    """
    SHORTENERS = ["bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly",
                  "cutt.ly", "rebrand.ly", "is.gd", "buff.ly"]
    KEYWORDS   = ["login", "bank", "verify", "secure", "account",
                  "otp", "payment", "update", "confirm", "signin"]

    try:
        parsed_domain = url.split('/')[2] if '://' in url else url.split('/')[0]
    except IndexError:
        parsed_domain = url

    features = {
        "url":                      url,
        "is_https":                 url.startswith("https://"),
        "has_ip_address":           bool(re.search(r"https?://\d+\.\d+\.\d+\.\d+", url)),
        "is_shortened":             any(s in url for s in SHORTENERS),
        "is_typosquatted":          any(c in parsed_domain for c in ['0', '1', '3', '5', '@']),
        "suspicious_keywords_found": [kw for kw in KEYWORDS if kw in url.lower()],
        "special_char_count":       sum(1 for c in url if not c.isalnum() and c not in '/:.-_?=&%#'),
        "num_subdomains":           max(0, parsed_domain.count('.') - 1),
    }

    result = calculate_risk_score(features)
    result["url"] = url
    return result
