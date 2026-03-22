"""
Affiliate Link Generator.

Converts raw product URLs into monetized affiliate links for:
    - Amazon India (Associates Program — tag parameter)
    - Flipkart (Affiliate Program — affid parameter)
    - IKEA India (UTM tracking — no official affiliate program)

How affiliate links work:
    Amazon:   https://www.amazon.in/dp/B0XXXXX?tag=yourtag-21
              When a user clicks and buys, you earn 1-10% commission.

    Flipkart: https://www.flipkart.com/product-slug/p/itm123?affid=yourid
              Flipkart tracks the click and pays commission on purchase.

    IKEA:     No official India affiliate program. We append UTM params
              for click tracking. Can be swapped for CJ/Impact links later.

Usage:
    from scraper.affiliate import make_affiliate_url
    aff_url = make_affiliate_url("https://www.amazon.in/dp/B08XYZ", source="amazon.in")
"""

from __future__ import annotations

import re
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs, urljoin

from config import AMAZON_AFFILIATE_TAG, FLIPKART_AFFILIATE_ID, IKEA_TRACKING_PARAM


def make_affiliate_url(raw_url: str, source: str = "", asin: str = "") -> str:
    """
    Convert a raw product URL into an affiliate URL.

    Args:
        raw_url:  The original product page URL.
        source:   One of "amazon.in", "flipkart.com", "ikea.com".
        asin:     Amazon ASIN (optional, used to build clean short link).

    Returns:
        Affiliate URL string. Falls back to raw_url if conversion fails.
    """
    if not raw_url:
        return ""

    url = raw_url.strip()

    try:
        if source == "amazon.in" or "amazon.in" in url:
            return _amazon_affiliate(url, asin)
        elif source == "flipkart.com" or "flipkart.com" in url:
            return _flipkart_affiliate(url)
        elif source == "ikea.com" or "ikea.com" in url:
            return _ikea_affiliate(url)
    except Exception:
        pass

    return url


def _amazon_affiliate(url: str, asin: str = "") -> str:
    """
    Build Amazon affiliate link.

    Strategy:
        1. If ASIN is available, build a clean short link: amazon.in/dp/ASIN?tag=XXX
        2. Otherwise, append ?tag=XXX to existing URL (strip old tracking)

    Amazon Associates link format:
        https://www.amazon.in/dp/B08EXAMPLE?tag=yourtag-21
    """
    tag = AMAZON_AFFILIATE_TAG
    if not tag:
        return url

    # Try to extract ASIN from URL if not provided
    if not asin:
        asin_match = re.search(r"/dp/([A-Z0-9]{10})", url)
        if asin_match:
            asin = asin_match.group(1)

    # Build clean short affiliate link with ASIN
    if asin:
        return f"https://www.amazon.in/dp/{asin}?tag={tag}"

    # Fallback: strip existing ref/tracking params, append tag
    clean = re.split(r"[?&](?:ref|tag|linkCode|camp|creative)=", url)[0]
    separator = "&" if "?" in clean else "?"
    return f"{clean}{separator}tag={tag}"


def _flipkart_affiliate(url: str) -> str:
    """
    Build Flipkart affiliate link.

    Strategy:
        Append affid parameter to the product URL.

    Flipkart Affiliate link format:
        https://www.flipkart.com/product-name/p/itmXXXXX?affid=yourid&affExtParam1=a2s
    """
    affid = FLIPKART_AFFILIATE_ID
    if not affid:
        return url

    # Strip existing affiliate params
    clean = re.split(r"[&?](?:affid|affExtParam)", url)[0]

    separator = "&" if "?" in clean else "?"
    return f"{clean}{separator}affid={affid}&affExtParam1=a2s_agent"


def _ikea_affiliate(url: str) -> str:
    """
    Build IKEA tracking link.

    IKEA India has no official affiliate program. We append UTM parameters
    for analytics tracking. Replace with CJ Affiliate / Impact links
    when available.

    Format:
        https://www.ikea.com/in/en/p/product-name-12345678/?utm_source=a2s&utm_medium=affiliate
    """
    tracking = IKEA_TRACKING_PARAM
    if not tracking:
        return url

    # Strip existing UTM params
    clean = re.split(r"[?&]utm_", url)[0]

    separator = "&" if "?" in clean else "?"
    return f"{clean}{separator}{tracking}"


def convert_existing_urls(products: list[dict]) -> list[dict]:
    """
    Batch-convert all product URLs in a list of product dicts.

    Updates both 'affiliate_url' (monetized) and keeps 'source_url' (original).

    Args:
        products: List of product dicts with 'source_url' and 'source' keys.

    Returns:
        Same list with 'affiliate_url' updated to affiliate links.
    """
    for p in products:
        source = p.get("source", "")
        raw_url = p.get("source_url") or p.get("affiliate_url", "")
        asin = ""

        # Extract ASIN from product_id for Amazon
        pid = p.get("product_id", "")
        if pid.startswith("AMZ_"):
            asin = pid.replace("AMZ_", "")

        # Keep original URL as source_url
        if raw_url:
            p["source_url"] = raw_url
            p["affiliate_url"] = make_affiliate_url(raw_url, source=source, asin=asin)

    return products
