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
GEMINI_MODEL = "gemini-2.0-flash"

# ──────────────────────────────────────────────
# Data - Managed via Azure SQL (DB source of truth)
# ──────────────────────────────────────────────
# Legacy Excel paths removed.

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
    "source",          # amazon.in / flipkart.com / ikea.com
    "scraped_date",    # when data was scraped
    "color",           # from IKEA
    "material",        # from IKEA
    "rating",          # from Amazon/Flipkart
]

# ──────────────────────────────────────────────
# Agent Defaults
# ──────────────────────────────────────────────
MAX_RESULTS_PER_QUERY = 5           # Products to show per response
MAX_CONTEXT_MESSAGES = 50           # Max messages kept in context window
TEMPERATURE = 0.7                   # Gemini temperature
TOP_P = 0.95                        # Gemini top-p

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
# Streamlit UI Settings
# ──────────────────────────────────────────────
APP_TITLE = "A2S – AI Interior Design Assistant"
APP_ICON = "🏠"
APP_DESCRIPTION = "Your smart interior design product advisor. Ask me about furniture, lighting, decor — I'll find the perfect products for your room, budget, and style."
