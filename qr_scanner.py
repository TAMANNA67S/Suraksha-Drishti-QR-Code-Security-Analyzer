# qr_scanner.py — QR Code Scanning Module
# LOCATION: app/qr_scanner.py
import cv2
import numpy as np
import re
import logging
from pathlib import Path
from typing import List
from PIL import Image

logger = logging.getLogger(__name__)

# =========================
# IMAGE LOADER
# =========================
def load_image_from_upload(uploaded_file) -> np.ndarray:
    """Converts a Streamlit UploadedFile to an OpenCV BGR ndarray."""
    image = Image.open(uploaded_file).convert('RGB')
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def load_image_from_path(path: str) -> np.ndarray:
    """Loads an image from disk path into an OpenCV BGR ndarray."""
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"Could not load image from: {path}")
    return img


# =========================
# QR DECODER (multi-stage)
# =========================
def decode_qr(image_bgr: np.ndarray) -> List[str]:
    """
    Multi-stage QR decode for maximum coverage.
    Stage 1 — raw image.
    Stage 2 — grayscale + Gaussian blur + Otsu threshold.
    Stage 3 — sharpened image.
    """
    detector = cv2.QRCodeDetector()

    def _attempt(img) -> List[str]:
        retval, decoded_info, _, _ = detector.detectAndDecodeMulti(img)
        if retval and decoded_info:
            return [d for d in decoded_info if d.strip()]
        return []

    # Stage 1 — raw
    results = _attempt(image_bgr)
    if results:
        return results

    # Stage 2 — pre-process
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    results = _attempt(thresh)
    if results:
        return results

    # Stage 3 — sharpen
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    results = _attempt(sharpened)
    return results


# =========================
# URL EXTRACTOR
# =========================
def extract_url(decoded_data: List[str]) -> List[str]:
    """Extracts unique, valid URLs from decoded QR text."""
    if not decoded_data:
        return []
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:[/\w\.\-\?=&%#]*)?'
    found = []
    for data in decoded_data:
        found.extend(re.findall(url_pattern, data))
        # Also pass raw text that looks like a domain without scheme
        if not found and re.match(r'^[\w\-]+\.[\w\-]+', data):
            found.append(f"http://{data.strip()}")
    return list(set(found))


# =========================
# HIGH-LEVEL API
# =========================
def scan_qr(image_path: str) -> List[str]:
    """
    Loads an image from disk, decodes all QR codes, returns extracted URLs.
    Used by main.py after writing the temp file.
    """
    try:
        image_bgr = load_image_from_path(image_path)
    except FileNotFoundError as e:
        logger.error(e)
        return []

    decoded = decode_qr(image_bgr)
    if not decoded:
        logger.warning("No QR codes detected in image.")
        return []

    urls = extract_url(decoded)
    logger.info(f"Extracted {len(urls)} URL(s) from QR code.")
    return urls