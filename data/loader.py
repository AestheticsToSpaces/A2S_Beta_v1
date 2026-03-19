"""
Data Loader & Merger Module.

Loads both original Excel data sources AND the scraped product data,
merges them, cleans the data, parses dimensions, and produces a
single clean Pandas DataFrame that serves as the product catalog.

Pipeline:
    Excel File 1 + Excel File 2 + Scraped Data
        → Merge & Deduplicate
        → Clean (nulls, brands, column names)
        → Enrich (parse WxDxH, extract brand from name)
        → Product Catalog DataFrame
"""

import re
import pandas as pd
import streamlit as st

from config import DATA_FILES, CANONICAL_COLUMNS, SCRAPED_DATA_FILE
from data.enrichment import enrich_dataset


# ──────────────────────────────────────────────
# Dimension parser
# ──────────────────────────────────────────────
def _parse_dimensions(dim_str: str) -> dict:
    """
    Parse dimension strings into width, depth, height (cm).

    Supported formats:
        "322x98x48"         → W=322, D=98, H=48
        "160 x 200 cm"      → W=160, D=200, H=None
        "33x38x33 cm"       → W=33, D=38, H=33
        "60x27x74 cm"       → W=60, D=27, H=74

    Returns:
        dict with keys: width_cm, depth_cm, height_cm (None if missing)
    """
    result = {"width_cm": None, "depth_cm": None, "height_cm": None}

    if not dim_str or pd.isna(dim_str):
        return result

    dim_str = str(dim_str).strip().lower().replace("cm", "").strip()

    # Match numbers separated by 'x' or ' x '
    numbers = re.findall(r"(\d+(?:\.\d+)?)", dim_str)

    if len(numbers) >= 3:
        result["width_cm"] = float(numbers[0])
        result["depth_cm"] = float(numbers[1])
        result["height_cm"] = float(numbers[2])
    elif len(numbers) == 2:
        result["width_cm"] = float(numbers[0])
        result["depth_cm"] = float(numbers[1])
    elif len(numbers) == 1:
        result["width_cm"] = float(numbers[0])

    return result


# ──────────────────────────────────────────────
# Brand cleaner
# ──────────────────────────────────────────────
_JUNK_BRAND_PATTERNS = [
    r"Browse\s+Type",
    r"Discount\s+Set",
    r"Microwave\s+safe",
    r"Primary\s+Material",
    r"Shade\s+material",
    r"Frame\s+Material",
    r"Power\s+source",
]

# Words that are NOT brands (colors, shapes, generic terms)
_NOT_BRANDS = {
    "unknown", "black", "white", "gold", "silver", "brown", "grey", "gray",
    "red", "blue", "green", "yellow", "beige", "pink", "orange", "purple",
    "multicolor", "round", "oval", "rectangle", "square", "designer",
    "modern", "classic", "vintage", "premium", "luxury", "set",
    "pack", "combo", "pair", "single", "double", "large", "small", "medium",
}

# Known real brands from Amazon/Flipkart
_KNOWN_BRANDS = {
    "amazon basics", "amazonbasics", "solimo", "nilkamal", "wakefit",
    "furny", "duroflex", "godrej", "zuari", "royaloak", "hometown",
    "urban ladder", "urbanladder", "pepperfry", "fabindia",
    "crosscut", "exclusivelane", "craft art india",
    "satyam kraft", "sehaz artworks", "art street",
    "divine trends", "wallmantra", "walldesign",
    "ganpati arts", "the attic", "home elements",
    "sleepyhead", "springtek", "centuary", "kurl-on",
    "wipro", "syska", "philips", "havells", "crompton",
    "asian paints", "berger", "nerolac",
}


def _clean_brand(brand: str, product_name: str = "") -> str:
    """
    Return cleaned brand name. Falls back to extracting brand
    from product_name if the brand field is junk.
    """
    if not brand or pd.isna(brand):
        brand = "Unknown"
    else:
        brand = str(brand).strip()

    # Check for junk HTML patterns
    for pattern in _JUNK_BRAND_PATTERNS:
        if re.search(pattern, brand, re.IGNORECASE):
            brand = "Unknown"
            break

    # Check for false brands (colors, shapes, etc.)
    if brand.lower() in _NOT_BRANDS:
        brand = "Unknown"

    # If still Unknown, try to extract from product_name
    if brand == "Unknown" and product_name:
        name = str(product_name).strip()

        # Check if a known brand appears in the name
        name_lower = name.lower()
        for kb in _KNOWN_BRANDS:
            if kb in name_lower:
                # Capitalize properly
                brand = kb.title()
                break

        # If still unknown, try the first word/phrase before common separators
        if brand == "Unknown":
            # Common patterns: "BrandName ProductType..." or "Brand Name - Product"
            first_part = re.split(r"\s+(?:for|with|in|and|set|\d|[-|])", name, maxsplit=1)[0]
            # Take first 1-2 words that look like a brand
            words = first_part.split()
            if words and len(words[0]) > 2:
                candidate = words[0]
                if len(words) > 1 and len(words[1]) > 2 and words[1][0].isupper():
                    candidate = words[0] + " " + words[1]
                if candidate.lower() not in _NOT_BRANDS and len(candidate) < 30:
                    brand = candidate

    return brand


# ──────────────────────────────────────────────
# Load scraped data
# ──────────────────────────────────────────────
def _load_scraped_data() -> pd.DataFrame:
    """Load the most recent scraped product file if it exists."""
    if not SCRAPED_DATA_FILE:
        return pd.DataFrame()

    try:
        df = pd.read_excel(SCRAPED_DATA_FILE, engine="openpyxl")

        # Ensure required columns exist
        if "product_id" not in df.columns or "product_name" not in df.columns:
            return pd.DataFrame()

        # Apply better brand extraction
        df["brand"] = df.apply(
            lambda row: _clean_brand(str(row.get("brand", "")), str(row.get("product_name", ""))),
            axis=1,
        )

        # Filter out junk prices (< ₹100 is likely bad data)
        if "price_value" in df.columns:
            df = df[df["price_value"] >= 100]

        return df

    except Exception as e:
        st.warning(f"Could not load scraped data: {e}")
        return pd.DataFrame()


# ──────────────────────────────────────────────
# Main loader
# ──────────────────────────────────────────────
# Version bump this when enrichment logic changes to bust the cache
_CATALOG_VERSION = "v5_reclassified"


@st.cache_data(show_spinner="Loading product catalog...")
def load_product_catalog(_version: str = _CATALOG_VERSION) -> pd.DataFrame:
    """
    Load, merge, clean, and enrich all data sources into a single DataFrame.

    Sources:
        1. design_products_data (1).xlsx
        2. design_products_with_dimension.xlsx
        3. scraped_products_*.xlsx (from crawler)

    Returns:
        pd.DataFrame – The unified product catalog.
    """
    frames = []

    # ── Load original Excel files ──────────────
    for filepath in DATA_FILES:
        try:
            df = pd.read_excel(filepath, engine="openpyxl")
            # Standardize the dimension column name
            dim_col = None
            for col in df.columns:
                if "dimension" in str(col).lower():
                    dim_col = col
                    break
            if dim_col and dim_col != "dimensions":
                df = df.rename(columns={dim_col: "dimensions"})

            # Drop completely unnamed / empty columns
            df = df.loc[:, ~df.columns.str.contains(r"^Unnamed|^None", na=False)]
            df = df.dropna(how="all", axis=1)

            # Tag source
            df["source"] = "original_data"

            frames.append(df)
        except Exception as e:
            st.warning(f"Could not load {filepath}: {e}")

    # ── Load scraped data ──────────────────────
    scraped_df = _load_scraped_data()
    if not scraped_df.empty:
        frames.append(scraped_df)

    if not frames:
        return pd.DataFrame()

    # ── Merge ────────────────────────────────
    catalog = pd.concat(frames, ignore_index=True)

    # ── Drop fully-empty rows ────────────────
    catalog = catalog.dropna(subset=["product_id"])

    # ── Filter junk prices (like ₹5 entries) ─
    if "price_value" in catalog.columns:
        catalog = catalog[
            (catalog["price_value"].isna()) | (catalog["price_value"] >= 100)
        ]

    # ── AGGRESSIVE DATA CLEANING ──────────────

    # 1. Remove garbage product names (scraping artifacts)
    _GARBAGE_NAME_PATTERNS = [
        r"buy\s+.+\s+at\s+best\s+price",  # "buy sofa at best price - ikea"
        r"buy\s+.+\s+online\s+in\s+india",  # "buy beds online in india"
        r"^[\*\.\-\s]+$",                    # just "*", ".", "-"
        r"^\d+\s*(inch|cm|mm)",              # "10 inch, white"
        r"^\d+\s*cm,",                       # "15 cm, green"
        r"^(black|white|grey|brown|red|blue|green|yellow|pink|beige)$",  # just a color word
    ]
    if "product_name" in catalog.columns:
        name_col = catalog["product_name"].fillna("").str.strip().str.lower()
        garbage_mask = pd.Series(False, index=catalog.index)
        for pattern in _GARBAGE_NAME_PATTERNS:
            garbage_mask |= name_col.str.contains(pattern, regex=True, na=False)
        # Also filter names shorter than 5 chars (garbage like "*")
        garbage_mask |= (name_col.str.len() < 5)
        removed_count = garbage_mask.sum()
        catalog = catalog[~garbage_mask]
        if removed_count > 0:
            print(f"[A2S] Removed {removed_count} garbage product name rows")

    # 2. Minimum price floors by product type (a sofa can't cost ₹134)
    _MIN_PRICE_BY_TYPE = {
        "sofa": 3000, "bed": 3000, "table": 500, "storage": 300,
        "chair": 500, "lighting": 200, "decor": 100, "textile": 100,
    }
    if "product_type" in catalog.columns and "price_value" in catalog.columns:
        price_mask = pd.Series(True, index=catalog.index)
        for ptype, min_price in _MIN_PRICE_BY_TYPE.items():
            is_type = catalog["product_type"] == ptype
            too_cheap = catalog["price_value"] < min_price
            price_mask &= ~(is_type & too_cheap)
        removed_price = (~price_mask).sum()
        catalog = catalog[price_mask]
        if removed_price > 0:
            print(f"[A2S] Removed {removed_price} products with impossibly low prices")

    # 3. Deduplicate by product_name (keep the one with best data quality)
    if "product_name" in catalog.columns:
        before = len(catalog)
        catalog = catalog.drop_duplicates(subset=["product_name"], keep="first")
        dedup_count = before - len(catalog)
        if dedup_count > 0:
            print(f"[A2S] Removed {dedup_count} duplicate product names")

    # ── Clean brands ─────────────────────────
    catalog["brand"] = catalog.apply(
        lambda row: _clean_brand(
            str(row.get("brand", "")),
            str(row.get("product_name", "")),
        ),
        axis=1,
    )

    # ── Parse dimensions ─────────────────────
    if "dimensions" in catalog.columns:
        dim_parsed = catalog["dimensions"].apply(_parse_dimensions).apply(pd.Series)
        catalog["width_cm"] = dim_parsed["width_cm"]
        catalog["depth_cm"] = dim_parsed["depth_cm"]
        catalog["height_cm"] = dim_parsed["height_cm"]

    # ── Normalize text columns ───────────────
    text_cols = ["room_type", "style", "color_palette", "product_type",
                 "product_name", "decor_type", "role_in_design"]
    for col in text_cols:
        if col in catalog.columns:
            catalog[col] = catalog[col].astype(str).str.strip().str.lower()
            catalog[col] = catalog[col].replace("nan", None)

    # ── Ensure numeric columns ───────────────
    numeric_cols = ["price_value", "budget_min", "budget_max",
                    "width_cm", "depth_cm", "height_cm"]
    for col in numeric_cols:
        if col in catalog.columns:
            catalog[col] = pd.to_numeric(catalog[col], errors="coerce")

    # ── Deduplicate by product_id (keep first) ──
    catalog = catalog.drop_duplicates(subset=["product_id"], keep="first")

    # ── ENRICH: extract color, material, room_type, style, etc. from names ──
    catalog = enrich_dataset(catalog)
    print(f"[A2S] Enriched catalog: {len(catalog)} products, "
          f"color={catalog['color'].notna().sum()}, "
          f"material={catalog['material'].notna().sum()}, "
          f"sub_type={catalog['sub_type'].notna().sum()}")

    # ── Select canonical columns that exist ──
    available = [c for c in CANONICAL_COLUMNS if c in catalog.columns]
    catalog = catalog[available].reset_index(drop=True)

    return catalog


def get_catalog_summary(catalog: pd.DataFrame) -> dict:
    """
    Return a summary dict for displaying catalog stats.
    """
    summary = {
        "total_products": len(catalog),
        "brands": sorted(catalog["brand"].dropna().unique().tolist()),
        "price_range": {
            "min": float(catalog["price_value"].min()) if not catalog["price_value"].isna().all() else 0,
            "max": float(catalog["price_value"].max()) if not catalog["price_value"].isna().all() else 0,
        },
    }

    # Optional fields
    for col_key in ["room_type", "style", "product_type", "color_palette"]:
        if col_key in catalog.columns:
            vals = catalog[col_key].dropna().unique().tolist()
            summary[f"{col_key}s" if not col_key.endswith("e") else f"{col_key}s"] = sorted(vals)
        else:
            summary[f"{col_key}s"] = []

    # Source breakdown
    if "source" in catalog.columns:
        summary["by_source"] = catalog["source"].value_counts().to_dict()
    else:
        summary["by_source"] = {"original_data": len(catalog)}

    return summary
