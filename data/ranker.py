"""
Product Ranking Engine.

After filtering, this module scores and ranks the remaining products
to surface the most relevant results to the user.

Supports sort_preference: "price_high" (costliest first) or "price_low" (cheapest first).

RANKING PHILOSOPHY:
    The user's EXPLICIT words matter most.  If they said "red sofa",
    a product whose name contains "red" is FAR more relevant than one
    that merely belongs to a "red and beige" palette but is actually grey.
"""

from __future__ import annotations
from typing import Any

import pandas as pd
import numpy as np

from config import MAX_RESULTS_PER_QUERY


def rank_products(
    products: pd.DataFrame,
    filters: dict[str, Any],
    top_n: int = MAX_RESULTS_PER_QUERY,
    sort_preference: str | None = None,
) -> pd.DataFrame:
    """
    Score and rank filtered products by relevance.

    Args:
        products:  Pre-filtered DataFrame of products.
        filters:   The same filter dict used for filtering (provides context).
        top_n:     Number of top results to return.
        sort_preference: "price_high" (most expensive first),
                         "price_low" (cheapest first), or None (relevance).

    Returns:
        Top-N products sorted by relevance score (descending).
    """
    if products.empty:
        return products

    df = products.copy()

    # ── SHORTCUT: If user explicitly wants costliest or cheapest ──
    if sort_preference == "price_high" and "price_value" in df.columns:
        df = df.dropna(subset=["price_value"])
        df = df.sort_values("price_value", ascending=False).head(top_n)
        return df.reset_index(drop=True)

    if sort_preference == "price_low" and "price_value" in df.columns:
        df = df.dropna(subset=["price_value"])
        df = df.sort_values("price_value", ascending=True).head(top_n)
        return df.reset_index(drop=True)

    # ── RELEVANCE SCORING ──
    df["_score"] = 0.0
    name_lower = df["product_name"].fillna("").str.lower() if "product_name" in df.columns else pd.Series("", index=df.index)

    # ── 1. Keyword / color / material in product_name  (40% — HIGHEST WEIGHT) ──
    #    This is the most important signal: if user said "red" and the product
    #    name contains "red", that's a STRONG indicator of relevance.
    keyword = filters.get("keyword")
    color = filters.get("color")
    material = filters.get("material")

    # Collect all user-specified search terms
    search_terms = set()
    if keyword:
        search_terms.add(str(keyword).lower())
    if color:
        search_terms.add(str(color).lower())
    if material:
        search_terms.add(str(material).lower())

    if search_terms:
        import re
        term_score = pd.Series(0.0, index=df.index)
        for term in search_terms:
            # Word-boundary match for short terms to avoid "gunnared" matching "red"
            if len(term) <= 5:
                pattern = r'(?:^|[\s,/\-_()])' + re.escape(term) + r'(?:$|[\s,/\-_()])'
                term_score += name_lower.str.contains(pattern, regex=True, na=False).astype(float)
            else:
                term_score += name_lower.str.contains(term, regex=False).astype(float)
        # Normalize: each term match = 0.40 / len(search_terms)
        df["_score"] += (term_score / len(search_terms)) * 0.40

    # ── 2. Exact product_type match (20%) ──
    if filters.get("product_type") and "product_type" in df.columns:
        target = str(filters["product_type"]).lower()
        exact = df["product_type"].fillna("").str.lower() == target
        df["_score"] += exact.astype(float) * 0.20

    # ── 3. Price closeness to budget midpoint (15%) ──
    budget_min = filters.get("budget_min")
    budget_max = filters.get("budget_max")

    if budget_min is not None or budget_max is not None:
        b_min = float(budget_min or 0)
        b_max = float(budget_max or df["price_value"].max())
        midpoint = (b_min + b_max) / 2

        if "price_value" in df.columns:
            distance = (df["price_value"] - midpoint).abs()
            max_dist = distance.max()
            if max_dist > 0:
                price_score = 1 - (distance / max_dist)
                df["_score"] += price_score * 0.15

    # ── 4. Room type match (5%) ──
    if filters.get("room_type") and "room_type" in df.columns:
        target = str(filters["room_type"]).lower()
        df["_score"] += (df["room_type"].fillna("").str.lower() == target).astype(float) * 0.05

    # ── 5. Style match (5%) ──
    if filters.get("style") and "style" in df.columns:
        target = str(filters["style"]).lower()
        df["_score"] += (df["style"].fillna("").str.lower() == target).astype(float) * 0.05

    # ── 6. Has valid image URL (10%) ──
    #    Products with images are much more useful to display
    if "image_url" in df.columns:
        df["_score"] += df["image_url"].fillna("").str.startswith("http").astype(float) * 0.10

    # ── 7. Has dimension data (5%) ──
    if "width_cm" in df.columns:
        df["_score"] += df["width_cm"].notna().astype(float) * 0.05

    # ── De-duplicate by product_name (keep highest score) ──
    if "product_name" in df.columns:
        df = df.sort_values("_score", ascending=False).drop_duplicates(
            subset=["product_name"], keep="first"
        )

    # ── Sort and return top N ──
    df = df.sort_values("_score", ascending=False).head(top_n)
    df = df.drop(columns=["_score"])

    return df.reset_index(drop=True)
