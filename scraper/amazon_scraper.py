"""
Amazon India Product Scraper.

Scrapes furniture product data from amazon.in.
Uses search result pages with category-specific queries.

Note: Amazon has aggressive anti-bot measures. This scraper uses
rotating headers and polite delays. If blocked, it gracefully
returns empty results.
"""

import re
import json
import logging
from typing import Optional

from bs4 import BeautifulSoup

from scraper.base import get_session, get_headers, fetch_page, clean_price, clean_text, logger
from scraper.affiliate import make_affiliate_url

# ──────────────────────────────────────────────
# Known furniture brands (Amazon India) — 200+
# ──────────────────────────────────────────────
_KNOWN_BRANDS = {
    # Major Indian furniture
    "nilkamal", "godrej", "godrej interio", "duroflex", "sleepyhead", "wakefit",
    "urban ladder", "hometown", "pepperfry", "royal oak", "damro", "durian",
    "zuari", "evok", "housefull", "stylespa", "stellar", "hometown",
    "saraf furniture", "wooden street", "induscraft", "lakdi", "apkainterior",
    "casacraft", "forzza", "decornation", "home edge", "furniture affair",
    # Amazon private labels
    "amazon brand", "amazon basics", "solimo", "amazon brand - solimo",
    "amazon brand - umi", "umi",
    # Flipkart brands
    "flipkart perfect homes", "perfect homes",
    # Sofa/seating brands
    "seventh heaven", "adorn india", "bharat lifestyle", "torque", "aart store",
    "craft city", "furnish craft", "vintej home", "suncrown", "woodsworth",
    "casastyle", "furny", "dia", "sleepyhug", "nattnak", "milan",
    "allie wood", "primowood", "hometown", "caspian",
    "ganpati arts", "greenforest", "petrolia", "woodkoof", "cherry wood",
    "the m m furniture store", "m m furniture", "strata furniture", "strata",
    "divine trends", "about space", "anton", "home elements", "metalmastery",
    "callas", "callas trinity", "spacewood", "trevi furniture",
    # Bed/mattress brands
    "kurlon", "sleepwell", "centuary", "springfit", "sunday",
    "the sleep company", "sleep company", "dr ortho", "coirfit", "king koil",
    "magniflex", "emma", "restolex", "peps", "amore", "boston",
    "beaatho", "bvslf", "fancymart",
    # Lighting brands
    "wipro", "wipro lighting", "philips", "havells", "crompton", "bajaj",
    "syska", "orient", "surya roshni", "eveready", "halonix", "murphy",
    "eglo", "corvi", "brightstar", "led fantasma",
    # Decor brands
    "decorglance", "art street", "random", "wall1ders", "sehaz artworks",
    "satyam kraft", "bikri kendra", "kotart", "u green", "glassco",
    "home berry", "paper plane design", "wallmantra",
    # Home textile brands
    "ikea", "home centre", "fabindia", "spaces", "bombay dyeing",
    "welspun", "trident", "raymond", "swayam", "story@home", "story at home",
    # Storage/office brands
    "cello", "varmora", "supreme", "italica", "jfa", "featherlite",
    "durian", "hof", "green soul",
}

# Words that are NOT brands — materials, product types, descriptors
_NOT_BRAND = {
    # Materials
    "sheesham", "engineered", "wooden", "wood", "teak", "mango", "acacia",
    "bamboo", "metal", "iron", "steel", "wrought", "brass", "chrome",
    "plastic", "fabric", "leather", "leatherette", "velvet", "cotton",
    "linen", "glass", "ceramic", "marble", "granite", "resin", "rattan",
    "pine", "oak", "walnut", "rosewood", "rubber", "plywood", "mdf",
    "solid", "hardwood", "softwood",
    # Product types
    "sofa", "bed", "table", "desk", "chair", "lamp", "light", "shelf",
    "wardrobe", "cabinet", "mirror", "curtain", "curtains", "rug", "stool",
    "bench", "mattress", "bookshelf", "bookcase", "rack", "unit", "stand",
    "ottoman", "cushion", "pillow", "vase", "clock", "frame", "plant",
    "holder", "recliner", "organizer", "drawer", "dresser", "almirah",
    "diwan", "palang", "cot", "divan", "futon", "storage", "almirah",
    "showcase", "sideboard", "trolley", "cart", "basket",
    "wall", "floor", "ceiling", "pendant", "hanging", "standing",
    "study", "office", "computer", "laptop", "writing", "dining",
    "coffee", "side", "console", "bar", "center", "centre",
    # Descriptors
    "modern", "contemporary", "traditional", "vintage", "antique",
    "portable", "foldable", "adjustable", "collapsible", "convertible",
    "luxury", "premium", "heavy", "duty", "industrial", "rustic",
    "minimalist", "elegant", "decorative", "ornamental",
    # Sizes, quantities, numbers as words
    "king", "queen", "single", "double", "twin", "full",
    "small", "medium", "large", "big", "mini", "compact",
    "size", "sized", "seater", "door", "doors", "drawer", "drawers",
    "tier", "layer", "layers", "shelf", "shelves", "compartment",
    "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "twelve", "first", "second", "third",
    # Colors
    "black", "white", "grey", "gray", "brown", "blue", "red", "green",
    "pink", "beige", "cream", "ivory", "orange", "yellow", "purple",
    "gold", "golden", "silver", "copper", "bronze", "natural", "dark",
    "light", "multi", "multicolor", "multicolour", "transparent",
    # Prepositions / connectors
    "for", "with", "without", "and", "or", "by", "at", "in", "on",
    "of", "to", "from", "near", "above", "below", "under",
    # Generic descriptors
    "the", "a", "an", "new", "best", "super", "extra", "pure",
    "classic", "royal", "quality", "original", "genuine", "imported",
    "branded", "set", "pair", "pack", "piece", "bunch",
    "home", "furniture", "decor", "decoration", "interior", "room",
    "living", "bedroom", "bathroom", "kitchen", "outdoor", "indoor",
    "hallway", "entryway", "corridor", "balcony", "garden", "patio",
    "led", "smart", "digital", "automatic", "manual",
    # Feature words
    "compatible", "touch", "control", "remote", "wireless", "bluetooth",
    "waterproof", "dustproof", "scratch", "resistant", "proof",
    "feet", "foot", "inch", "inches", "long", "short", "tall", "wide",
    "thick", "thin", "deep", "narrow", "round", "square", "oval",
    "rectangular", "circular", "flat", "curved",
    "box", "finish", "finished", "polished", "matte", "glossy",
    "color", "colour", "colored", "coloured", "printed", "painted",
    "tripod", "telescopic", "extendable", "expandable", "platform",
    "sectional", "modular", "convertible", "reversible", "stackable",
    "chairs", "sofas", "beds", "tables", "lamps", "lights", "shelves",
    "pieces", "units", "items", "options", "types",
    # Furniture parts
    "headboard", "footboard", "armrest", "backrest", "cushioned",
    "upholstered", "tufted", "mounted", "wall-mounted", "floating", "hanging",
    "standing", "folding", "sliding", "rotating", "swivel",
    # More decor / misc
    "artificial", "natural", "real", "fake", "faux", "synthetic",
    "rose", "flower", "flowers", "bouquet", "bunch",
    "fixture", "shade", "bulb", "canopy", "cover", "covers",
    "string", "strip", "panel", "tile", "tiles",
}

_PRODUCT_WORDS_RE = re.compile(
    r"\b(\d+[\s-]?seater|sofa|bed|table|desk|chair|lamp|light|shelf|"
    r"wardrobe|cabinet|mirror|curtains?|rug|stool|bench|mattress|"
    r"bookshelf|tv\s*unit|shoe\s*rack|storage|organizer|recliner|"
    r"ottoman|cushion|pillow|vase|clock|frame|plant|holder|"
    r"king\s*size|queen\s*size|single\s*bed|double\s*bed|king|queen|"
    r"for\s+|with\s+|set\s+of|\d+\s*inch|\d+\s*cm|\d+\s*mm|\d+\s*ft|"
    r"foldable|adjustable|portable|modern|wooden|metal|fabric|"
    r"engineered|sheesham|solid\s*wood|teak|mango\s*wood)\b",
    re.IGNORECASE,
)


def _extract_brand_from_title(title: str) -> str:
    """
    Extract brand name from an Amazon product title.

    Strategy (in order):
        1. Match against 200+ known brands (longest match first)
        2. Take words before first product keyword, validate they're not materials/types
        3. Scan full title for known brand appearing anywhere (e.g. after "by")
        4. First capitalized word(s) if they pass the not-a-brand blocklist
    """
    if not title:
        return "Unknown"

    title_clean = re.sub(r"[®™©]", "", title).strip()
    title_lower = title_clean.lower()

    # ── Strategy 1: Known brand at start of title (longest match wins) ──
    for brand in sorted(_KNOWN_BRANDS, key=len, reverse=True):
        if title_lower.startswith(brand):
            return title_clean[:len(brand)].strip()

    # ── Strategy 2: Known brand anywhere in title ──
    # Catches "by BrandName", "from BrandName", or brand in middle
    for brand in sorted(_KNOWN_BRANDS, key=len, reverse=True):
        idx = title_lower.find(brand)
        if idx >= 0:
            return title_clean[idx:idx + len(brand)].strip()

    def _is_valid_brand(name: str) -> bool:
        """Check if a candidate string looks like a real brand name."""
        if not name or len(name) < 3:
            return False
        clean = name.strip(" -|,.'\"")
        if len(clean) < 3:
            return False
        stripped = re.sub(r"[^a-zA-Z0-9 ]", "", clean).strip()
        if len(stripped) < 2:
            return False
        words = stripped.lower().split()
        if all(w in _NOT_BRAND for w in words):
            return False
        if not any(c.isalpha() for c in stripped):
            return False
        return True

    # ── Strategy 3: Words before first product-type keyword ──
    match = _PRODUCT_WORDS_RE.search(title_clean)
    if match and match.start() > 2:
        candidate = title_clean[:match.start()].strip().rstrip(" -|,")
        words = candidate.split()
        # Strip leading and trailing noise
        while words and words[0].lower().strip(",-.'\"") in _NOT_BRAND:
            words.pop(0)
        while words and words[-1].lower().strip(",-.'\"") in _NOT_BRAND:
            words.pop()
        if 1 <= len(words) <= 3:
            candidate = " ".join(w.strip(",-") for w in words)
            if _is_valid_brand(candidate):
                return candidate

    # ── Strategy 4: First non-noise capitalized word ──
    words = title_clean.split()
    start = 0
    while start < len(words) and (
        words[start].lower().strip(",-.'\"") in _NOT_BRAND
        or not any(c.isalpha() for c in words[start])
        or len(words[start].strip(",-")) < 2
    ):
        start += 1

    if start < len(words):
        w = words[start].strip(",-")
        if _is_valid_brand(w) and w[0].isalpha():
            # Take second word too if it looks like part of brand
            if start + 1 < len(words):
                w2 = words[start + 1].strip(",-")
                if (_is_valid_brand(w2) and w2[0].isupper()
                        and not _PRODUCT_WORDS_RE.match(w2)):
                    combo = f"{w} {w2}"
                    if _is_valid_brand(combo):
                        return combo
            return w

    return "Unknown"

# ──────────────────────────────────────────────
# Amazon India search URLs
# ──────────────────────────────────────────────
AMAZON_SEARCHES = {
    "sofa": [
        "https://www.amazon.in/s?k=sofa+set&i=furniture&rh=p_36%3A500000-10000000",
        "https://www.amazon.in/s?k=3+seater+sofa&i=furniture",
        "https://www.amazon.in/s?k=L+shape+sofa&i=furniture",
    ],
    "bed": [
        "https://www.amazon.in/s?k=king+size+bed+with+storage&i=furniture",
        "https://www.amazon.in/s?k=queen+size+bed&i=furniture",
        "https://www.amazon.in/s?k=single+bed+with+storage&i=furniture",
    ],
    "lighting": [
        "https://www.amazon.in/s?k=ceiling+light+for+living+room&i=lighting",
        "https://www.amazon.in/s?k=table+lamp+for+bedroom&i=lighting",
        "https://www.amazon.in/s?k=floor+lamp+modern&i=lighting",
    ],
    "table": [
        "https://www.amazon.in/s?k=study+table+with+storage&i=furniture",
        "https://www.amazon.in/s?k=coffee+table+for+living+room&i=furniture",
        "https://www.amazon.in/s?k=dining+table+set+4+seater&i=furniture",
    ],
    "decor": [
        "https://www.amazon.in/s?k=wall+mirror+decorative&i=furniture",
        "https://www.amazon.in/s?k=curtains+for+living+room&i=furniture",
        "https://www.amazon.in/s?k=flower+vase+for+home+decoration&i=furniture",
    ],
    "storage": [
        "https://www.amazon.in/s?k=bookshelf+for+home&i=furniture",
        "https://www.amazon.in/s?k=wardrobe+for+bedroom&i=furniture",
        "https://www.amazon.in/s?k=tv+unit+for+living+room&i=furniture",
    ],
}


def _parse_amazon_results(html: str, product_type: str) -> list[dict]:
    """Parse Amazon search results page HTML."""
    products = []
    soup = BeautifulSoup(html, "html.parser")

    # Amazon product cards
    cards = soup.select("[data-component-type='s-search-result']")

    if not cards:
        # Fallback selectors
        cards = soup.select(".s-result-item[data-asin]")

    for card in cards:
        try:
            asin = card.get("data-asin", "")
            if not asin or asin == "":
                continue

            # Product name
            title_el = card.select_one("h2 a span, h2 span, .a-text-normal")
            name = clean_text(title_el.get_text()) if title_el else ""
            if not name or len(name) < 5:
                continue

            # Price
            price = None
            price_el = card.select_one(".a-price .a-offscreen, .a-price-whole")
            if price_el:
                price = clean_price(price_el.get_text())

            if not price or price < 100:
                continue

            # Image
            img_el = card.select_one("img.s-image, img[data-image-latency='s-product-image']")
            image_url = img_el.get("src", "") if img_el else ""

            # Product URL
            link_el = card.select_one("h2 a, a.a-link-normal[href*='/dp/']")
            product_url = ""
            if link_el:
                href = link_el.get("href", "")
                if href.startswith("/"):
                    product_url = "https://www.amazon.in" + href
                elif href.startswith("http"):
                    product_url = href
                # Clean tracking params
                product_url = product_url.split("/ref=")[0]

            # Rating
            rating_el = card.select_one(".a-icon-alt")
            rating = ""
            if rating_el:
                rating = clean_text(rating_el.get_text())

            # Brand — extract from title (Amazon India has no separate brand element)
            brand = _extract_brand_from_title(name)

            # Dimensions — multiple patterns from title and card text
            dimensions = ""
            card_text = card.get_text()

            # Pattern 1: "72 x 36 x 18 cm" or "72x36"
            dim_match = re.search(
                r"(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)(?:\s*[xX×]\s*(\d+(?:\.\d+)?))?(?:\s*(?:cm|inch|inches|in|mm))?",
                card_text,
            )
            if dim_match:
                parts = [g for g in dim_match.groups() if g]
                unit = "cm"
                unit_match = re.search(r"[xX×]\s*\d+(?:\.\d+)?\s*(cm|inch|inches|in|mm)", card_text)
                if unit_match:
                    unit = unit_match.group(1)
                dimensions = " x ".join(parts) + f" {unit}"

            # Pattern 2: "Width 120cm, Depth 60cm, Height 75cm"
            if not dimensions:
                w = re.search(r"(?:width|W)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:cm|in)", card_text, re.I)
                d = re.search(r"(?:depth|D)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:cm|in)", card_text, re.I)
                h = re.search(r"(?:height|H)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:cm|in)", card_text, re.I)
                parts = []
                if w: parts.append(w.group(1))
                if d: parts.append(d.group(1))
                if h: parts.append(h.group(1))
                if parts:
                    dimensions = " x ".join(parts) + " cm"

            # Pattern 3: "6x5 feet" / "6ft x 4ft"
            if not dimensions:
                ft_match = re.search(
                    r"(\d+(?:\.\d+)?)\s*(?:ft|feet)?\s*[xX×]\s*(\d+(?:\.\d+)?)\s*(?:ft|feet)",
                    card_text,
                )
                if ft_match:
                    parts = [g for g in ft_match.groups() if g]
                    dimensions = " x ".join(parts) + " feet"

            products.append({
                "product_id": f"AMZ_{asin}",
                "product_name": name,
                "brand": brand,
                "price_value": price,
                "price_currency": "INR",
                "product_type": product_type,
                "image_url": image_url,
                "affiliate_url": make_affiliate_url(product_url, source="amazon.in", asin=asin),
                "source_url": product_url,
                "dimensions": dimensions,
                "rating": rating,
                "source": "amazon.in",
            })

        except Exception as e:
            logger.debug(f"Failed to parse Amazon card: {e}")
            continue

    return products


def scrape_amazon(max_per_category: int = 100) -> list[dict]:
    """
    Scrape products from Amazon India with pagination.

    Args:
        max_per_category: Target products per search URL (paginated).

    Returns:
        List of product dicts.
    """
    logger.info("Starting Amazon India scraper (with pagination)...")
    session = get_session()
    all_products = []
    seen_ids = set()

    for product_type, urls in AMAZON_SEARCHES.items():
        for base_url in urls:
            collected_for_url = 0
            max_pages = (max_per_category // 20) + 1  # ~20-30 per page

            for page in range(1, max_pages + 1):
                url = f"{base_url}&page={page}" if page > 1 else base_url
                logger.info(f"Scraping Amazon [{product_type}] page {page}: {url[:80]}...")
                html = fetch_page(url, session=session, delay=3.0)
                if not html:
                    logger.warning(f"  → Failed to fetch page {page} (possibly blocked)")
                    break

                products = _parse_amazon_results(html, product_type)

                if not products:
                    logger.info(f"  → No products on page {page}, stopping pagination")
                    break

                new_count = 0
                for p in products:
                    pid = p["product_id"]
                    if pid not in seen_ids:
                        seen_ids.add(pid)
                        all_products.append(p)
                        collected_for_url += 1
                        new_count += 1

                logger.info(f"  → Page {page}: {new_count} new products (url total: {collected_for_url}, grand total: {len(all_products)})")

                if collected_for_url >= max_per_category:
                    break

    logger.info(f"Amazon scraping complete: {len(all_products)} products")
    return all_products
