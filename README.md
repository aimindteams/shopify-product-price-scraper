# Shopify Product & Price Scraper and Price Monitor (Python)

Get every product from any **Shopify store** with prices, compare-at prices, discounts, stock, variants and images, or **monitor competitors** and receive only what changed: **price drops, price increases, restocks, sell-outs, new and removed products**.

This repo is a small, free Python client for the [Shopify Store Scraper & Price Monitor](https://apify.com/aimindteams/shopify-catalog-price-monitor) on Apify. The Actor reads each store's public catalog in the cloud; this script runs it and saves a CSV.

## What you get

- **Every product:** title, vendor, type, tags, price range, compare-at price, discount %, availability, variant count, options, image and URL
- **Variant level** (optional): one row per size or color with SKU, price and stock
- **Change tracking:** a baseline on the first run, then only the products whose price or stock changed, with old and new values
- **Filters:** collections, keywords, vendors, product types, in stock only, on sale only, price range

## Quick start (no code)

Open the [Actor on the Apify Store](https://apify.com/aimindteams/shopify-catalog-price-monitor), add store domains and press **Start**. Download the results as CSV, Excel or JSON, or schedule it daily with change tracking on.

## Quick start (Python)

```bash
git clone https://github.com/aimindteams/shopify-product-price-scraper
cd shopify-product-price-scraper
pip install -r requirements.txt
export APIFY_TOKEN=your_token   # free account: https://console.apify.com/settings/integrations

# Everything on sale at one store
python watch_prices.py allbirds.com --on-sale-only --csv sale.csv

# One collection, one row per size or color
python watch_prices.py example-store.com --collections sale --variants

# Competitor monitoring: run it daily; after the first (baseline) run you only get changes
python watch_prices.py competitor-one.com competitor-two.com --track --csv changes.csv
```

On Windows PowerShell use `$env:APIFY_TOKEN="your_token"`.

## What the CSV looks like

Illustrative example (invented store):

| store | title | price_min | compare_at_price_max | max_discount_pct | available | change_type | change_detail |
|---|---|---|---|---|---|---|---|
| example-store.com | Merino Runner - Navy | 89.0 | 120.0 | 25.8 | True | price_drop | price_drop 9 110.0 -> 89.0 |
| example-store.com | Trail Sock 3-Pack | 24.0 | | | False | sold_out | sold_out |

## Use cases

- **Competitor price monitoring** for Shopify brands and resellers
- **Deal and drop alerts** for affiliate sites and deal newsletters
- **Assortment research:** see a competitor's full catalog, vendors and price bands
- **MAP compliance:** watch retailers for prices below the minimum advertised price

## Use it from AI agents (MCP)

```
https://mcp.apify.com?tools=aimindteams/shopify-catalog-price-monitor
```

## Pricing

Pay per product delivered. With change tracking, unchanged products are skipped after the baseline run, so a daily schedule only pays for what changed. Current prices are on the [Pricing tab](https://apify.com/aimindteams/shopify-catalog-price-monitor/pricing). `--max-cost` (default $1) caps any single run.

## FAQ

**How do I know a store runs on Shopify?** Try it: non-Shopify stores are reported in the run log. Custom domains work as well as .myshopify.com addresses.

**Where is the change-tracking baseline kept?** In a Key-Value Store (SHOPIFY-CATALOG-SNAPSHOTS) in your own Apify account, one snapshot per store and filter set.

## License

The code in this repo is MIT licensed. The Actor itself is a hosted service on Apify.
