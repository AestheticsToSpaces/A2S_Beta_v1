"""
Live Gemini Response Quality Test.

Sends real queries to Gemini and checks:
  1. Does it return valid JSON?
  2. Are the extracted filters correct?
  3. Is the response_text sensible (not empty, not generic)?
  4. Are the new fields (is_combo, combo_products, total_budget) present?

Run:  python -m tests.test_gemini_live
"""

from __future__ import annotations
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE, TOP_P
from agent.prompts import SYSTEM_PROMPT
from agent.core import _parse_agent_response


client = genai.Client(api_key=GEMINI_API_KEY)

# ─── Test queries and expected filters ───
TESTS = [
    {
        "query": "show me red sofas",
        "expect_filters": {"product_type": "sofa", "color": "red"},
        "expect_keyword_in": ["red"],
        "expect_combo": False,
    },
    {
        "query": "costliest beds",
        "expect_filters": {"product_type": "bed"},
        "expect_keyword_in": [],
        "expect_combo": False,
    },
    {
        "query": "wooden coffee table under 10000",
        "expect_filters": {"product_type": "table", "sub_type": "coffee table"},
        "expect_keyword_in": ["wood"],
        "expect_combo": False,
    },
    {
        "query": "study room lighting options",
        "expect_filters": {"product_type": "lighting", "room_type": "study"},
        "expect_keyword_in": [],
        "expect_combo": False,
    },
    {
        "query": "leather recliner",
        "expect_filters": {"product_type": "sofa", "material": "leather", "sub_type": "recliner"},
        "expect_keyword_in": ["leather"],
        "expect_combo": False,
    },
    {
        "query": "I have 50K budget, I want a sofa and a mirror",
        "expect_filters": {},
        "expect_keyword_in": [],
        "expect_combo": True,
        "expect_combo_types": ["sofa", "decor"],
    },
    {
        "query": "furnish my study under 1 lakh - need a desk, chair, and lamp",
        "expect_filters": {},
        "expect_keyword_in": [],
        "expect_combo": True,
        "expect_combo_types": ["table", "chair", "lighting"],
    },
    {
        "query": "cheapest black office chair",
        "expect_filters": {"product_type": "chair", "color": "black", "sub_type": "office chair"},
        "expect_keyword_in": ["black"],
        "expect_combo": False,
    },
    {
        "query": "3 seater velvet sofa under 30000",
        "expect_filters": {"product_type": "sofa", "material": "velvet", "seating": "3-seater"},
        "expect_keyword_in": ["velvet"],
        "expect_combo": False,
    },
    {
        "query": "LED ceiling light for bedroom",
        "expect_filters": {"product_type": "lighting", "room_type": "bedroom"},
        "expect_keyword_in": ["led"],
        "expect_combo": False,
    },
]

print(f"Model: {GEMINI_MODEL}")
print(f"Testing {len(TESTS)} queries against live Gemini API...")
print("=" * 80)

passed = 0
failed = 0

for i, test in enumerate(TESTS, 1):
    query = test["query"]
    print(f"\n[{i}/{len(TESTS)}] Query: \"{query}\"")

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=query)])],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                response_mime_type="application/json",
            ),
        )
        raw = response.text or ""
        parsed = _parse_agent_response(raw)

        # ── Check 1: Valid JSON with required keys ──
        required_keys = ["filters", "response_text", "show_products"]
        missing = [k for k in required_keys if k not in parsed]
        if missing:
            print(f"  FAIL: Missing keys: {missing}")
            print(f"  Raw response (first 300 chars): {raw[:300]}")
            failed += 1
            continue

        filters = parsed.get("filters", {})
        resp_text = parsed.get("response_text", "")
        is_combo = parsed.get("is_combo", False)
        combo_products = parsed.get("combo_products", [])
        total_budget = parsed.get("total_budget")

        errors = []

        # ── Check 2: Expected filters present ──
        for key, expected_val in test["expect_filters"].items():
            actual = filters.get(key)
            if actual is None:
                errors.append(f"Missing filter '{key}' (expected '{expected_val}')")
            elif isinstance(expected_val, str) and expected_val.lower() not in str(actual).lower():
                errors.append(f"Filter '{key}': got '{actual}', expected contains '{expected_val}'")

        # ── Check 3: Keywords in filters ──
        kw = str(filters.get("keyword", "")).lower()
        mat = str(filters.get("material", "")).lower()
        color = str(filters.get("color", "")).lower()
        for expected_kw in test["expect_keyword_in"]:
            if expected_kw not in kw and expected_kw not in mat and expected_kw not in color:
                errors.append(f"Expected keyword/material/color containing '{expected_kw}', got keyword='{kw}', material='{mat}', color='{color}'")

        # ── Check 4: Response text quality ──
        if not resp_text or len(resp_text) < 10:
            errors.append(f"Response text too short or empty: '{resp_text[:50]}'")

        # ── Check 5: Combo detection ──
        if test["expect_combo"]:
            if not is_combo:
                errors.append("Expected is_combo=true, got false")
            if not combo_products:
                errors.append("Expected combo_products to be non-empty")
            else:
                combo_types = [cp.get("product_type") for cp in combo_products]
                for et in test.get("expect_combo_types", []):
                    if et not in combo_types:
                        errors.append(f"Missing combo type '{et}' in {combo_types}")
            if total_budget is None or total_budget <= 0:
                errors.append(f"Expected total_budget > 0, got {total_budget}")
        else:
            if is_combo:
                errors.append("Expected is_combo=false, got true")

        # ── Print results ──
        if errors:
            failed += 1
            print(f"  FAIL ({len(errors)} issues):")
            for e in errors:
                print(f"    - {e}")
            print(f"  Filters returned: {json.dumps(filters, indent=2)}")
            if is_combo:
                print(f"  Combo: is_combo={is_combo}, combo_products={combo_products}, total_budget={total_budget}")
            print(f"  Response text: {resp_text[:120]}...")
        else:
            passed += 1
            print(f"  PASS")
            print(f"  Filters: {json.dumps(filters)}")
            if is_combo:
                print(f"  Combo: types={[cp.get('product_type') for cp in combo_products]}, budget={total_budget}")
            print(f"  Response: {resp_text[:100]}...")

    except Exception as e:
        failed += 1
        print(f"  ERROR: {e}")

    # Rate limit protection
    time.sleep(1)

print(f"\n{'=' * 80}")
print(f"TOTAL: {len(TESTS)} | PASSED: {passed} | FAILED: {failed}")
if failed == 0:
    print("ALL LIVE TESTS PASSED!")
else:
    print(f"{failed} TEST(S) FAILED — Gemini response quality needs improvement")
print("=" * 80)
