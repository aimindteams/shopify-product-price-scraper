"""Scrape Shopify stores for products, prices, discounts and stock, or watch them for changes.

Runs the "Shopify Store Scraper & Price Monitor" Actor on Apify and saves one CSV row per product.

    export APIFY_TOKEN=...   # free account: https://console.apify.com/settings/integrations
    python watch_prices.py allbirds.com --on-sale-only --csv sale.csv
    python watch_prices.py competitor-one.com competitor-two.com --track   # first run saves a baseline
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter

from apify_client import ApifyClient

ACTOR_ID = "aimindteams/shopify-catalog-price-monitor"

COLUMNS = [
    "store", "title", "vendor", "product_type", "price_min", "price_max", "compare_at_price_max",
    "max_discount_pct", "on_sale", "available", "variants_count", "change_type", "change_detail", "url",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scrape or monitor Shopify stores.")
    p.add_argument("stores", nargs="+", help="Store domains or URLs (custom domains and .myshopify.com both work)")
    p.add_argument("--collections", nargs="*", default=[], help="Only these collections (handles or URLs)")
    p.add_argument("--keywords", nargs="*", default=[], help="Keep products whose title, tags, vendor or type match")
    p.add_argument("--vendors", nargs="*", default=[], help="Keep products from these brands")
    p.add_argument("--on-sale-only", action="store_true", help="Only discounted products")
    p.add_argument("--in-stock-only", action="store_true", help="Only products you can buy right now")
    p.add_argument("--max-per-store", type=int, default=1000, help="Products per store after filters (default 1000)")
    p.add_argument("--variants", action="store_true", help="One row per variant (size, color) instead of per product")
    p.add_argument("--track", action="store_true", help="Monitor changes: first run saves a baseline, later runs return only changes")
    p.add_argument("--csv", default="products.csv", help="CSV output path (default products.csv)")
    p.add_argument("--json", help="Also save the full results as JSON")
    p.add_argument("--max-cost", type=float, default=1.0, help="Stop the run before it costs more than this (USD)")
    return p.parse_args()


def describe_changes(item: dict) -> str:
    if item.get("variant_id") and item.get("old_price") is not None:  # variant rows
        return f"{item.get('change_type')} {item['old_price']} -> {item.get('price')}"
    parts = []
    for change in item.get("changes") or []:
        kind = change.get("type", "change")
        if "old_price" in change and "new_price" in change:
            label = change.get("variant_title") or ""
            parts.append(f"{kind} {label} {change['old_price']} -> {change['new_price']}".replace("  ", " "))
        else:
            parts.append(kind)
    return "; ".join(parts[:5])


def row(item: dict) -> dict:
    title = item.get("title") or " / ".join(x for x in (item.get("product_title"), item.get("variant_title")) if x)
    return {
        "store": item.get("store"),
        "title": title,
        "vendor": item.get("vendor"),
        "product_type": item.get("product_type"),
        "price_min": item.get("price_min", item.get("price")),
        "price_max": item.get("price_max", item.get("price")),
        "compare_at_price_max": item.get("compare_at_price_max", item.get("compare_at_price")),
        "max_discount_pct": item.get("max_discount_pct", item.get("discount_pct")),
        "on_sale": item.get("on_sale"),
        "available": item.get("available"),
        "variants_count": item.get("variants_count"),
        "change_type": item.get("change_type"),
        "change_detail": describe_changes(item),
        "url": item.get("url"),
    }


def main() -> int:
    args = parse_args()
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN first. Get one free at https://console.apify.com/settings/integrations")

    run_input = {
        "stores": args.stores,
        "collections": args.collections,
        "keywords": args.keywords,
        "vendors": args.vendors,
        "onSaleOnly": args.on_sale_only,
        "onlyAvailable": args.in_stock_only,
        "maxProductsPerStore": args.max_per_store,
        "outputLevel": "variant" if args.variants else "product",
        "trackChanges": args.track,
        "onlyChanges": True,
    }
    client = ApifyClient(token)
    print(f"Reading {len(args.stores)} stores with {ACTOR_ID} ...")
    run = client.actor(ACTOR_ID).call(run_input=run_input, max_total_charge_usd=args.max_cost)
    if not run or run.get("status") != "SUCCEEDED":
        sys.exit(f"Run did not finish: {run and run.get('status')}")

    items = list(client.dataset(run["defaultDatasetId"]).iterate_items(clean=True))
    with open(args.csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(row(i) for i in items)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(items, handle, indent=2)

    print(f"Saved {len(items)} rows to {args.csv}")
    if args.track:
        changes = Counter(i.get("change_type") for i in items if i.get("change_type"))
        if changes:
            for kind, count in changes.most_common():
                print(f"  {count:>5}  {kind}")
        else:
            print("  No changes since the last run (or this was the baseline run).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
