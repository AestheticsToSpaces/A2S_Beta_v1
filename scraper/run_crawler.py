"""
Main Crawler Runner.

Runs all scrapers (IKEA, Amazon, Flipkart), merges results,
cleans the data, and exports to Excel.

Usage:
    python -m scraper.run_crawler
    python -m scraper.run_crawler --sites ikea amazon
    python -m scraper.run_crawler --sites flipkart --max 20

Output:
    scraped_products_YYYYMMDD_HHMMSS.xlsx  (in project root)
"""

import argparse
import re
import sys
import os
from datetime import datetime

import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.base import logger
from scraper.affiliate import convert_existing_urls


def run_scraper(sites: list[str], max_per_category: int = 30) -> pd.DataFrame:
    """
    Run selected scrapers and return combined DataFrame.

    Args:
        sites: List of site names to scrape ("ikea", "amazon", "flipkart").
        max_per_category: Max products per category per site.

    Returns:
        Combined and cleaned DataFrame.
    """
    all_products = []

    if "ikea" in sites:
        from scraper.ikea_scraper import scrape_ikea
        products = scrape_ikea(max_per_category=max_per_category)
        all_products.extend(products)
        logger.info(f"IKEA: {len(products)} products")

    if "amazon" in sites:
        from scraper.amazon_scraper import scrape_amazon
        products = scrape_amazon(max_per_category=max_per_category)
        all_products.extend(products)
        logger.info(f"Amazon: {len(products)} products")

    if "flipkart" in sites:
        from scraper.flipkart_scraper import scrape_flipkart
        products = scrape_flipkart(max_per_category=max_per_category)
        all_products.extend(products)
        logger.info(f"Flipkart: {len(products)} products")

    if not all_products:
        logger.warning("No products scraped from any site!")
        return pd.DataFrame()

    # ── Ensure affiliate links (safety net for any that slipped through) ──
    all_products = convert_existing_urls(all_products)

    # ── Build DataFrame ──
    df = pd.DataFrame(all_products)

    # ── Clean ──
    df = _clean_dataframe(df)

    logger.info(f"Total after cleaning: {len(df)} products")
    return df


def _parse_dimensions(dim_str: str) -> dict:
    """Parse dimension string into W x D x H."""
    result = {"width_cm": None, "depth_cm": None, "height_cm": None}
    if not dim_str or pd.isna(dim_str) or dim_str == "":
        return result
    dim_str = str(dim_str).lower().replace("cm", "").strip()
    numbers = re.findall(r"(\d+(?:\.\d+)?)", dim_str)
    if len(numbers) >= 3:
        result["width_cm"] = float(numbers[0])
        result["depth_cm"] = float(numbers[1])
        result["height_cm"] = float(numbers[2])
    elif len(numbers) == 2:
        result["width_cm"] = float(numbers[0])
        result["depth_cm"] = float(numbers[1])
    elif len(numbers) == 1:
        result["width_cm"] = float(numbers[0])
    return result


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich the scraped DataFrame."""

    # Drop rows with no name or price
    df = df.dropna(subset=["product_name"])
    df = df[df["price_value"].notna() & (df["price_value"] >= 100)]

    # Remove duplicates by product_id
    df = df.drop_duplicates(subset=["product_id"], keep="first")

    # Remove duplicates by product_name + price (catch near-dupes)
    df = df.drop_duplicates(subset=["product_name", "price_value"], keep="first")

    # Clean product names
    df["product_name"] = df["product_name"].apply(lambda x: re.sub(r"\s+", " ", str(x)).strip()[:200])

    # Clean brand
    df["brand"] = df["brand"].fillna("Unknown").apply(
        lambda x: "Unknown" if not x or len(str(x)) > 50 else str(x).strip()
    )

    # Parse dimensions
    dim_parsed = df["dimensions"].apply(_parse_dimensions).apply(pd.Series)
    df["width_cm"] = dim_parsed["width_cm"]
    df["depth_cm"] = dim_parsed["depth_cm"]
    df["height_cm"] = dim_parsed["height_cm"]

    # Add metadata
    df["price_currency"] = "INR"
    df["scraped_date"] = datetime.now().strftime("%Y-%m-%d")

    # Sort by source then price
    df = df.sort_values(["source", "product_type", "price_value"]).reset_index(drop=True)

    return df


def export_to_excel(df: pd.DataFrame, output_dir: str = ".") -> str:
    """Export DataFrame to Excel file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scraped_products_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)

    # Select and order columns for export
    export_cols = [
        "product_id", "product_name", "brand", "price_value", "price_currency",
        "product_type", "dimensions", "width_cm", "depth_cm", "height_cm",
        "image_url", "affiliate_url", "source_url", "source", "scraped_date",
    ]

    # Only include columns that exist
    cols = [c for c in export_cols if c in df.columns]
    df[cols].to_excel(filepath, index=False, engine="openpyxl")

    logger.info(f"Exported {len(df)} products to {filepath}")
    return filepath


def print_summary(df: pd.DataFrame) -> None:
    """Print a human-readable summary of scraped data."""
    print("\n" + "=" * 60)
    print("  SCRAPING RESULTS SUMMARY")
    print("=" * 60)
    print(f"  Total products:  {len(df)}")

    if df.empty:
        print("  No data scraped.")
        return

    print(f"\n  By source:")
    for src, count in df["source"].value_counts().items():
        print(f"    {src:20s} {count:4d} products")

    print(f"\n  By product type:")
    for ptype, count in df["product_type"].value_counts().items():
        print(f"    {ptype:20s} {count:4d} products")

    print(f"\n  Price range: ₹{df['price_value'].min():,.0f} – ₹{df['price_value'].max():,.0f}")
    print(f"  Avg price:   ₹{df['price_value'].mean():,.0f}")

    brands = df[df["brand"] != "Unknown"]["brand"].nunique()
    print(f"  Known brands: {brands}")

    has_dims = df["width_cm"].notna().sum()
    print(f"  With dimensions: {has_dims}/{len(df)}")

    has_images = df["image_url"].fillna("").str.startswith("http").sum()
    print(f"  With images: {has_images}/{len(df)}")

    if "affiliate_url" in df.columns:
        has_aff = df["affiliate_url"].fillna("").str.len().gt(0).sum()
        has_tag = df["affiliate_url"].fillna("").str.contains("tag=|affid=|utm_source=", regex=True).sum()
        print(f"  With affiliate links: {has_tag}/{len(df)}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="A2S Product Scraper")
    parser.add_argument(
        "--sites",
        nargs="+",
        choices=["ikea", "amazon", "flipkart"],
        default=["ikea", "amazon", "flipkart"],
        help="Sites to scrape (default: all)",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=30,
        help="Max products per category per site (default: 30)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=".",
        help="Output directory (default: current)",
    )

    args = parser.parse_args()

    print(f"\n🕷️  A2S Product Crawler")
    print(f"   Sites: {', '.join(args.sites)}")
    print(f"   Max per category: {args.max}\n")

    df = run_scraper(sites=args.sites, max_per_category=args.max)

    if not df.empty:
        filepath = export_to_excel(df, output_dir=args.output)
        print_summary(df)
        print(f"📁 Data saved to: {filepath}")
    else:
        print("❌ No products were scraped. Sites may be blocking requests.")
        print("   Try again later or with different settings.")


if __name__ == "__main__":
    main()
