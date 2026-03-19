"""
Context Manager for the AI Agent.

Manages the full conversation history and accumulated search filters
in Streamlit session state so that context is NEVER lost across
chat turns.

Architecture:
    - messages[]       : Full chat history (role + content)
    - active_filters{} : Currently accumulated search filters
    - search_history[] : Past search filter snapshots
"""

from __future__ import annotations
from typing import Any

import streamlit as st


def init_context() -> None:
    """Initialize all session-state keys if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "active_filters" not in st.session_state:
        st.session_state.active_filters = {}

    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    if "last_products" not in st.session_state:
        st.session_state.last_products = None


def add_message(role: str, content: str, products: Any = None, combo: Any = None) -> None:
    """
    Append a message to the conversation history.

    Args:
        role:     "user" or "assistant"
        content:  The text content of the message.
        products: Optional list of product dicts shown with this message.
        combo:    Optional combo result dict for grouped display.
    """
    msg = {"role": role, "content": content}
    if products is not None:
        msg["products"] = products
    if combo is not None:
        msg["combo"] = combo
    st.session_state.messages.append(msg)


def get_messages() -> list[dict]:
    """Return the full conversation history."""
    return st.session_state.messages


def get_messages_for_llm() -> list[dict]:
    """
    Return messages formatted for the Gemini API.

    Maps 'assistant' → 'model' for Gemini's expected format,
    and strips product data (only sends text).
    """
    formatted = []
    for msg in st.session_state.messages:
        role = "model" if msg["role"] == "assistant" else "user"
        formatted.append({
            "role": role,
            "parts": [{"text": msg["content"]}],
        })
    return formatted


def update_filters(new_filters: dict) -> None:
    """
    Merge new filters into the active filter set.

    Smart merge rules:
    - None values in new_filters are ignored (don't clear existing).
    - Explicit values overwrite existing ones.
    - Budget conflict resolution:
        * If new budget_max < existing budget_min → clear budget_min
        * If new budget_min > existing budget_max → clear budget_max
    - Dimension conflict resolution (same logic).
    - Use reset_filters() to clear all.
    """
    current = st.session_state.active_filters

    for key, value in new_filters.items():
        if value is not None:
            current[key] = value

    # ── Fix contradictory budget ──
    bmin = current.get("budget_min")
    bmax = current.get("budget_max")
    if bmin is not None and bmax is not None:
        if float(bmin) > float(bmax):
            # Whichever was set most recently wins — the new one
            if "budget_max" in new_filters and new_filters["budget_max"] is not None:
                current.pop("budget_min", None)
            elif "budget_min" in new_filters and new_filters["budget_min"] is not None:
                current.pop("budget_max", None)
            else:
                # Fallback: keep budget_max, drop budget_min
                current.pop("budget_min", None)

    # ── Fix contradictory dimensions ──
    dim_pairs = [("min_width", "max_width"), ("min_depth", "max_depth"), ("min_height", "max_height")]
    for dmin, dmax in dim_pairs:
        vmin = current.get(dmin)
        vmax = current.get(dmax)
        if vmin is not None and vmax is not None and float(vmin) > float(vmax):
            if dmax in new_filters and new_filters[dmax] is not None:
                current.pop(dmin, None)
            else:
                current.pop(dmax, None)

    st.session_state.active_filters = current


def get_active_filters() -> dict:
    """Return the current accumulated filters."""
    return st.session_state.active_filters.copy()


def reset_filters() -> None:
    """Clear all active filters (user said 'start over')."""
    # Save to history before clearing
    if st.session_state.active_filters:
        st.session_state.search_history.append(
            st.session_state.active_filters.copy()
        )
    st.session_state.active_filters = {}
    st.session_state.last_products = None


def set_last_products(products: list[dict] | None) -> None:
    """Store the last set of products shown to the user."""
    st.session_state.last_products = products


def get_last_products() -> list[dict] | None:
    """Return the last set of products shown."""
    return st.session_state.last_products


def get_context_summary() -> str:
    """
    Build a short text summary of current context for debugging / display.
    """
    filters = st.session_state.active_filters
    if not filters:
        return "No active filters — start by telling me what you're looking for!"

    parts = []
    if filters.get("room_type"):
        parts.append(f"Room: {filters['room_type']}")
    if filters.get("style"):
        parts.append(f"Style: {filters['style']}")
    if filters.get("product_type"):
        parts.append(f"Product: {filters['product_type']}")
    if filters.get("color_palette"):
        parts.append(f"Color: {filters['color_palette']}")
    if filters.get("budget_max"):
        parts.append(f"Budget: up to ₹{filters['budget_max']:,.0f}")
    elif filters.get("budget_min"):
        parts.append(f"Budget: from ₹{filters['budget_min']:,.0f}")
    if filters.get("brand"):
        parts.append(f"Brand: {filters['brand']}")
    if filters.get("keyword"):
        parts.append(f"Search: {filters['keyword']}")

    return " · ".join(parts) if parts else "Filters active"
