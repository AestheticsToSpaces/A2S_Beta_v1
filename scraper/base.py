"""
Base scraper with shared utilities: headers rotation, retry logic,
rate limiting, and data normalization.
"""

import time
import random
import logging
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Rotating User-Agents to avoid detection
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]


def get_session() -> requests.Session:
    """Create a requests session with retry logic and connection pooling."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_headers() -> dict:
    """Return randomized browser headers."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8,hi;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }


def fetch_page(url: str, session: Optional[requests.Session] = None, delay: float = 1.5) -> Optional[str]:
    """
    Fetch a page with rate limiting and error handling.

    Args:
        url: URL to fetch.
        session: Optional requests session (creates new if None).
        delay: Seconds to wait before request (rate limiting).

    Returns:
        HTML content as string, or None on failure.
    """
    time.sleep(delay + random.uniform(0.5, 1.5))  # Polite delay

    sess = session or get_session()
    headers = get_headers()

    try:
        resp = sess.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        logger.info(f"OK {resp.status_code} — {url[:80]}")
        return resp.text
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP {e.response.status_code} — {url[:80]}")
    except requests.exceptions.ConnectionError:
        logger.warning(f"Connection error — {url[:80]}")
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout — {url[:80]}")
    except Exception as e:
        logger.warning(f"Error fetching {url[:80]}: {e}")

    return None


def clean_price(text: str) -> Optional[float]:
    """Extract numeric price from text like '₹12,990', 'Rs. 12990', etc."""
    import re
    if not text:
        return None
    # Remove currency symbols, commas, spaces
    cleaned = re.sub(r"[₹,\s]", "", str(text))
    cleaned = re.sub(r"^(Rs\.?|INR)\s*", "", cleaned)
    # Extract first number
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    return float(match.group(1)) if match else None


def clean_text(text: str) -> str:
    """Strip and normalize whitespace in text."""
    if not text:
        return ""
    import re
    return re.sub(r"\s+", " ", str(text)).strip()
