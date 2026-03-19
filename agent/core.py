"""
Core AI Agent – The brain of A2S.

Orchestrates the full pipeline:
    1. Receives user message + full conversation history
    2. Sends to Gemini with system prompt for intent + entity extraction
    3. Parses the structured JSON response
    4. Runs the filter engine on the product catalog
    5. Ranks results
    6. Returns natural language response + product cards

Uses the new `google.genai` SDK.
"""

from __future__ import annotations

import json
import re
import traceback

from google import genai
from google.genai import types
import pandas as pd

from config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE, TOP_P, MAX_RESULTS_PER_QUERY
from agent.prompts import SYSTEM_PROMPT
from agent.context import (
    get_messages_for_llm,
    update_filters,
    get_active_filters,
    reset_filters,
    set_last_products,
)
from data.filter_engine import filter_products
from data.ranker import rank_products


# ──────────────────────────────────────────────
# Configure Gemini client (lazy init)
# ──────────────────────────────────────────────
_client = None


def _get_client():
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key not set. Set GEMINI_API_KEY in config.py or as environment variable.")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


# ──────────────────────────────────────────────
# JSON response parser
# ──────────────────────────────────────────────
def _parse_agent_response(raw_text: str) -> dict:
    """Parse Gemini's JSON response with robust fallback."""
    text = raw_text.strip()

    # Strip markdown fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Fallback
    return {
        "filters": {},
        "response_text": raw_text,
        "show_products": True,
        "is_reset": False,
        "topic_changed": False,
    }


def _build_contents(history_msgs: list[dict], current_message: str) -> list[types.Content]:
    """Build contents list for Gemini API."""
    contents = []
    for msg in history_msgs:
        role = msg["role"]
        text = msg["parts"][0]["text"]
        contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=text)])
        )
    contents.append(
        types.Content(role="user", parts=[types.Part.from_text(text=current_message)])
    )
    return contents


def _clean_response_text(text: str) -> str:
    """
    Clean up Gemini's response text:
    - Strip filler phrases that add no value
    - Truncate overly long responses
    - Ensure it's not empty
    """
    if not text:
        return "Here are products matching your search!"

    # Remove common filler starts
    filler_starts = [
        "Certainly! ", "Of course! ", "Sure! ", "Absolutely! ",
        "I'd be happy to help! ", "Great question! ",
        "Let me search ", "I'm searching ", "Looking for ",
        "I'll look ", "Searching through ", "I'll filter ",
        "Based on your requirements, ", "I understand you're looking for ",
    ]
    cleaned = text
    for filler in filler_starts:
        if cleaned.startswith(filler):
            cleaned = cleaned[len(filler):]
            # Capitalize the remaining text
            if cleaned:
                cleaned = cleaned[0].upper() + cleaned[1:]
            break

    # Truncate if way too long (more than 300 chars)
    if len(cleaned) > 300:
        # Find a good break point
        cut = cleaned[:300]
        last_period = cut.rfind(".")
        last_excl = cut.rfind("!")
        last_q = cut.rfind("?")
        best_break = max(last_period, last_excl, last_q)
        if best_break > 100:
            cleaned = cleaned[:best_break + 1]
        else:
            cleaned = cut.rstrip() + "..."

    return cleaned.strip() or "Here are products matching your search!"


def _has_product_intent(message: str) -> bool:
    """Check if the user message is asking about products (not just chatting)."""
    product_keywords = [
        "sofa", "bed", "light", "lamp", "mirror", "curtain", "clock",
        "vase", "furniture", "decor", "chair", "table", "desk", "show",
        "find", "give", "want", "need", "suggest", "recommend", "search",
        "cheapest", "costliest", "expensive", "budget", "under", "above",
        "below", "price", "buy", "room", "bedroom", "living", "dining",
        "study", "kids", "ikea", "modern", "ethnic", "classic", "product",
        "wardrobe", "bookshelf", "tv unit", "storage", "rug", "stool",
        "pendant", "ceiling", "floor lamp", "mattress", "recliner",
        "amazon", "flipkart", "shelf", "cabinet",
    ]
    msg_lower = message.lower()
    return any(kw in msg_lower for kw in product_keywords)


def _detect_sort_preference(message: str) -> str | None:
    """
    Detect if user wants results sorted by price.
    Returns "price_high", "price_low", or None.
    """
    msg = message.lower()
    high_keywords = [
        "costliest", "most expensive", "expensive", "highest price",
        "premium", "luxury", "high end", "high-end", "top end",
        "priciest", "rich", "best quality", "top range",
    ]
    low_keywords = [
        "cheapest", "lowest price", "most affordable", "budget",
        "inexpensive", "economical", "value for money", "cheap",
        "low cost", "low price", "least expensive",
    ]
    for kw in high_keywords:
        if kw in msg:
            return "price_high"
    for kw in low_keywords:
        if kw in msg:
            return "price_low"
    return None


def _detect_product_type_from_message(message: str) -> str | None:
    """
    Detect product type directly from user message as a safety net
    in case Gemini doesn't extract it properly.
    """
    msg = message.lower()
    mapping = {
        "lighting": ["light", "lamp", "chandelier", "pendant", "bulb", "led strip"],
        "table": ["table", "desk", "coffee table", "dining table", "study table", "center table"],
        "sofa": ["sofa", "couch", "recliner", "loveseat", "settee"],
        "bed": ["bed", "mattress", "bunk bed", "cot"],
        "storage": ["wardrobe", "bookshelf", "shelf", "cabinet", "tv unit", "almirah", "cupboard", "drawer"],
        "decor": ["mirror", "clock", "vase", "frame", "plant", "decorative", "wall art"],
        "chair": ["chair", "stool", "bench", "seating"],
        "textile": ["curtain", "rug", "carpet", "throw", "blanket", "towel", "bedspread"],
    }
    for ptype, keywords in mapping.items():
        for kw in keywords:
            if kw in msg:
                return ptype
    return None


# ── Well-known colors for safety-net extraction ──
_COLORS = [
    "red", "blue", "green", "black", "white", "grey", "gray", "brown",
    "yellow", "pink", "beige", "orange", "purple", "cream", "maroon",
    "teal", "navy", "gold", "silver", "ivory", "turquoise", "coral",
    "magenta", "olive", "burgundy", "tan", "peach", "charcoal",
]

_MATERIALS = [
    "wood", "wooden", "metal", "fabric", "leather", "velvet", "glass",
    "plastic", "rattan", "marble", "bamboo", "steel", "iron", "oak",
    "teak", "pine", "plywood", "mdf", "ceramic", "cotton", "linen",
    "jute", "cane", "wicker", "acacia", "sheesham",
]


def _detect_color_from_message(message: str) -> str | None:
    """Detect explicit color from user message."""
    msg = message.lower()
    for c in _COLORS:
        # word boundary check: "red" but not "bored"
        if f" {c} " in f" {msg} ":
            return c
    return None


def _detect_material_from_message(message: str) -> str | None:
    """Detect explicit material from user message."""
    msg = message.lower()
    for m in _MATERIALS:
        if f" {m} " in f" {msg} ":
            return m
    return None


# ──────────────────────────────────────────────
# Search products with aggressive fallback
# ──────────────────────────────────────────────
def _search_products(catalog: pd.DataFrame, merged_filters: dict) -> tuple[pd.DataFrame, str]:
    """
    Search for products with progressive filter relaxation.

    RULE: If exact filters find ANY results, return ONLY those.
          Never pad with unrelated products. Only relax when zero matches.

    Returns:
        (result_df, note_text) — the matched products and any note about relaxation.
    """
    note = ""

    if not merged_filters:
        note = "\n\n*Here are some popular products from our catalog:*"
        return catalog, note

    # STAGE 1: Try ALL filters exactly as given
    filtered = filter_products(catalog, merged_filters)
    if not filtered.empty:
        return filtered, note

    # STAGE 2: Drop room_type (many products lack this)
    relaxed = {k: v for k, v in merged_filters.items() if k != "room_type"}
    if relaxed != merged_filters and relaxed:
        filtered = filter_products(catalog, relaxed)
        if not filtered.empty:
            return filtered, note

    # STAGE 3: product_type + color/keyword/material
    ptype = merged_filters.get("product_type")
    color = merged_filters.get("color")
    keyword = merged_filters.get("keyword")
    material = merged_filters.get("material")

    if ptype and (color or keyword or material):
        core = {"product_type": ptype}
        if color:
            core["color"] = color
        if keyword:
            core["keyword"] = keyword
        if material:
            core["material"] = material
        filtered = filter_products(catalog, core)
        if not filtered.empty:
            return filtered, note

    # STAGE 4: product_type + keyword only (color might be too restrictive)
    if ptype and keyword:
        filtered = filter_products(catalog, {"product_type": ptype, "keyword": keyword})
        if not filtered.empty:
            return filtered, note

    # STAGE 5: product_type + budget
    if ptype:
        core = {"product_type": ptype}
        for k in ["budget_min", "budget_max"]:
            if k in merged_filters:
                core[k] = merged_filters[k]
        filtered = filter_products(catalog, core)
        if not filtered.empty:
            return filtered, note

    # STAGE 6: Just product_type — with honest note
    if ptype:
        filtered = filter_products(catalog, {"product_type": ptype})
        if not filtered.empty:
            specifics = []
            if color:
                specifics.append(f"**{color}**")
            if material:
                specifics.append(f"**{material}**")
            if specifics:
                note = f"\n\n*No {' '.join(specifics)} {ptype}s found. Showing all {ptype}s instead:*"
            return filtered, note

    # STAGE 7: Just keyword search across everything
    if keyword:
        filtered = filter_products(catalog, {"keyword": keyword})
        if not filtered.empty:
            note = f"\n\n*Showing products matching **{keyword}**:*"
            return filtered, note

    # STAGE 8: Just color search across everything
    if color:
        filtered = filter_products(catalog, {"keyword": color})
        if not filtered.empty:
            note = f"\n\n*Showing **{color}** products:*"
            return filtered, note

    # STAGE 9: decor_type
    dtype = merged_filters.get("decor_type")
    if dtype:
        filtered = filter_products(catalog, {"decor_type": dtype})
        if not filtered.empty:
            note = f"\n\n*Showing all **{dtype}** products:*"
            return filtered, note

    # STAGE 10: Nothing matched at all
    note = "\n\n*No matching products found. Try a broader search like \"show me sofas\" or \"start over\".*"
    return pd.DataFrame(), note


# ──────────────────────────────────────────────
# Combo / Multi-Product Search
# ──────────────────────────────────────────────

# Budget allocation weights by product type (higher = more expensive category)
_BUDGET_WEIGHTS = {
    "sofa": 5, "bed": 5, "storage": 3, "table": 3,
    "chair": 2, "lighting": 2, "decor": 1, "textile": 1, "misc": 1,
}


def _combo_search(
    catalog: pd.DataFrame,
    combo_products: list[dict],
    total_budget: float,
    top_per_type: int = 3,
) -> dict:
    """
    Search for multiple product types within a total budget.

    Strategy:
        1. Allocate budget proportionally by product type weight
        2. Give each category a 30% buffer (so we don't miss borderline items)
        3. Search each type independently
        4. Pick the best combination that fits within total budget

    Args:
        catalog:        The product catalog
        combo_products: List of filter dicts, one per product type
        total_budget:   Total budget across all products
        top_per_type:   Max products to show per type

    Returns:
        dict with:
            - groups: list of {type, label, products, budget_slice}
            - total_cost: total cost of the recommended combo
            - total_budget: the user's budget
            - within_budget: bool
    """
    if not combo_products or total_budget <= 0:
        return {"groups": [], "total_cost": 0, "total_budget": total_budget, "within_budget": True}

    # ── Step 1: Calculate budget allocation ──
    types = []
    for pf in combo_products:
        pt = pf.get("product_type", "misc")
        types.append(pt)

    total_weight = sum(_BUDGET_WEIGHTS.get(pt, 1) for pt in types)
    allocations = {}
    for pt in types:
        weight = _BUDGET_WEIGHTS.get(pt, 1)
        share = (weight / total_weight) * total_budget
        # Give 30% buffer so we don't miss borderline products
        allocations[pt] = share * 1.3

    # ── Step 2: Search each product type ──
    groups = []
    for pf in combo_products:
        pt = pf.get("product_type", "misc")
        budget_slice = allocations.get(pt, total_budget * 0.5)

        # Build filter with budget cap
        search_filter = dict(pf)
        search_filter["budget_max"] = budget_slice

        results, _ = _search_products(catalog, search_filter)

        if results.empty:
            # Relax: try without budget cap
            search_filter.pop("budget_max", None)
            results, _ = _search_products(catalog, search_filter)

        if not results.empty:
            # Use the ranker for quality-based sorting (not just cheapest)
            ranked = rank_products(results, search_filter, top_n=top_per_type)

            sub_type = pf.get("sub_type", "")
            label = sub_type.title() if sub_type else pt.replace("_", " ").title()

            groups.append({
                "type": pt,
                "label": label,
                "products": ranked.to_dict("records"),
                "budget_slice": budget_slice,
            })

    # ── Step 3: Build the best combo within budget ──
    # Pick the cheapest from each group and check total
    total_cost = 0
    for g in groups:
        if g["products"]:
            cheapest = min(p.get("price_value", 0) for p in g["products"])
            total_cost += cheapest

    return {
        "groups": groups,
        "total_cost": total_cost,
        "total_budget": total_budget,
        "within_budget": total_cost <= total_budget,
    }


def _detect_combo_intent(message: str) -> tuple[bool, list[str], float | None]:
    """
    Safety net: detect if user wants multiple product types in one budget.

    Returns:
        (is_combo, list_of_product_types, total_budget_or_None)
    """
    msg = message.lower()

    # Must mention a budget keyword
    has_budget = any(kw in msg for kw in [
        "budget", "under", "within", "total", "for", "in",
        "rs", "₹", "rupee", "inr", "lakh", "k ",
    ])
    if not has_budget:
        return False, [], None

    # Must mention multiple product types connected by "and" / "&" / "," / "+"
    connectors = [" and ", " & ", " + ", ", "]
    has_connector = any(c in msg for c in connectors)
    if not has_connector:
        return False, [], None

    # Detect all product types mentioned
    type_mapping = {
        "sofa": "sofa", "couch": "sofa", "recliner": "sofa",
        "bed": "bed", "mattress": "bed",
        "light": "lighting", "lamp": "lighting", "chandelier": "lighting",
        "table": "table", "desk": "table",
        "chair": "chair", "stool": "chair",
        "storage": "storage", "wardrobe": "storage", "bookshelf": "storage",
        "shelf": "storage", "cabinet": "storage", "tv unit": "storage",
        "mirror": "decor", "clock": "decor", "vase": "decor", "decor": "decor",
        "curtain": "textile", "rug": "textile", "carpet": "textile",
    }

    found_types = []
    for keyword, ptype in type_mapping.items():
        if keyword in msg and ptype not in found_types:
            found_types.append(ptype)

    if len(found_types) < 2:
        return False, [], None

    # Try to extract budget amount
    budget = None
    # Match patterns like "50000", "50K", "50k", "1 lakh", "₹50000"
    budget_match = re.search(r'(\d+(?:,\d+)*)\s*(?:k|K)', msg)
    if budget_match:
        budget = float(budget_match.group(1).replace(",", "")) * 1000
    else:
        budget_match = re.search(r'(\d+(?:,\d+)*)\s*(?:lakh|lac)', msg)
        if budget_match:
            budget = float(budget_match.group(1).replace(",", "")) * 100000
        else:
            budget_match = re.search(r'(?:₹|rs\.?|inr)\s*(\d+(?:,\d+)*)', msg)
            if budget_match:
                budget = float(budget_match.group(1).replace(",", ""))
            else:
                budget_match = re.search(r'(\d{4,})', msg)
                if budget_match:
                    budget = float(budget_match.group(1).replace(",", ""))

    return True, found_types, budget


# ──────────────────────────────────────────────
# Main agent function
# ──────────────────────────────────────────────
def process_message(
    user_message: str,
    catalog: pd.DataFrame,
) -> dict:
    """
    Process a user message and return the agent's response with products.
    """
    result = {
        "response_text": "",
        "products": None,
        "filters": {},
        "error": None,
    }

    try:
        # ── Build conversation for Gemini ──
        history = get_messages_for_llm()

        active = get_active_filters()
        context_note = ""
        if active:
            context_note = f"[SYSTEM: Current accumulated filters: {json.dumps(active)}]\n\n"

        full_message = context_note + user_message
        contents = _build_contents(history, full_message)

        # ── Call Gemini ──
        client = _get_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                response_mime_type="application/json",
            ),
        )

        # ── Parse response ──
        raw_text = response.text or ""
        parsed = _parse_agent_response(raw_text)

        response_text = parsed.get("response_text", "Let me find products for you!")
        # ── Guardrail: clean up response text ──
        response_text = _clean_response_text(response_text)
        raw_filters = parsed.get("filters", {})
        # CRITICAL: Strip null/None values — Gemini sometimes returns them explicitly
        filters = {k: v for k, v in raw_filters.items() if v is not None}
        show_products = parsed.get("show_products", True)
        is_reset = parsed.get("is_reset", False)
        topic_changed = parsed.get("topic_changed", False)

        # ── Handle reset ──
        if is_reset:
            reset_filters()
            result["response_text"] = response_text
            result["filters"] = {}
            set_last_products(None)
            return result

        # ── Handle topic change: CLEAR old filters before applying new ones ──
        if topic_changed:
            reset_filters()

        # ── Safety net: detect topic change from message even if Gemini missed it ──
        if not topic_changed and active.get("product_type"):
            detected_type = _detect_product_type_from_message(user_message)
            old_type = active.get("product_type")
            if detected_type and detected_type != old_type:
                # User switched products! Clear old filters.
                reset_filters()
                topic_changed = True

        # ── Safety net: ensure product_type is set from message if Gemini missed it ──
        if not filters.get("product_type"):
            detected_type = _detect_product_type_from_message(user_message)
            if detected_type:
                filters["product_type"] = detected_type

        # ── Safety net: ensure color is extracted if Gemini missed it ──
        detected_color = _detect_color_from_message(user_message)
        if detected_color:
            if not filters.get("color"):
                filters["color"] = detected_color
            # ALWAYS also set keyword to color so we search product names
            if not filters.get("keyword"):
                filters["keyword"] = detected_color

        # ── Safety net: ensure material is extracted if Gemini missed it ──
        detected_mat = _detect_material_from_message(user_message)
        if detected_mat:
            if not filters.get("material"):
                filters["material"] = detected_mat
            if not filters.get("keyword"):
                filters["keyword"] = detected_mat

        # ── Update accumulated filters ──
        clean_filters = {k: v for k, v in filters.items() if v is not None}
        if clean_filters:
            update_filters(clean_filters)

        merged_filters = get_active_filters()
        result["filters"] = merged_filters

        # ── Check for COMBO request (multiple product types in one budget) ──
        is_combo = parsed.get("is_combo", False)
        combo_products = parsed.get("combo_products", [])
        total_budget = parsed.get("total_budget")

        # Safety net: detect combo from message if Gemini missed it
        if not is_combo:
            detected_combo, detected_types, detected_budget = _detect_combo_intent(user_message)
            if detected_combo and len(detected_types) >= 2:
                is_combo = True
                combo_products = [{"product_type": pt} for pt in detected_types]
                if detected_budget:
                    total_budget = detected_budget

        # ── COMBO PATH: multiple products in one budget ──
        if is_combo and combo_products and total_budget:
            reset_filters()  # Combo is always a fresh search
            combo_result = _combo_search(catalog, combo_products, total_budget)
            result["combo"] = combo_result
            result["response_text"] = response_text

            # Also flatten all products for context storage
            all_products = []
            for g in combo_result.get("groups", []):
                all_products.extend(g.get("products", []))
            if all_products:
                result["products"] = all_products
                set_last_products(all_products)

            return result

        # ── SINGLE PRODUCT PATH (existing flow) ──
        user_wants_products = _has_product_intent(user_message)
        should_show = show_products or user_wants_products or bool(merged_filters)

        if should_show:
            search_results, search_note = _search_products(catalog, merged_filters)

            # Detect sort preference from the user's message
            sort_pref = _detect_sort_preference(user_message)

            if not search_results.empty:
                ranked = rank_products(search_results, merged_filters, top_n=MAX_RESULTS_PER_QUERY, sort_preference=sort_pref)
                products_list = ranked.to_dict("records")
                result["products"] = products_list
                set_last_products(products_list)
                response_text += search_note
            else:
                response_text += (
                    "\n\n😔 I searched the entire catalog but couldn't find matches.\n"
                    "Try: *\"show me all lighting\"* or *\"start over\"* to reset."
                )

        result["response_text"] = response_text

    except Exception as e:
        error_str = str(e)
        traceback.print_exc()

        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            result["error"] = "Gemini API rate limit reached. Quota resets daily."
            result["response_text"] = (
                "⏳ I'm temporarily rate-limited by the Gemini API.\n\n"
                "**Switch to the 🛍️ Browse Products tab** to explore products manually with filters!"
            )
        else:
            result["error"] = f"Error: {error_str}"
            result["response_text"] = (
                "Something went wrong processing your request. "
                "Please try rephrasing or say **\"start over\"** to reset."
            )

    return result


def _relax_filters(filters: dict) -> dict:
    """Remove non-essential filters, keep core (type, budget, color, keyword)."""
    relaxed = filters.copy()
    # Keep: product_type, budget_min, budget_max, color, keyword, material
    for key in ["decor_type", "role_in_design", "style",
                "color_palette", "brand", "room_type",
                "min_width", "max_width",
                "min_depth", "max_depth", "min_height", "max_height"]:
        relaxed.pop(key, None)
    return relaxed
