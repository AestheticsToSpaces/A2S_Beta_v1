"""
Configuration for A2S - AI Interior Design Product Recommendation Agent.

This module centralizes all configuration: API keys, file paths, model
settings, and application defaults.
"""

import os

# ──────────────────────────────────────────────
# Google Gemini API
# ──────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY",
    "",
)
GEMINI_MODEL = "gemini-2.5-pro"

# ──────────────────────────────────────────────
# Data File Paths (relative to project root)
# ──────────────────────────────────────────────
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILES = [
    os.path.join(DATA_DIR, "design_products_data (1).xlsx"),
    os.path.join(DATA_DIR, "design_products_with_dimension.xlsx"),
]

# Scraped data file (auto-detected: most recent scraped_products_*.xlsx)
import glob as _glob
_scraped = sorted(_glob.glob(os.path.join(DATA_DIR, "scraped_products_*.xlsx")))
SCRAPED_DATA_FILE = _scraped[-1] if _scraped else None

# ──────────────────────────────────────────────
# Product Catalog Settings
# ──────────────────────────────────────────────
# Columns to keep after merging (canonical names)
CANONICAL_COLUMNS = [
    "design_id",
    "room_type",
    "style",
    "budget_min",
    "budget_max",
    "color_palette",
    "image_url",
    "product_id",
    "product_type",
    "product_name",
    "brand",
    "price_currency",
    "price_value",
    "dimensions",
    "width_cm",
    "depth_cm",
    "height_cm",
    "affiliate_url",
    "paint_brand",
    "paint_code",
    "decor_type",
    "quantity_in_design",
    "role_in_design",
    "source_url",
    "source",           # amazon.in / flipkart.com / ikea.com
    "scraped_date",     # when data was scraped
    "rating",           # from Amazon/Flipkart
    # ── Enriched attributes (extracted from product names) ──
    "color",            # red, blue, brown, white, etc.
    "material",         # wood, metal, fabric, leather, etc.
    "sub_type",         # coffee table, floor lamp, 3-seater sofa, etc.
    "seating",          # 1-seater, 2-seater, 3-seater, etc.
    "price_tier",       # budget, mid-range, premium, luxury
    "size_category",    # small, medium, large
    "features",         # foldable, adjustable, led, smart, etc.
]

# ──────────────────────────────────────────────
# Agent Defaults
# ──────────────────────────────────────────────
MAX_RESULTS_PER_QUERY = 9           # Products to show per response (3 columns x 3 rows)
MAX_CONTEXT_MESSAGES = 50           # Max messages kept in context window
TEMPERATURE = 0.3                   # Lower = more consistent, less creative
TOP_P = 0.9                         # Tighter nucleus for reliable filter extraction

# ──────────────────────────────────────────────
# Known domain values (used for entity matching)
# ──────────────────────────────────────────────
ROOM_TYPES = ["bedroom", "living_room", "dining_room", "kids_room", "study"]
STYLES = ["classic", "contemporary", "ethnic", "functional", "minimal", "modern"]
COLOR_PALETTES = ["cool", "dark wood", "light wood", "neutral", "red and beige", "warm", "white", "wood tones"]
PRODUCT_TYPES = ["sofa", "bed", "lighting", "table", "storage", "decor", "chair", "textile", "misc"]
PAINT_BRANDS = ["Asian Paints", "Berger", "Nerolac"]
DECOR_TYPES = ["clock", "curtain", "lamp", "mirror", "vase", "wall art"]
ROLES = ["ambient lighting", "centerpiece", "dining", "floor decor", "main bed", "main seating", "storage"]

# ──────────────────────────────────────────────
# Affiliate Program Configuration
# ──────────────────────────────────────────────
# Amazon Associates — Sign up: https://affiliate-program.amazon.in/
# Your tag looks like: "yourtag-21" (always ends with -21 for India)
AMAZON_AFFILIATE_TAG = os.environ.get("AMAZON_AFFILIATE_TAG", "a2sdesign-21")

# Flipkart Affiliate — Sign up: https://affiliate.flipkart.com/
# Your affiliate ID from the Flipkart Affiliate dashboard
FLIPKART_AFFILIATE_ID = os.environ.get("FLIPKART_AFFILIATE_ID", "a2sdesign")

# IKEA — No direct affiliate program in India.
# Uses redirect tracking. Set a custom tracking param or leave empty.
IKEA_TRACKING_PARAM = os.environ.get("IKEA_TRACKING_PARAM", "utm_source=a2s&utm_medium=affiliate")

# ──────────────────────────────────────────────
# Streamlit UI Settings
# ──────────────────────────────────────────────
APP_TITLE = "A2S – AI Interior Design Assistant"
APP_ICON = "🏠"
APP_DESCRIPTION = "Your smart interior design product advisor. Ask me about furniture, lighting, decor — I'll find the perfect products for your room, budget, and style."
