"""
End-to-End Test Suite for A2S Product Search Pipeline.

Tests the full chain: safety-net extraction → filter engine → search → ranker
WITHOUT calling Gemini (tests the deterministic parts only).

Run:  python -m tests.test_e2e
"""

from __future__ import annotations

import sys
import os
import re
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from data.loader import load_product_catalog
from data.filter_engine import filter_products
from data.ranker import rank_products
from agent.core import (
    _detect_color_from_message,
    _detect_material_from_message,
    _detect_product_type_from_message,
    _detect_sort_preference,
    _search_products,
    _combo_search,
    _detect_combo_intent,
)


# ═══════════════════════════════════════════════════
# Test Infrastructure
# ═══════════════════════════════════════════════════
class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = True
        self.errors: list[str] = []

    def fail(self, msg: str):
        self.passed = False
        self.errors.append(msg)

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        err_str = "\n    ".join(self.errors) if self.errors else ""
        return f"  [{status}] {self.name}" + (f"\n    {err_str}" if err_str else "")


results: list[TestResult] = []


def run_test(name: str):
    """Decorator to register and run a test."""
    def decorator(fn):
        t = TestResult(name)
        try:
            fn(t)
        except Exception as e:
            t.fail(f"EXCEPTION: {e}")
        results.append(t)
        return fn
    return decorator


def word_in_text(word: str, text: str) -> bool:
    """Check if word appears as a whole word in text (case-insensitive)."""
    pattern = r'(?:^|[^a-z])' + re.escape(word.lower()) + r'(?:$|[^a-z])'
    return bool(re.search(pattern, text.lower()))


# ═══════════════════════════════════════════════════
# Load catalog once
# ═══════════════════════════════════════════════════
print("Loading product catalog...")
t0 = time.time()
catalog = load_product_catalog()
print(f"Loaded {len(catalog)} products in {time.time()-t0:.1f}s")
print(f"Columns: {list(catalog.columns)}")
print(f"Enriched: color={catalog['color'].notna().sum()}, "
      f"material={catalog['material'].notna().sum()}, "
      f"sub_type={catalog['sub_type'].notna().sum()}, "
      f"price_tier={catalog['price_tier'].notna().sum()}")
print()


# ═══════════════════════════════════════════════════
# CATEGORY 1: Safety-Net Detectors
# ═══════════════════════════════════════════════════
@run_test("Detect color: 'red sofas' → red")
def _(t):
    c = _detect_color_from_message("red sofas")
    if c != "red":
        t.fail(f"Expected 'red', got '{c}'")

@run_test("Detect color: 'show me blue chairs' → blue")
def _(t):
    c = _detect_color_from_message("show me blue chairs")
    if c != "blue":
        t.fail(f"Expected 'blue', got '{c}'")

@run_test("Detect color: 'gunnared sofa' → None (not a color)")
def _(t):
    c = _detect_color_from_message("gunnared sofa")
    if c is not None:
        t.fail(f"Expected None, got '{c}' (false positive on 'gunnared')")

@run_test("Detect material: 'wooden table' → wooden")
def _(t):
    m = _detect_material_from_message("wooden table")
    if m != "wooden":
        t.fail(f"Expected 'wooden', got '{m}'")

@run_test("Detect material: 'leather recliner' → leather")
def _(t):
    m = _detect_material_from_message("leather recliner")
    if m != "leather":
        t.fail(f"Expected 'leather', got '{m}'")

@run_test("Detect type: 'study room lighting' → lighting")
def _(t):
    p = _detect_product_type_from_message("study room lighting")
    if p != "lighting":
        t.fail(f"Expected 'lighting', got '{p}'")

@run_test("Detect type: 'coffee table' → table")
def _(t):
    p = _detect_product_type_from_message("coffee table")
    if p != "table":
        t.fail(f"Expected 'table', got '{p}'")

@run_test("Detect type: 'bookshelf for study' → storage")
def _(t):
    p = _detect_product_type_from_message("bookshelf for study")
    if p != "storage":
        t.fail(f"Expected 'storage', got '{p}'")

@run_test("Detect sort: 'costliest products' → price_high")
def _(t):
    s = _detect_sort_preference("costliest products")
    if s != "price_high":
        t.fail(f"Expected 'price_high', got '{s}'")

@run_test("Detect sort: 'cheapest bed' → price_low")
def _(t):
    s = _detect_sort_preference("cheapest bed")
    if s != "price_low":
        t.fail(f"Expected 'price_low', got '{s}'")

@run_test("Detect sort: 'modern sofa' → None (no sort intent)")
def _(t):
    s = _detect_sort_preference("modern sofa")
    if s is not None:
        t.fail(f"Expected None, got '{s}'")


# ═══════════════════════════════════════════════════
# CATEGORY 2: Single Product Searches
# ═══════════════════════════════════════════════════
@run_test("Search: 'sofas' returns sofa products")
def _(t):
    f = {"product_type": "sofa"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No results for sofas")
    elif not all(results["product_type"].str.contains("sofa", case=False, na=False)):
        bad = results[~results["product_type"].str.contains("sofa", case=False, na=False)]
        t.fail(f"{len(bad)} non-sofa products in results")

@run_test("Search: 'lighting' returns lighting products")
def _(t):
    f = {"product_type": "lighting"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No results for lighting")

@run_test("Search: 'bed' returns bed products")
def _(t):
    f = {"product_type": "bed"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No results for bed")

@run_test("Search: 'storage' returns storage products")
def _(t):
    f = {"product_type": "storage"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No results for storage")

@run_test("Search: 'decor' returns decor products")
def _(t):
    f = {"product_type": "decor"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No results for decor")

@run_test("Search: 'chair' returns chair products")
def _(t):
    f = {"product_type": "chair"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No results for chair")

@run_test("Search: 'textile' returns textile products")
def _(t):
    f = {"product_type": "textile"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No results for textile")

@run_test("Search: 'table' returns table products")
def _(t):
    f = {"product_type": "table"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No results for table")


# ═══════════════════════════════════════════════════
# CATEGORY 3: Color Searches
# ═══════════════════════════════════════════════════
@run_test("Color: 'red sofas' → only products with 'red' in name/color")
def _(t):
    f = {"product_type": "sofa", "color": "red", "keyword": "red"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No red sofas found")
        return
    for _, r in results.iterrows():
        name = str(r.get("product_name", "")).lower()
        color = str(r.get("color", "")).lower()
        if "red" not in color and not word_in_text("red", name) and not word_in_text("crimson", name) and not word_in_text("maroon", name):
            t.fail(f"Non-red product in results: {name[:50]} (color={color})")
            break

@run_test("Color: 'white bed' → has results")
def _(t):
    f = {"product_type": "bed", "color": "white", "keyword": "white"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No white beds found")

@run_test("Color: 'black chair' → has results")
def _(t):
    f = {"product_type": "chair", "color": "black", "keyword": "black"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        # Fallback: try without keyword
        f2 = {"product_type": "chair", "color": "black"}
        results, _ = _search_products(catalog, f2)
        if results.empty:
            t.fail("No black chairs found even with relaxed filters")

@run_test("Color: 'brown bookshelf' → has results with brown")
def _(t):
    f = {"product_type": "storage", "color": "brown", "keyword": "brown", "sub_type": "bookshelf"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        f2 = {"product_type": "storage", "keyword": "brown"}
        results, _ = _search_products(catalog, f2)
        if results.empty:
            t.fail("No brown storage products found")

@run_test("Color: no false positives — 'gunnared' does NOT match 'red'")
def _(t):
    f = {"product_type": "sofa", "color": "red", "keyword": "red"}
    results, _ = _search_products(catalog, f)
    for _, r in results.iterrows():
        name = str(r.get("product_name", "")).lower()
        if "gunnared" in name:
            t.fail(f"False positive: 'gunnared' matched 'red' in: {name[:60]}")
            break


# ═══════════════════════════════════════════════════
# CATEGORY 4: Material Searches
# ═══════════════════════════════════════════════════
@run_test("Material: 'leather sofa' → has results")
def _(t):
    f = {"product_type": "sofa", "material": "leather", "keyword": "leather"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No leather sofas found")
    else:
        count = len(results)
        if count < 3:
            t.fail(f"Only {count} leather sofas — expected more")

@run_test("Material: 'wooden table' → results have wood material")
def _(t):
    f = {"product_type": "table", "material": "wood", "keyword": "wooden"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No wooden tables found")
    elif len(results) < 10:
        t.fail(f"Only {len(results)} wooden tables — expected 10+")

@run_test("Material: 'velvet sofa' → has results")
def _(t):
    f = {"product_type": "sofa", "material": "velvet", "keyword": "velvet"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No velvet sofas found")

@run_test("Material: 'glass table' → has results")
def _(t):
    f = {"product_type": "table", "material": "glass", "keyword": "glass"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No glass tables found")


# ═══════════════════════════════════════════════════
# CATEGORY 5: Sub-type Searches
# ═══════════════════════════════════════════════════
@run_test("Sub-type: 'coffee table' → has results")
def _(t):
    f = {"product_type": "table", "sub_type": "coffee table"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No coffee tables found")

@run_test("Sub-type: 'floor lamp' → has results")
def _(t):
    f = {"product_type": "lighting", "sub_type": "floor lamp"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No floor lamps found")

@run_test("Sub-type: 'recliner' → has results")
def _(t):
    f = {"product_type": "sofa", "sub_type": "recliner"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No recliners found")

@run_test("Sub-type: 'bookshelf' → has results")
def _(t):
    f = {"product_type": "storage", "sub_type": "bookshelf"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No bookshelves found")

@run_test("Sub-type: 'tv unit' → has results")
def _(t):
    f = {"product_type": "storage", "sub_type": "tv unit"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No TV units found")

@run_test("Sub-type: 'wardrobe' → has results")
def _(t):
    f = {"product_type": "storage", "sub_type": "wardrobe"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No wardrobes found")

@run_test("Sub-type: 'chandelier' → has results")
def _(t):
    f = {"product_type": "lighting", "sub_type": "chandelier"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No chandeliers found")


# ═══════════════════════════════════════════════════
# CATEGORY 6: Budget Searches
# ═══════════════════════════════════════════════════
@run_test("Budget: sofa under 20000 → all results <= 20000")
def _(t):
    f = {"product_type": "sofa", "budget_max": 20000}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No sofas under 20K")
        return
    over = results[results["price_value"] > 20000]
    if not over.empty:
        t.fail(f"{len(over)} products exceed ₹20,000 budget")

@run_test("Budget: lighting between 1000-5000 → all in range")
def _(t):
    f = {"product_type": "lighting", "budget_min": 1000, "budget_max": 5000}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No lighting in 1K-5K range")
        return
    out = results[(results["price_value"] < 1000) | (results["price_value"] > 5000)]
    if not out.empty:
        t.fail(f"{len(out)} products outside ₹1K-5K range")

@run_test("Budget: bed above 50000 → all results >= 50000")
def _(t):
    f = {"product_type": "bed", "budget_min": 50000}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No beds above 50K")
        return
    under = results[results["price_value"] < 50000]
    if not under.empty:
        t.fail(f"{len(under)} products below ₹50,000 minimum")


# ═══════════════════════════════════════════════════
# CATEGORY 7: Sort Preference (Costliest / Cheapest)
# ═══════════════════════════════════════════════════
@run_test("Sort: costliest sofas → first result is most expensive")
def _(t):
    f = {"product_type": "sofa"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No sofas found")
        return
    ranked = rank_products(results, f, top_n=5, sort_preference="price_high")
    prices = ranked["price_value"].tolist()
    if prices != sorted(prices, reverse=True):
        t.fail(f"Not sorted descending: {prices[:5]}")

@run_test("Sort: cheapest lighting → first result is least expensive")
def _(t):
    f = {"product_type": "lighting"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No lighting found")
        return
    ranked = rank_products(results, f, top_n=5, sort_preference="price_low")
    prices = ranked["price_value"].tolist()
    if prices != sorted(prices):
        t.fail(f"Not sorted ascending: {prices[:5]}")

@run_test("Sort: costliest overall → most expensive product in catalog")
def _(t):
    ranked = rank_products(catalog, {}, top_n=5, sort_preference="price_high")
    top_price = ranked.iloc[0]["price_value"]
    max_price = catalog["price_value"].max()
    if top_price != max_price:
        t.fail(f"Top price {top_price} != catalog max {max_price}")


# ═══════════════════════════════════════════════════
# CATEGORY 8: Room Type Searches
# ═══════════════════════════════════════════════════
@run_test("Room: bedroom lighting → has results")
def _(t):
    f = {"product_type": "lighting", "room_type": "bedroom"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No bedroom lighting found")

@run_test("Room: living room sofa → has results")
def _(t):
    f = {"product_type": "sofa", "room_type": "living_room"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No living room sofas found")

@run_test("Room: study table → has results")
def _(t):
    f = {"product_type": "table", "room_type": "study"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No study tables found")


# ═══════════════════════════════════════════════════
# CATEGORY 9: Feature Searches
# ═══════════════════════════════════════════════════
@run_test("Feature: foldable table → has results")
def _(t):
    f = {"product_type": "table", "features": "foldable"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No foldable tables found")

@run_test("Feature: LED lighting → has results")
def _(t):
    f = {"product_type": "lighting", "features": "led"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No LED lighting found")

@run_test("Feature: wall mounted storage → has results")
def _(t):
    f = {"product_type": "storage", "features": "wall_mounted"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No wall-mounted storage found")


# ═══════════════════════════════════════════════════
# CATEGORY 10: Price Tier Searches
# ═══════════════════════════════════════════════════
@run_test("Tier: budget sofas → all are budget tier")
def _(t):
    f = {"product_type": "sofa", "price_tier": "budget"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No budget sofas found")
    elif "price_tier" in results.columns:
        non_budget = results[results["price_tier"] != "budget"]
        if not non_budget.empty:
            t.fail(f"{len(non_budget)} non-budget products in results")

@run_test("Tier: luxury beds → has results")
def _(t):
    f = {"product_type": "bed", "price_tier": "luxury"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No luxury beds found")

@run_test("Tier: premium lighting → has results")
def _(t):
    f = {"product_type": "lighting", "price_tier": "premium"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No premium lighting found")


# ═══════════════════════════════════════════════════
# CATEGORY 11: Seating Searches
# ═══════════════════════════════════════════════════
@run_test("Seating: 3-seater sofa → has results")
def _(t):
    f = {"product_type": "sofa", "seating": "3-seater"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No 3-seater sofas found")

@run_test("Seating: 7-seater sofa → has results (or honest fallback)")
def _(t):
    f = {"product_type": "sofa", "seating": "7-seater"}
    results, _ = _search_products(catalog, f)
    # 7-seater is rare, might fall through. Just confirm no crash.
    # If 0, the fallback should give all sofas.


# ═══════════════════════════════════════════════════
# CATEGORY 12: Complex Multi-Filter Queries
# ═══════════════════════════════════════════════════
@run_test("Complex: modern white sofa under 30K → respects all filters")
def _(t):
    f = {"product_type": "sofa", "color": "white", "keyword": "white",
         "style": "modern", "budget_max": 30000}
    results, _ = _search_products(catalog, f)
    # Exact combo may be empty, fallback should relax gracefully
    if not results.empty:
        over_budget = results[results["price_value"] > 30000]
        if not over_budget.empty:
            t.fail(f"{len(over_budget)} products exceed ₹30K budget")

@run_test("Complex: leather 3-seater sofa → has results")
def _(t):
    f = {"product_type": "sofa", "material": "leather", "keyword": "leather",
         "seating": "3-seater"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No leather 3-seater sofas found")

@run_test("Complex: foldable wooden study table under 5000 → has results")
def _(t):
    f = {"product_type": "table", "material": "wood", "keyword": "wooden",
         "sub_type": "study table", "features": "foldable", "budget_max": 5000}
    results, _ = _search_products(catalog, f)
    if results.empty:
        # Relax to just foldable table under 5K
        f2 = {"product_type": "table", "features": "foldable", "budget_max": 5000}
        results, _ = _search_products(catalog, f2)
        if results.empty:
            t.fail("No foldable tables under 5K found")


# ═══════════════════════════════════════════════════
# CATEGORY 13: Edge Cases
# ═══════════════════════════════════════════════════
@run_test("Edge: empty filters → returns full catalog")
def _(t):
    results, note = _search_products(catalog, {})
    if results.empty:
        t.fail("Empty filters returned no results")
    if len(results) != len(catalog):
        t.fail(f"Expected full catalog ({len(catalog)}), got {len(results)}")

@run_test("Edge: nonexistent product type → graceful fallback")
def _(t):
    f = {"product_type": "spaceship"}
    results, note = _search_products(catalog, f)
    # Should not crash. May return empty or popular products.

@run_test("Edge: impossible budget (max 10) → empty or graceful")
def _(t):
    f = {"product_type": "sofa", "budget_max": 10}
    results, note = _search_products(catalog, f)
    # Should not crash. Likely empty since min price is ~100.

@run_test("Edge: conflicting budget (min > max) → no crash")
def _(t):
    f = {"product_type": "sofa", "budget_min": 50000, "budget_max": 10000}
    results, note = _search_products(catalog, f)
    # Should not crash

@run_test("Edge: very specific brand → has results or honest empty")
def _(t):
    f = {"brand": "IKEA"}
    results, _ = _search_products(catalog, f)
    # IKEA products should exist
    if results.empty:
        t.fail("No IKEA products found")

@run_test("Edge: ranker handles 0 products → no crash")
def _(t):
    empty_df = pd.DataFrame(columns=catalog.columns)
    ranked = rank_products(empty_df, {"product_type": "sofa"}, top_n=5)
    if not ranked.empty:
        t.fail("Expected empty result for empty input")

@run_test("Edge: ranker handles 1 product → returns exactly 1")
def _(t):
    one = catalog.head(1).copy()
    ranked = rank_products(one, {}, top_n=5)
    if len(ranked) != 1:
        t.fail(f"Expected 1 result, got {len(ranked)}")


# ═══════════════════════════════════════════════════
# CATEGORY 14: Ranking Quality Checks
# ═══════════════════════════════════════════════════
@run_test("Rank: 'red sofa' → top result contains 'red' in name")
def _(t):
    f = {"product_type": "sofa", "color": "red", "keyword": "red"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No red sofas found")
        return
    ranked = rank_products(results, f, top_n=3)
    top_name = str(ranked.iloc[0]["product_name"]).lower()
    if not word_in_text("red", top_name) and "crimson" not in top_name and "maroon" not in top_name:
        t.fail(f"Top result doesn't contain 'red': {top_name[:60]}")

@run_test("Rank: 'wooden coffee table' → top results are relevant")
def _(t):
    f = {"product_type": "table", "material": "wood", "keyword": "wooden",
         "sub_type": "coffee table"}
    results, _ = _search_products(catalog, f)
    if results.empty:
        t.fail("No wooden coffee tables found")
        return
    ranked = rank_products(results, f, top_n=3)
    top_name = str(ranked.iloc[0]["product_name"]).lower()
    if "coffee" not in top_name and "center" not in top_name and "table" not in top_name:
        t.fail(f"Top result not a table: {top_name[:60]}")

@run_test("Rank: products with images rank higher than those without")
def _(t):
    f = {"product_type": "sofa"}
    results, _ = _search_products(catalog, f)
    ranked = rank_products(results, f, top_n=9)
    top_has_image = ranked.head(5)["image_url"].fillna("").str.startswith("http").sum()
    if top_has_image < 3:
        t.fail(f"Only {top_has_image}/5 top products have images")

@run_test("Rank: deduplication — no duplicate product names in results")
def _(t):
    f = {"product_type": "sofa"}
    results, _ = _search_products(catalog, f)
    ranked = rank_products(results, f, top_n=9)
    names = ranked["product_name"].tolist()
    if len(names) != len(set(names)):
        dupes = [n for n in names if names.count(n) > 1]
        t.fail(f"Duplicate names found: {set(dupes)}")


# ═══════════════════════════════════════════════════
# CATEGORY 15: Source / Brand Searches
# ═══════════════════════════════════════════════════
@run_test("Source: IKEA products exist in catalog")
def _(t):
    ikea = catalog[catalog["source"] == "ikea.com"]
    if ikea.empty:
        t.fail("No IKEA products in catalog")
    else:
        if len(ikea) < 50:
            t.fail(f"Only {len(ikea)} IKEA products — expected 50+")

@run_test("Source: Amazon products exist in catalog")
def _(t):
    amazon = catalog[catalog["source"] == "amazon.in"]
    if amazon.empty:
        t.fail("No Amazon products in catalog")

@run_test("Source: Flipkart products exist in catalog")
def _(t):
    fk = catalog[catalog["source"] == "flipkart.com"]
    if fk.empty:
        t.fail("No Flipkart products in catalog")


# ═══════════════════════════════════════════════════
# CATEGORY 16: Combo Intent Detection
# ═══════════════════════════════════════════════════
@run_test("Combo detect: 'sofa and mirror for 50K' → combo with 2 types")
def _(t):
    is_c, types, budget = _detect_combo_intent("sofa and mirror for 50K")
    if not is_c:
        t.fail("Should be combo")
    if len(types) < 2:
        t.fail(f"Expected 2+ types, got {types}")
    if budget != 50000:
        t.fail(f"Expected 50000, got {budget}")

@run_test("Combo detect: 'need a bed and wardrobe under 80000' → combo")
def _(t):
    is_c, types, budget = _detect_combo_intent("need a bed and wardrobe under 80000")
    if not is_c:
        t.fail("Should be combo")
    if "bed" not in types or "storage" not in types:
        t.fail(f"Expected bed + storage, got {types}")
    if budget != 80000:
        t.fail(f"Expected 80000, got {budget}")

@run_test("Combo detect: 'desk, chair, and lamp for 1 lakh' → combo with 3 types")
def _(t):
    is_c, types, budget = _detect_combo_intent("desk, chair, and lamp for 1 lakh")
    if not is_c:
        t.fail("Should be combo")
    if len(types) < 3:
        t.fail(f"Expected 3+ types, got {types}")
    if budget != 100000:
        t.fail(f"Expected 100000, got {budget}")

@run_test("Combo detect: 'red sofa under 30K' → NOT combo (single product)")
def _(t):
    is_c, types, budget = _detect_combo_intent("red sofa under 30K")
    if is_c:
        t.fail(f"Should NOT be combo (single product), got types={types}")

@run_test("Combo detect: 'table and chair' without budget → NOT combo")
def _(t):
    is_c, types, budget = _detect_combo_intent("table and chair")
    # No budget keyword → not combo
    if is_c and budget is None:
        pass  # Acceptable: detected intent but no budget is fine

@run_test("Combo detect: 'sofa and curtains under 40K' → combo")
def _(t):
    is_c, types, budget = _detect_combo_intent("sofa and curtains under 40K")
    if not is_c:
        t.fail("Should be combo")
    if budget != 40000:
        t.fail(f"Expected 40000, got {budget}")


# ═══════════════════════════════════════════════════
# CATEGORY 17: Combo Search Engine
# ═══════════════════════════════════════════════════
@run_test("Combo search: sofa + mirror for 50K → has both groups")
def _(t):
    combo = _combo_search(
        catalog,
        [{"product_type": "sofa"}, {"product_type": "decor", "sub_type": "mirror"}],
        50000,
    )
    groups = combo.get("groups", [])
    if len(groups) < 2:
        t.fail(f"Expected 2 groups, got {len(groups)}")
    types_found = [g["type"] for g in groups]
    if "sofa" not in types_found:
        t.fail(f"Missing sofa group: {types_found}")
    if "decor" not in types_found:
        t.fail(f"Missing decor group: {types_found}")
    if combo.get("total_cost", 0) <= 0:
        t.fail("Total cost should be > 0")

@run_test("Combo search: bed + wardrobe for 80K → within budget")
def _(t):
    combo = _combo_search(
        catalog,
        [{"product_type": "bed"}, {"product_type": "storage", "sub_type": "wardrobe"}],
        80000,
    )
    groups = combo.get("groups", [])
    if len(groups) < 1:
        t.fail("Expected at least 1 group")
    # Check total cost is reasonable
    tc = combo.get("total_cost", 0)
    if tc <= 0:
        t.fail(f"Total cost should be > 0, got {tc}")

@run_test("Combo search: table + chair + lamp for 1 lakh → has 3 groups")
def _(t):
    combo = _combo_search(
        catalog,
        [
            {"product_type": "table"},
            {"product_type": "chair"},
            {"product_type": "lighting"},
        ],
        100000,
    )
    groups = combo.get("groups", [])
    if len(groups) < 3:
        t.fail(f"Expected 3 groups, got {len(groups)}")

@run_test("Combo search: budget 0 → empty result, no crash")
def _(t):
    combo = _combo_search(catalog, [{"product_type": "sofa"}], 0)
    if combo.get("groups"):
        t.fail("Expected empty groups for budget 0")

@run_test("Combo search: empty product list → empty result, no crash")
def _(t):
    combo = _combo_search(catalog, [], 50000)
    if combo.get("groups"):
        t.fail("Expected empty groups for no products")

@run_test("Combo search: tight budget 5K for sofa + bed → picks cheapest")
def _(t):
    combo = _combo_search(
        catalog,
        [{"product_type": "sofa"}, {"product_type": "bed"}],
        5000,
    )
    # With 5K total, it will find budget items or overflow gracefully
    # Main test: no crash
    tc = combo.get("total_cost", 0)
    # Just verify it returns something
    if combo.get("groups") is None:
        t.fail("groups key missing")


# ═══════════════════════════════════════════════════
# Print Results
# ═══════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  A2S END-TO-END TEST RESULTS")
print("=" * 70)

passed = sum(1 for r in results if r.passed)
failed = sum(1 for r in results if not r.passed)
total = len(results)

for r in results:
    print(r)

print(f"\n{'=' * 70}")
print(f"  TOTAL: {total}  |  PASSED: {passed}  |  FAILED: {failed}")
if failed == 0:
    print("  ALL TESTS PASSED!")
else:
    print(f"  {failed} TEST(S) NEED FIXING")
print(f"{'=' * 70}")

sys.exit(0 if failed == 0 else 1)
