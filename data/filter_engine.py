"""
Smart Filter Engine.

Applies multi-criteria filtering to the product catalog based on
user requirements extracted by the AI agent.  Supports fuzzy/partial
matching for text fields and range queries for numeric fields.

Supported filter keys:
    room_type       – exact or fuzzy match
    style           – exact or fuzzy match
    color_palette   – exact or fuzzy match
    color           – searches product_name, color column, color_palette
    product_type    – exact or fuzzy match
    brand           – exact or fuzzy match (case-insensitive)
    budget_min      – numeric: products with price >= value
    budget_max      – numeric: products with price <= value
    min_width       – numeric: width_cm >= value
    max_width       – numeric: width_cm <= value
    min_depth       – numeric: depth_cm >= value
    max_depth       – numeric: depth_cm <= value
    min_height      – numeric: height_cm >= value
    max_height      – numeric: height_cm <= value
    decor_type      – exact or fuzzy match
    role_in_design  – exact or fuzzy match
    keyword         – free-text search across product_name + brand
    material        – searches product_name + material column
"""

from __future__ import annotations
from typing import Any

import pandas as pd


def _fuzzy_match(series: pd.Series, value: str) -> pd.Series:
    """Case-insensitive substring match on a text Series."""
    value = str(value).strip().lower()
    return series.fillna("").str.lower().str.contains(value, regex=False)


def _multi_col_search(catalog: pd.DataFrame, value: str, columns: list[str],
                      word_boundary: bool = False) -> pd.Series:
    """
    Search for a value across multiple columns (OR logic).
    Returns True for rows where ANY of the columns contain the value.

    Args:
        word_boundary: If True, use regex word-boundary matching (\\bvalue\\b)
                       to avoid false positives like "gunnared" matching "red".
    """
    value = str(value).strip().lower()
    mask = pd.Series(False, index=catalog.index)
    for col in columns:
        if col in catalog.columns:
            col_lower = catalog[col].fillna("").str.lower()
            if word_boundary:
                import re
                pattern = r'(?:^|[\s,/\-_()])' + re.escape(value) + r'(?:$|[\s,/\-_()])'
                mask = mask | col_lower.str.contains(pattern, regex=True, na=False)
            else:
                mask = mask | col_lower.str.contains(value, regex=False)
    return mask


def filter_products(
    catalog: pd.DataFrame,
    filters: dict[str, Any],
) -> pd.DataFrame:
    """
    Apply a dictionary of filters to the catalog and return matching rows.

    Args:
        catalog:  The full product catalog DataFrame.
        filters:  Dict of filter_key → value(s).  Supports:
                  - str values for text columns (fuzzy matched)
                  - int/float for numeric columns
                  - list[str] for multi-value text matching (OR)

    Returns:
        Filtered DataFrame (may be empty).
    """
    if not filters:
        return catalog.copy()

    mask = pd.Series(True, index=catalog.index)

    # ── Text filters (fuzzy / substring) ──────
    text_filters = {
        "room_type": "room_type",
        "style": "style",
        "color_palette": "color_palette",
        "product_type": "product_type",
        "brand": "brand",
        "decor_type": "decor_type",
        "role_in_design": "role_in_design",
        "sub_type": "sub_type",
        "seating": "seating",
        "price_tier": "price_tier",
        "size_category": "size_category",
    }

    for filter_key, col_name in text_filters.items():
        if filter_key in filters and filters[filter_key] and col_name in catalog.columns:
            value = filters[filter_key]
            if isinstance(value, list):
                # OR match: any of the listed values
                sub_mask = pd.Series(False, index=catalog.index)
                for v in value:
                    sub_mask = sub_mask | _fuzzy_match(catalog[col_name], v)
                mask = mask & sub_mask
            else:
                mask = mask & _fuzzy_match(catalog[col_name], value)

    # ── Features filter (search in comma-separated features column) ──
    if "features" in filters and filters["features"] and "features" in catalog.columns:
        feat_val = str(filters["features"]).strip().lower()
        mask = mask & catalog["features"].fillna("").str.lower().str.contains(feat_val, regex=False)

    # ── Color filter (word-boundary match to avoid "gunnared" matching "red") ──
    if "color" in filters and filters["color"]:
        color_val = str(filters["color"]).strip().lower()
        color_mask = _multi_col_search(
            catalog, color_val,
            ["product_name", "color", "color_palette"],
            word_boundary=True,
        )
        mask = mask & color_mask

    # ── Material filter (word-boundary match) ──
    if "material" in filters and filters["material"]:
        mat_val = str(filters["material"]).strip().lower()
        mat_mask = _multi_col_search(
            catalog, mat_val,
            ["product_name", "material"],
            word_boundary=True,
        )
        mask = mask & mat_mask

    # ── Budget / Price filters ────────────────
    if "budget_min" in filters and filters["budget_min"] is not None:
        val = float(filters["budget_min"])
        if "price_value" in catalog.columns:
            mask = mask & (catalog["price_value"] >= val)

    if "budget_max" in filters and filters["budget_max"] is not None:
        val = float(filters["budget_max"])
        if "price_value" in catalog.columns:
            mask = mask & (catalog["price_value"] <= val)

    # ── Dimension filters ─────────────────────
    dimension_filters = {
        "min_width": ("width_cm", ">="),
        "max_width": ("width_cm", "<="),
        "min_depth": ("depth_cm", ">="),
        "max_depth": ("depth_cm", "<="),
        "min_height": ("height_cm", ">="),
        "max_height": ("height_cm", "<="),
    }

    for filter_key, (col_name, op) in dimension_filters.items():
        if filter_key in filters and filters[filter_key] is not None:
            val = float(filters[filter_key])
            if col_name in catalog.columns:
                col = catalog[col_name]
                if op == ">=":
                    mask = mask & (col >= val)
                elif op == "<=":
                    mask = mask & (col <= val)

    # ── Keyword / free-text search (word-boundary for short terms, substring for longer) ──
    if "keyword" in filters and filters["keyword"]:
        keyword = str(filters["keyword"]).strip().lower()
        # Short keywords (<=5 chars like "red", "blue", "wood") need word-boundary
        # to avoid false positives; longer keywords are safe with substring match
        use_wb = len(keyword) <= 5
        kw_mask = _multi_col_search(
            catalog, keyword,
            ["product_name", "brand", "color", "material"],
            word_boundary=use_wb,
        )
        mask = mask & kw_mask

    return catalog[mask].copy()
