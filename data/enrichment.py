"""
Data Enrichment Engine — Extracts attributes from product names.

Takes the raw scraped dataset and adds:
    - color          (extracted from product name)
    - material       (extracted from product name)
    - room_type      (inferred from product name + product_type)
    - style          (inferred from product name keywords)
    - seating        (e.g., "3 seater", "L shape")
    - price_tier     (budget / mid / premium / luxury based on price)
    - sub_type       (more specific type: "coffee table", "floor lamp", etc.)
    - use_case       (functional tags: "foldable", "adjustable", "storage", etc.)

Philosophy: extract ONLY what's genuinely in the product name. No guessing.
"""

from __future__ import annotations
import re
import pandas as pd


# ═══════════════════════════════════════════════════
# COLOR EXTRACTION
# ═══════════════════════════════════════════════════
_COLOR_MAP = {
    # Basic colors
    "red": "red", "crimson": "red", "maroon": "red", "burgundy": "red", "wine": "red",
    "scarlet": "red", "cherry": "red", "ruby": "red",
    "blue": "blue", "navy": "blue", "cobalt": "blue", "azure": "blue",
    "indigo": "blue", "teal": "blue", "turquoise": "blue", "aqua": "blue",
    "royal blue": "blue", "sky blue": "blue", "dark blue": "blue",
    "green": "green", "olive": "green", "emerald": "green", "sage": "green",
    "mint": "green", "forest green": "green", "lime": "green", "moss": "green",
    "dark green": "green", "light green": "green",
    "yellow": "yellow", "mustard": "yellow", "gold": "yellow", "amber": "yellow",
    "lemon": "yellow", "golden": "yellow",
    "orange": "orange", "tangerine": "orange", "peach": "orange", "coral": "orange",
    "rust": "orange", "burnt orange": "orange",
    "purple": "purple", "violet": "purple", "lavender": "purple", "plum": "purple",
    "mauve": "purple", "lilac": "purple", "magenta": "purple",
    "pink": "pink", "rose": "pink", "blush": "pink", "salmon": "pink", "fuchsia": "pink",
    "hot pink": "pink",
    "black": "black", "charcoal": "black", "ebony": "black", "jet black": "black",
    "white": "white", "ivory": "white", "cream": "white", "off-white": "white",
    "off white": "white", "pearl": "white", "snow white": "white",
    "grey": "grey", "gray": "grey", "silver": "grey", "ash": "grey", "slate": "grey",
    "graphite": "grey", "dark grey": "grey", "light grey": "grey", "medium grey": "grey",
    "brown": "brown", "chocolate": "brown", "tan": "brown", "beige": "brown",
    "khaki": "brown", "coffee": "brown", "caramel": "brown", "mocha": "brown",
    "espresso": "brown", "walnut": "brown", "chestnut": "brown", "cocoa": "brown",
    "taupe": "brown", "natural": "brown", "mahogany": "brown",
    "multicolor": "multicolor", "multicolour": "multicolor", "multi-color": "multicolor",
    "multi colour": "multicolor", "multi color": "multicolor",
    "printed": "multicolor", "floral": "multicolor", "rainbow": "multicolor",
}

# Sort by length (longest first) so "dark blue" matches before "blue"
_COLOR_PATTERNS = sorted(_COLOR_MAP.keys(), key=len, reverse=True)


def _extract_color(name: str) -> str | None:
    """Extract color from product name using word-boundary matching."""
    name_lower = name.lower()
    for pattern in _COLOR_PATTERNS:
        # Word boundary: pattern must be surrounded by non-alpha chars or string edges
        regex = r'(?:^|[^a-z])' + re.escape(pattern) + r'(?:$|[^a-z])'
        if re.search(regex, name_lower):
            return _COLOR_MAP[pattern]
    return None


# ═══════════════════════════════════════════════════
# MATERIAL EXTRACTION
# ═══════════════════════════════════════════════════
_MATERIAL_MAP = {
    # Wood types
    "sheesham": "wood", "sheesham wood": "wood", "teak": "wood", "teak wood": "wood",
    "oak": "wood", "pine": "wood", "acacia": "wood", "mango wood": "wood",
    "bamboo": "wood", "wooden": "wood", "solid wood": "wood", "hardwood": "wood",
    "plywood": "engineered wood", "engineered wood": "engineered wood",
    "particle board": "engineered wood", "mdf": "engineered wood",
    "laminated": "engineered wood", "veneer": "engineered wood",
    # Metal
    "metal": "metal", "iron": "metal", "steel": "metal", "stainless steel": "metal",
    "brass": "metal", "copper": "metal", "aluminium": "metal", "aluminum": "metal",
    "wrought iron": "metal", "chrome": "metal", "powder coated": "metal",
    # Fabric types
    "fabric": "fabric", "cotton": "fabric", "linen": "fabric", "polyester": "fabric",
    "jute": "fabric", "canvas": "fabric", "chenille": "fabric", "silk": "fabric",
    "microfiber": "fabric", "upholstered": "fabric", "woven": "fabric",
    # Special fabrics
    "velvet": "velvet", "suede": "velvet",
    "leather": "leather", "leatherette": "leather", "faux leather": "leather",
    "pu leather": "leather", "rexine": "leather",
    # Glass / Ceramic
    "glass": "glass", "tempered glass": "glass", "frosted glass": "glass",
    "ceramic": "ceramic", "porcelain": "ceramic",
    # Plastic / Resin
    "plastic": "plastic", "polypropylene": "plastic", "abs": "plastic",
    "acrylic": "plastic", "resin": "plastic", "fiberglass": "plastic",
    # Natural
    "rattan": "rattan", "wicker": "rattan", "cane": "rattan",
    "marble": "marble", "stone": "stone", "granite": "stone",
    # Foam
    "foam": "foam", "memory foam": "foam", "hr foam": "foam",
}

_MATERIAL_PATTERNS = sorted(_MATERIAL_MAP.keys(), key=len, reverse=True)


def _extract_material(name: str) -> str | None:
    """Extract primary material from product name."""
    name_lower = name.lower()
    for pattern in _MATERIAL_PATTERNS:
        regex = r'(?:^|[^a-z])' + re.escape(pattern) + r'(?:$|[^a-z])'
        if re.search(regex, name_lower):
            return _MATERIAL_MAP[pattern]
    return None


# ═══════════════════════════════════════════════════
# ROOM TYPE INFERENCE
# ═══════════════════════════════════════════════════
_ROOM_KEYWORDS = {
    "bedroom": [
        "bedroom", "bedside", "bed side", "nightstand", "night stand",
        "dressing", "wardrobe", "mattress", "pillow", "bedspread",
        "blanket", "duvet", "quilt", "bed sheet", "bedsheet",
    ],
    "living_room": [
        "living room", "living-room", "drawing room", "lounge",
        "tv unit", "tv stand", "tv cabinet", "entertainment",
        "coffee table", "center table", "centre table", "sofa",
        "couch", "recliner", "floor lamp", "accent",
    ],
    "dining_room": [
        "dining", "dinner", "kitchen", "bar stool", "bar table",
        "bar cabinet", "crockery", "cutlery",
    ],
    "study": [
        "study", "office", "computer", "laptop", "work desk",
        "workstation", "writing desk", "book shelf", "bookshelf",
        "bookcase", "book rack", "file cabinet",
    ],
    "kids_room": [
        "kids", "children", "child", "baby", "nursery", "toddler",
        "bunk bed", "bunk", "cartoon", "playroom",
    ],
    "bathroom": [
        "bathroom", "bath", "shower", "toilet", "washroom",
        "towel", "bath mat", "washcloth",
    ],
    "outdoor": [
        "outdoor", "garden", "balcony", "patio", "terrace",
        "adirondack", "lawn", "poolside",
    ],
}


def _infer_room_type(name: str, product_type: str) -> str | None:
    """Infer room type from product name and type."""
    name_lower = name.lower()

    # Check explicit room mentions
    for room, keywords in _ROOM_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return room

    # Fallback: infer from product_type
    type_room = {
        "bed": "bedroom",
        "textile": "bedroom",
    }
    return type_room.get(str(product_type).lower())


# ═══════════════════════════════════════════════════
# STYLE INFERENCE
# ═══════════════════════════════════════════════════
_STYLE_KEYWORDS = {
    "modern": [
        "modern", "contemporary", "minimalist", "minimal", "sleek",
        "nordic", "scandinavian", "mid-century", "mid century",
        "geometric", "abstract", "clean lines",
    ],
    "classic": [
        "classic", "traditional", "antique", "vintage", "retro",
        "victorian", "baroque", "colonial", "heritage", "ornate",
    ],
    "industrial": [
        "industrial", "loft", "pipe", "raw", "exposed",
        "factory", "warehouse", "urban",
    ],
    "rustic": [
        "rustic", "farmhouse", "country", "cottage", "distressed",
        "reclaimed", "weathered", "barn",
    ],
    "ethnic": [
        "ethnic", "bohemian", "boho", "moroccan", "indian",
        "mandala", "tribal", "rajasthani", "handcrafted",
        "handicraft", "artisan",
    ],
    "luxury": [
        "luxury", "premium", "designer", "chesterfield",
        "royal", "imperial", "elegant", "opulent",
    ],
    "functional": [
        "foldable", "folding", "portable", "compact",
        "adjustable", "convertible", "multipurpose", "multi-purpose",
        "space saving", "space-saving",
    ],
}


def _infer_style(name: str) -> str | None:
    """Infer design style from product name."""
    name_lower = name.lower()
    for style, keywords in _STYLE_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return style
    return None


# ═══════════════════════════════════════════════════
# SUB-TYPE EXTRACTION
# ═══════════════════════════════════════════════════
_SUB_TYPE_MAP = {
    # Sofa sub-types
    "sofa": {
        "sofa cum bed": "sofa cum bed", "sofa bed": "sofa cum bed",
        "recliner": "recliner", "l shape": "l-shape sofa", "l-shape": "l-shape sofa",
        "sectional": "sectional sofa", "loveseat": "loveseat", "futon": "futon",
        "chaise": "chaise lounge", "ottoman": "ottoman",
        "3 seater": "3-seater sofa", "3-seater": "3-seater sofa",
        "2 seater": "2-seater sofa", "2-seater": "2-seater sofa",
        "1 seater": "single sofa", "single seater": "single sofa",
    },
    # Bed sub-types
    "bed": {
        "bunk bed": "bunk bed", "bunk": "bunk bed",
        "queen": "queen bed", "king": "king bed", "single": "single bed",
        "double": "double bed", "mattress": "mattress",
        "sofa cum bed": "sofa cum bed", "folding bed": "folding bed",
    },
    # Table sub-types
    "table": {
        "coffee table": "coffee table", "center table": "center table",
        "centre table": "center table", "dining table": "dining table",
        "study table": "study table", "study desk": "study desk",
        "computer table": "computer table", "laptop table": "laptop table",
        "side table": "side table", "end table": "side table",
        "bedside table": "bedside table", "nightstand": "bedside table",
        "console": "console table", "dressing table": "dressing table",
        "tv table": "tv unit", "writing desk": "writing desk",
    },
    # Lighting sub-types
    "lighting": {
        "ceiling": "ceiling light", "pendant": "pendant light",
        "chandelier": "chandelier", "floor lamp": "floor lamp",
        "table lamp": "table lamp", "desk lamp": "desk lamp",
        "wall lamp": "wall light", "wall light": "wall light", "sconce": "wall light",
        "led strip": "led strip", "led panel": "led panel",
        "down light": "downlight", "downlight": "downlight",
        "night lamp": "night lamp", "night light": "night lamp",
        "fairy": "fairy lights", "string light": "fairy lights",
    },
    # Storage sub-types
    "storage": {
        "bookshelf": "bookshelf", "book shelf": "bookshelf", "book rack": "bookshelf",
        "wardrobe": "wardrobe", "almirah": "wardrobe", "closet": "wardrobe",
        "tv unit": "tv unit", "tv stand": "tv unit", "tv cabinet": "tv unit",
        "shoe rack": "shoe rack", "shoe stand": "shoe rack",
        "cabinet": "cabinet", "cupboard": "cabinet",
        "drawer": "chest of drawers", "chest": "chest of drawers",
        "shelf": "shelf", "shelves": "shelf", "wall shelf": "wall shelf",
        "organizer": "organizer", "rack": "rack",
    },
    # Decor sub-types
    "decor": {
        "mirror": "mirror", "wall mirror": "wall mirror",
        "clock": "clock", "wall clock": "wall clock",
        "vase": "vase", "flower vase": "flower vase",
        "frame": "photo frame", "photo frame": "photo frame",
        "painting": "wall art", "wall art": "wall art", "canvas": "wall art",
        "plant": "artificial plant", "artificial": "artificial plant",
        "showpiece": "showpiece", "figurine": "figurine", "statue": "statue",
        "candle": "candle holder", "lantern": "lantern",
    },
    # Chair sub-types
    "chair": {
        "office chair": "office chair", "ergonomic": "office chair",
        "dining chair": "dining chair", "bar stool": "bar stool",
        "stool": "stool", "bench": "bench", "rocking": "rocking chair",
        "gaming": "gaming chair", "bean bag": "bean bag",
        "arm chair": "armchair", "armchair": "armchair", "accent chair": "accent chair",
    },
    # Textile sub-types
    "textile": {
        "curtain": "curtain", "rug": "rug", "carpet": "carpet",
        "throw": "throw", "blanket": "blanket", "bedspread": "bedspread",
        "towel": "towel", "bath mat": "bath mat", "door mat": "doormat",
        "cushion": "cushion cover", "pillow": "pillow cover",
        "table cloth": "table cloth", "runner": "table runner",
    },
}


def _extract_sub_type(name: str, product_type: str) -> str | None:
    """Extract specific sub-type from product name."""
    name_lower = name.lower()
    pt = str(product_type).lower()
    sub_types = _SUB_TYPE_MAP.get(pt, {})

    # Sort by key length (longest first) for best match
    for keyword in sorted(sub_types.keys(), key=len, reverse=True):
        if keyword in name_lower:
            return sub_types[keyword]
    return None


# ═══════════════════════════════════════════════════
# SEATING EXTRACTION
# ═══════════════════════════════════════════════════
def _extract_seating(name: str) -> str | None:
    """Extract seating capacity from product name."""
    name_lower = name.lower()

    # Match patterns like "3 seater", "3-seater", "3-seat", "7-seat"
    m = re.search(r'(\d+)\s*[-]?\s*seat(?:er|s)?', name_lower)
    if m:
        return f"{m.group(1)}-seater"

    # Match "single", "double", "triple"
    word_map = {"single": "1-seater", "double": "2-seater", "triple": "3-seater"}
    for word, val in word_map.items():
        if word in name_lower and "seat" in name_lower:
            return val

    return None


# ═══════════════════════════════════════════════════
# USE CASE / FEATURE TAGS
# ═══════════════════════════════════════════════════
_FEATURE_KEYWORDS = {
    "foldable": ["foldable", "folding", "fold"],
    "adjustable": ["adjustable", "height adjustable", "tilt"],
    "portable": ["portable", "lightweight", "carry"],
    "with_storage": ["with storage", "storage", "drawer", "shelf"],
    "wall_mounted": ["wall mounted", "wall mount", "wall hanging", "wall-mounted"],
    "waterproof": ["waterproof", "water resistant", "water-resistant"],
    "washable": ["washable", "machine wash"],
    "led": ["led", "energy saving"],
    "smart": ["smart", "wifi", "bluetooth", "remote control", "alexa", "google"],
    "dimmable": ["dimmable", "dimmer", "dimming"],
    "eco_friendly": ["eco friendly", "sustainable", "recycled", "organic", "natural"],
    "diy": ["diy", "do-it-yourself", "assembly required"],
}


def _extract_features(name: str) -> list[str]:
    """Extract feature tags from product name."""
    name_lower = name.lower()
    features = []
    for feature, keywords in _FEATURE_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                features.append(feature)
                break
    return features


# ═══════════════════════════════════════════════════
# PRICE TIER
# ═══════════════════════════════════════════════════
def _assign_price_tier(price: float, product_type: str) -> str:
    """Assign price tier based on price and product type."""
    # Different thresholds for different product types
    thresholds = {
        "sofa":     (10000, 30000, 70000),
        "bed":      (8000, 20000, 50000),
        "table":    (3000, 10000, 30000),
        "storage":  (3000, 10000, 30000),
        "chair":    (3000, 10000, 25000),
        "lighting": (1000, 5000, 15000),
        "decor":    (500, 2000, 8000),
        "textile":  (500, 2000, 8000),
    }

    pt = str(product_type).lower()
    budget_max, mid_max, premium_max = thresholds.get(pt, (3000, 10000, 30000))

    if pd.isna(price):
        return "unknown"
    elif price <= budget_max:
        return "budget"
    elif price <= mid_max:
        return "mid-range"
    elif price <= premium_max:
        return "premium"
    else:
        return "luxury"


# ═══════════════════════════════════════════════════
# SIZE CATEGORY
# ═══════════════════════════════════════════════════
def _extract_size_from_name(name: str) -> str | None:
    """Extract size indicator from name."""
    name_lower = name.lower()
    if any(w in name_lower for w in ["large", "big", "xl", "king", "7 seat", "6 seat"]):
        return "large"
    elif any(w in name_lower for w in ["medium", "queen", "4 seat", "3 seat"]):
        return "medium"
    elif any(w in name_lower for w in ["small", "compact", "mini", "single", "1 seat", "2 seat"]):
        return "small"
    return None


# ═══════════════════════════════════════════════════
# MAIN ENRICHMENT FUNCTION
# ═══════════════════════════════════════════════════
def enrich_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich a product DataFrame with extracted attributes.

    Adds columns: color, material, room_type, style, sub_type,
                  seating, price_tier, size_category, features

    Args:
        df: DataFrame with at least 'product_name', 'product_type', 'price_value'

    Returns:
        Enriched DataFrame with new columns.
    """
    result = df.copy()
    names = result["product_name"].fillna("")
    types = result["product_type"].fillna("")
    prices = result["price_value"]

    # Extract all attributes — only fill where currently missing (NaN/None)
    def _fill_if_missing(col_name, extractor):
        """Apply extractor only where column is missing or NaN."""
        extracted = extractor()
        if col_name in result.columns:
            # Keep existing non-null values, fill NaN with extracted
            result[col_name] = result[col_name].fillna(pd.Series(extracted, index=result.index))
        else:
            result[col_name] = extracted

    _fill_if_missing("color", lambda: names.apply(_extract_color))
    _fill_if_missing("material", lambda: names.apply(_extract_material))
    _fill_if_missing("room_type", lambda: [_infer_room_type(n, t) for n, t in zip(names, types)])
    _fill_if_missing("style", lambda: names.apply(_infer_style))

    # These are always new columns — safe to overwrite
    result["sub_type"] = [_extract_sub_type(n, t) for n, t in zip(names, types)]
    result["seating"] = names.apply(_extract_seating)
    result["price_tier"] = [_assign_price_tier(p, t) for p, t in zip(prices, types)]
    result["size_category"] = names.apply(_extract_size_from_name)
    result["features"] = names.apply(lambda n: ",".join(_extract_features(n)) if _extract_features(n) else None)

    # ── CRITICAL: Fix misclassified product_type based on product names ──
    result = _fix_product_type_classification(result)

    return result


def _fix_product_type_classification(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix products whose product_type doesn't match their actual name.

    E.g.:
        - "day-bed" labeled as "sofa" → should be "bed"
        - "table and 4 chairs" labeled as "chair" → should be "table"
        - "gaming desk and chair" labeled as "chair" → should be "table"
    """
    result = df.copy()
    names = result["product_name"].fillna("").str.lower()
    fixes = 0

    # 1. Day-beds misclassified as sofa → bed
    is_daybed = names.str.contains(r"day[\s-]?bed", regex=True, na=False)
    wrong_sofa = is_daybed & (result["product_type"] == "sofa")
    result.loc[wrong_sofa, "product_type"] = "bed"
    result.loc[wrong_sofa, "sub_type"] = "day bed"
    fixes += wrong_sofa.sum()

    # 2. "sofa bed" / "sofa cum bed" labeled as bed → sofa
    is_sofabed = names.str.contains(r"sofa[\s-]?(bed|cum\s*bed)", regex=True, na=False)
    wrong_bed = is_sofabed & (result["product_type"] == "bed")
    result.loc[wrong_bed, "product_type"] = "sofa"
    result.loc[wrong_bed, "sub_type"] = "sofa cum bed"
    fixes += wrong_bed.sum()

    # 3. "table and N chairs/stools" labeled as chair → table
    is_table_set = names.str.contains(r"table\s+and\s+\d+\s+(chair|stool|seat)", regex=True, na=False)
    wrong_chair = is_table_set & (result["product_type"] == "chair")
    result.loc[wrong_chair, "product_type"] = "table"
    result.loc[wrong_chair, "sub_type"] = "dining set"
    fixes += wrong_chair.sum()

    # 4. "desk and chair" labeled as chair → table
    is_desk_set = names.str.contains(r"desk\s+and\s+(chair|stool)", regex=True, na=False)
    wrong_desk = is_desk_set & (result["product_type"] == "chair")
    result.loc[wrong_desk, "product_type"] = "table"
    result.loc[wrong_desk, "sub_type"] = "desk set"
    fixes += wrong_desk.sum()

    # 5. "picnic table" labeled as chair → table
    is_picnic = names.str.contains(r"picnic\s+table", regex=True, na=False)
    wrong_picnic = is_picnic & (result["product_type"] == "chair")
    result.loc[wrong_picnic, "product_type"] = "table"
    fixes += wrong_picnic.sum()

    # 6. Products with "mattress" in name but not "bed" type → bed
    is_mattress = names.str.contains(r"\bmattress\b", regex=True, na=False)
    wrong_mattress = is_mattress & ~(result["product_type"].isin(["bed", "sofa"]))
    result.loc[wrong_mattress, "product_type"] = "bed"
    result.loc[wrong_mattress, "sub_type"] = "mattress"
    fixes += wrong_mattress.sum()

    if fixes > 0:
        print(f"[A2S] Reclassified {fixes} mistyped products")

    return result


def print_enrichment_report(df: pd.DataFrame) -> None:
    """Print a summary of enrichment coverage."""
    total = len(df)
    print(f"\n{'='*60}")
    print(f"  ENRICHMENT REPORT — {total} products")
    print(f"{'='*60}")

    attrs = ["color", "material", "room_type", "style", "sub_type",
             "seating", "price_tier", "size_category", "features"]

    for attr in attrs:
        if attr in df.columns:
            non_null = df[attr].notna().sum()
            pct = non_null / total * 100
            bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
            print(f"  {attr:>15}: {non_null:>5}/{total}  ({pct:5.1f}%)  {bar}")

    # Top values for each attribute
    for attr in ["color", "material", "room_type", "style", "sub_type", "price_tier"]:
        if attr in df.columns:
            top = df[attr].dropna().value_counts().head(8)
            if not top.empty:
                vals = ", ".join(f"{v}({c})" for v, c in top.items())
                print(f"\n  Top {attr}: {vals}")

    print(f"\n{'='*60}")
