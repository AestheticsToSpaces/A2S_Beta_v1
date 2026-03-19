"""
Product Card Formatters – Compact Edition.

Formats product data into compact, space-efficient Streamlit display cards
with small thumbnails, prices, dimensions, and affiliate links.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd


def display_product_cards(products: list[dict]) -> None:
    """
    Render product cards in a 3-column compact grid.
    Each card has a small thumbnail, name, price, source badge, and buy link.
    """
    if not products:
        st.info("No products to display.")
        return

    for i in range(0, len(products), 3):
        cols = st.columns(3, gap="small")
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(products):
                break
            product = products[idx]
            with col:
                _render_card(product)


def _render_card(product: dict) -> None:
    """Render a single compact product card."""
    with st.container(border=True):
        # ── Image (small thumbnail) ──
        image_url = product.get("image_url", "")
        if image_url and str(image_url).startswith("http"):
            try:
                st.markdown(
                    f'<div style="width:100%; height:140px; overflow:hidden; border-radius:8px; '
                    f'background:#111; display:flex; align-items:center; justify-content:center;">'
                    f'<img src="{image_url}" style="max-width:100%; max-height:140px; object-fit:contain;" /></div>',
                    unsafe_allow_html=True,
                )
            except Exception:
                pass

        # ── Source badge (inline, top) ──
        source = product.get("source", "")
        source_html = ""
        if source and str(source) not in ("None", "nan", "original_data", ""):
            src_colors = {
                "amazon.in": ("#ff9900", "#232f3e"),
                "flipkart.com": ("#2874f0", "#fff"),
                "ikea.com": ("#0058a3", "#ffdb00"),
            }
            bg, fg = src_colors.get(source, ("#6366f1", "#fff"))
            src_label = source.replace(".com", "").replace(".in", "").upper()
            source_html = (
                f'<span style="background:{bg}; color:{fg}; padding:1px 6px; '
                f'border-radius:4px; font-size:0.6rem; font-weight:700; '
                f'letter-spacing:0.4px; vertical-align:middle;">{src_label}</span> '
            )

        # ── Name (truncated) + Brand ──
        name = product.get("product_name", "Unknown Product")
        brand = product.get("brand", "")
        display_name = str(name).title()[:65]
        if len(str(name)) > 65:
            display_name += "…"

        st.markdown(
            f'<p style="font-size:0.82rem; font-weight:600; color:#e2e8f0; '
            f'margin:0.4rem 0 0.15rem 0; line-height:1.3;">{source_html}{display_name}</p>',
            unsafe_allow_html=True,
        )

        if brand and str(brand) not in ("Unknown", "None", "nan", ""):
            st.markdown(
                f'<span style="color:#8b5cf6; font-size:0.72rem; font-weight:600;">{brand}</span>',
                unsafe_allow_html=True,
            )

        # ── Price ──
        price = product.get("price_value")
        if price and not pd.isna(price):
            st.markdown(
                f'<span style="font-size:1.2rem; font-weight:800; color:#a78bfa;">₹{float(price):,.0f}</span>',
                unsafe_allow_html=True,
            )

        # ── Dimensions (compact) ──
        width = product.get("width_cm")
        depth = product.get("depth_cm")
        height = product.get("height_cm")
        dims = []
        if width and not pd.isna(width):
            dims.append(f"{int(width)}")
        if depth and not pd.isna(depth):
            dims.append(f"{int(depth)}")
        if height and not pd.isna(height):
            dims.append(f"{int(height)}")

        raw_dim = product.get("dimensions")
        if dims:
            st.caption(f"📐 {' × '.join(dims)} cm")
        elif raw_dim and str(raw_dim) not in ("None", "nan", ""):
            st.caption(f"📐 {raw_dim}")

        # ── Tags (compact row) ──
        tags = []
        for field, icon in [("product_type", "🪑"), ("style", "🎨")]:
            val = product.get(field)
            if val and str(val) not in ("None", "nan"):
                tags.append(f'{icon} {str(val).replace("_"," ").title()}')

        if tags:
            tags_str = " · ".join(tags)
            st.markdown(
                f'<span style="font-size:0.65rem; color:#9ca3af;">{tags_str}</span>',
                unsafe_allow_html=True,
            )

        # ── Buy Link ──
        url = product.get("affiliate_url") or product.get("source_url")
        if url and str(url).startswith("http"):
            st.link_button("🛒 Buy", str(url), use_container_width=True)


def display_combo_cards(combo_result: dict) -> None:
    """
    Display grouped product cards for a combo/multi-product request.

    Shows each product type as a section with a header, then a total cost bar.
    """
    groups = combo_result.get("groups", [])
    total_budget = combo_result.get("total_budget", 0)
    total_cost = combo_result.get("total_cost", 0)
    within_budget = combo_result.get("within_budget", True)

    if not groups:
        st.info("No combo products to display.")
        return

    for g in groups:
        label = g.get("label", "Products")
        products = g.get("products", [])
        budget_slice = g.get("budget_slice", 0)

        # Section header
        st.markdown(
            f'<div style="background:linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2)); '
            f'border:1px solid rgba(139,92,246,0.3); border-radius:10px; padding:0.5rem 1rem; '
            f'margin:0.8rem 0 0.4rem 0;">'
            f'<span style="font-size:1.1rem; font-weight:700; color:#c4b5fd;">'
            f'{label}</span>'
            f'<span style="float:right; font-size:0.8rem; color:#9ca3af;">'
            f'Budget allocation: ₹{budget_slice:,.0f}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if products:
            for i in range(0, len(products), 3):
                cols = st.columns(3, gap="small")
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx >= len(products):
                        break
                    with col:
                        _render_card(products[idx])
        else:
            st.caption(f"No {label.lower()} found matching your criteria.")

    # ── Total Cost Summary Bar ──
    if within_budget:
        bar_color = "rgba(34,197,94,0.3)"
        border_color = "rgba(34,197,94,0.5)"
        text_color = "#4ade80"
        status = f"Within your ₹{total_budget:,.0f} budget"
        icon = "✅"
    else:
        bar_color = "rgba(239,68,68,0.2)"
        border_color = "rgba(239,68,68,0.4)"
        text_color = "#f87171"
        status = f"Exceeds ₹{total_budget:,.0f} budget by ₹{total_cost - total_budget:,.0f}"
        icon = "⚠️"

    savings = total_budget - total_cost if within_budget else 0

    st.markdown(
        f'<div style="background:{bar_color}; border:1px solid {border_color}; '
        f'border-radius:12px; padding:0.8rem 1.2rem; margin-top:1rem; '
        f'display:flex; justify-content:space-between; align-items:center;">'
        f'<div>'
        f'<span style="font-size:1.3rem; font-weight:800; color:{text_color};">'
        f'{icon} Combo Total: ₹{total_cost:,.0f}</span><br/>'
        f'<span style="font-size:0.8rem; color:#9ca3af;">'
        f'{status}'
        f'{"  •  You save ₹" + f"{savings:,.0f}" if savings > 0 else ""}'
        f'</span>'
        f'</div>'
        f'<div style="text-align:right;">'
        f'<span style="font-size:0.75rem; color:#9ca3af;">Budget</span><br/>'
        f'<span style="font-size:1.1rem; font-weight:700; color:#c4b5fd;">₹{total_budget:,.0f}</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def format_product_summary(products: list[dict]) -> str:
    """Text summary of products for conversation history."""
    if not products:
        return ""

    lines = [f"\n**Showing {len(products)} product(s):**\n"]
    for i, p in enumerate(products, 1):
        name = p.get("product_name", "Unknown")
        price = p.get("price_value", "N/A")
        brand = p.get("brand", "")
        price_str = f"₹{float(price):,.0f}" if price and not pd.isna(price) else "N/A"
        line = f"{i}. **{str(name).title()[:60]}** — {price_str}"
        if brand and str(brand) not in ("Unknown", "None", "nan", ""):
            line += f" ({brand})"
        lines.append(line)

    return "\n".join(lines)
