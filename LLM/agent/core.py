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
# Configure Gemini client
# ──────────────────────────────────────────────
try:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "PLACEHOLDER_API_KEY":
        print("⚠️ GEMINI_API_KEY is missing or placeholder. Running in Mock Mode.")
        _client = None
    else:
        _client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"⚠️ Failed to initialize Gemini client: {e}. Running in Mock Mode.")
    _client = None


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


# ──────────────────────────────────────────────
# Search products with aggressive fallback
# ──────────────────────────────────────────────
def _search_products(catalog: pd.DataFrame, merged_filters: dict) -> tuple[pd.DataFrame, str]:
    """
    Search for products with progressive filter relaxation.
    Key fix: if room_type filter eliminates too many results,
    drop it early since scraped data doesn't have room_type.

    Returns:
        (result_df, note_text) — the matched products and any note about relaxation.
    """
    note = ""

    # STAGE 1: Try exact filters
    if merged_filters:
        filtered = filter_products(catalog, merged_filters)
        if len(filtered) >= 3:
            return filtered, note

    # STAGE 2: Drop room_type (scraped data has no room_type)
    if merged_filters and "room_type" in merged_filters:
        no_room = {k: v for k, v in merged_filters.items() if k != "room_type"}
        if no_room:
            filtered = filter_products(catalog, no_room)
            if len(filtered) >= 3:
                note = ""  # Don't mention relaxation if we still match by product type
                return filtered, note

    # STAGE 3: Keep only product_type + budget
    if merged_filters:
        core = {}
        for k in ["product_type", "budget_min", "budget_max"]:
            if k in merged_filters:
                core[k] = merged_filters[k]
        if core:
            filtered = filter_products(catalog, core)
            if not filtered.empty:
                return filtered, note

    # STAGE 4: Just product_type
    ptype = merged_filters.get("product_type") if merged_filters else None
    if ptype:
        filtered = filter_products(catalog, {"product_type": ptype})
        if not filtered.empty:
            note = f"\n\n*Showing all **{ptype}** products from our catalog:*"
            return filtered, note

    # STAGE 5: Keyword search in product_name
    keyword = merged_filters.get("keyword") if merged_filters else None
    if keyword:
        filtered = filter_products(catalog, {"keyword": keyword})
        if not filtered.empty:
            note = f"\n\n*Showing products matching **{keyword}**:*"
            return filtered, note

    # STAGE 6: decor_type
    dtype = merged_filters.get("decor_type") if merged_filters else None
    if dtype:
        filtered = filter_products(catalog, {"decor_type": dtype})
        if not filtered.empty:
            note = f"\n\n*Showing all **{dtype}** products:*"
            return filtered, note

    # STAGE 7: Return popular products
    note = "\n\n*Here are some popular products from our catalog:*"
    return catalog, note


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

        if _client is None:
            # Mock behavior
            response_text = f"I'm running in mock mode because no Gemini API key was found. You asked: '{user_message}'. I'll simulate a response."
            parsed = {
                "response_text": response_text,
                "filters": _detect_product_type_from_message(user_message) or {},
                "show_products": True
            }
        else:
            # ── Call Gemini ──
            response = _client.models.generate_content(
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
        filters = parsed.get("filters", {})
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

        # ── Update accumulated filters ──
        clean_filters = {k: v for k, v in filters.items() if v is not None}
        if clean_filters:
            update_filters(clean_filters)

        merged_filters = get_active_filters()
        result["filters"] = merged_filters

        # ── ALWAYS try to show products if user is asking about products ──
        user_wants_products = _has_product_intent(user_message)
        should_show = show_products or user_wants_products or bool(merged_filters)

        if should_show:
            search_results, search_note = _search_products(catalog, merged_filters)

            if not search_results.empty:
                ranked = rank_products(search_results, merged_filters, top_n=MAX_RESULTS_PER_QUERY)
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


def process_vastu(room_type: str, description: str) -> dict:
    """Perform a Vastu audit for a room."""
    prompt = (
        f"Perform a strict Vastu Shastra audit for a {room_type}. "
        f"Here is the description of the items and layout: {description}. "
        "Provide an output in JSON format with fields: "
        "score (0-10), summary, pros (array of strings), cons (array of strings). "
        "Do not include markdown formatting like ```json."
    )

    try:
        if _client is None:
            return {
                "score": 8,
                "summary": f"Mock Vastu audit for your {room_type}. Everything looks good for now!",
                "pros": ["Good lighting", "Open space"],
                "cons": ["Maybe add a plant in the corner"],
                "is_mock": True
            }

        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
            config=types.GenerateContentConfig(
                temperature=TEMPERATURE,
                response_mime_type="application/json",
            ),
        )
        
        raw_text = response.text or "{}"
        return _parse_agent_response(raw_text)

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

def _relax_filters(filters: dict) -> dict:
    """Remove non-essential filters, keep core (type, budget)."""
    relaxed = filters.copy()
    for key in ["decor_type", "role_in_design", "keyword", "style",
                "color_palette", "brand", "room_type",
                "min_width", "max_width",
                "min_depth", "max_depth", "min_height", "max_height"]:
        relaxed.pop(key, None)
    return relaxed
