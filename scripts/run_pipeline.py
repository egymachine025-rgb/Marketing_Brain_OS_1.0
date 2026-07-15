#!/usr/bin/env python3
"""
Run the full Marketing Brain OS pipeline:
    Telegram Messages -> ParserManager -> ProductBuilder -> ProductNormalizer -> DuplicateEngine -> Repository -> Dashboard

Now reads from channel subdirectories: data/raw/telegram/{channel_name}/
"""

import os
import sys
import json
import shutil
import warnings
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from marketing_brain_os.fingerprint_engine import FingerprintEngine, compute_similarity
from marketing_brain_os.duplicate_engine import DuplicateEngine, DuplicateResult
from marketing_brain_os.dashboard_backend import DashboardBackend
from marketing_brain_os.parser_manager import ParserManager as LegacyParserManager
from marketing_brain_os.product_builder import ProductBuilder as LegacyProductBuilder
from marketing_brain_os.normalizer import ProductNormalizer as LegacyProductNormalizer
from src.parsing import ParserManager, ProductBuilder, ProductNormalizer

# Stateless workers — safe to share across the whole pipeline run
_parser_manager = ParserManager()
_product_builder = ProductBuilder()
_normalizer = ProductNormalizer()
_legacy_parser_manager = LegacyParserManager()
_legacy_product_builder = LegacyProductBuilder()
_legacy_normalizer = LegacyProductNormalizer()


def _normalize_channel_name(channel: str | None) -> str | None:
    if not channel:
        return None
    channel_name = str(channel).strip()
    if not channel_name:
        return None
    if not channel_name.startswith("@"):
        channel_name = "@" + channel_name
    return channel_name


def _extract_channel_from_message(raw_msg: dict) -> str | None:
    if not isinstance(raw_msg, dict):
        return None
    channel = raw_msg.get("channel")
    if channel:
        return _normalize_channel_name(channel)

    if "message" in raw_msg:
        chat = raw_msg.get("message", {}).get("chat", {})
    else:
        chat = raw_msg.get("chat", {})

    if isinstance(chat, dict):
        username = chat.get("username")
        title = chat.get("title")
        first_name = chat.get("first_name")
        if username:
            return _normalize_channel_name(username)
        if title:
            return _normalize_channel_name(title)
        if first_name:
            return _normalize_channel_name(first_name)

    return None


def load_telegram_messages(data_dir: str = "data/raw/telegram") -> list:
    """Load all Telegram JSON message files from channel subdirectories."""
    messages = []
    telegram_dir = os.path.join(PROJECT_ROOT, data_dir)

    if not os.path.exists(telegram_dir):
        print(f"[!] Telegram directory not found: {telegram_dir}")
        os.makedirs(telegram_dir, exist_ok=True)
        return messages

    # Walk through channel subdirectories
    for channel_name in sorted(os.listdir(telegram_dir)):
        channel_path = os.path.join(telegram_dir, channel_name)
        if not os.path.isdir(channel_path):
            # Also check flat files (backward compatibility)
            if channel_name.endswith(".json"):
                filepath = os.path.join(telegram_dir, channel_name)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        msg = json.load(f)
                        channel = _extract_channel_from_message(msg)
                        if channel:
                            msg["channel"] = channel
                        messages.append(msg)
                        print(f"      Found 1 messages in channel {channel or channel_name}")
                except Exception as e:
                    print(f"[!] Error reading {filepath}: {e}")
            continue

        # Read messages from channel subdirectory
        channel_messages = []
        normalized_channel = _normalize_channel_name(channel_name)
        for filename in sorted(os.listdir(channel_path)):
            if filename.endswith(".json") and not filename.startswith("_"):
                filepath = os.path.join(channel_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        msg = json.load(f)
                        # Add channel info if missing or empty
                        if not msg.get("channel"):
                            msg["channel"] = normalized_channel
                        messages.append(msg)
                        channel_messages.append(msg)
                except Exception as e:
                    print(f"[!] Error reading {filepath}: {e}")

        print(f"      Found {len(channel_messages)} messages in channel {normalized_channel or channel_name}")

    return messages


def parse_message(raw_msg: dict) -> dict:
    """Parse a raw Telegram message into structured data."""
    # Handle both old format and new format
    if "message" in raw_msg:
        # Old format (from run_telegram_acquisition)
        message = raw_msg.get("message", {})
        from_user = message.get("from", {})
        text = message.get("text", "")
        date_ts = message.get("date", 0)
        return {
            "source": "telegram",
            "source_id": str(raw_msg.get("update_id", "")),
            "message_id": str(message.get("message_id", "")),
            "raw_text": text,
            "channel": raw_msg.get("channel"),
            "sender": {
                "id": str(from_user.get("id", "")),
                "username": from_user.get("username", ""),
                "first_name": from_user.get("first_name", ""),
                "last_name": from_user.get("last_name", ""),
            },
            "timestamp": date_ts,
        }
    else:
        # New format (from telegram_bot.py)
        return {
            "source": "telegram",
            "source_id": str(raw_msg.get("message_id", "")),
            "message_id": str(raw_msg.get("message_id", "")),
            "raw_text": raw_msg.get("text", ""),
            "channel": raw_msg.get("channel"),
            "sender": {
                "id": "",
                "username": "",
                "first_name": "",
                "last_name": "",
            },
            "timestamp": raw_msg.get("date", datetime.now().isoformat()),
        }


def _normalize_timestamp(raw_timestamp) -> str:
    """
    Normalize a raw message timestamp (unix epoch int/float, or an
    already-ISO string) into a consistent ISO-8601 string.

    Pre-existing data quality issue: different raw Telegram message
    formats store "date" as either a unix epoch int or an ISO string.
    DashboardBackend.sort() compares these values directly and raises
    TypeError when the catalog mixes both types. This normalization is
    integration glue in the adapter only — DashboardBackend itself is
    untouched. See report "Blockers".
    """
    if isinstance(raw_timestamp, (int, float)):
        try:
            return datetime.utcfromtimestamp(raw_timestamp).isoformat() + "Z"
        except (OverflowError, OSError, ValueError):
            return datetime.utcnow().isoformat() + "Z"
    if isinstance(raw_timestamp, str) and raw_timestamp:
        return raw_timestamp
    return datetime.utcnow().isoformat() + "Z"


def build_product_from_message(parsed: dict) -> dict:
    """
    Build a product from a parsed Telegram message using the real
    Marketing Brain parsing stack — NOT regex classification:

        ParserManager -> ProductBuilder -> ProductNormalizer

    TASK-K009 (Dashboard Migration): name/category/brand are now stored
    as top-level Product Model fields — DashboardBackend reads them
    directly, not through "listing".

    The "listing" sub-object is kept ONLY as a compatibility mirror for
    DuplicateEngine/FingerprintEngine, which still read
    listing.title/listing.category/listing.price and remain off-limits
    to modify. It is not a second source of truth — title/category here
    are copies of name/category above, not independently derived. Once
    DuplicateEngine/FingerprintEngine are migrated in a future task,
    this mirror can be deleted entirely.
    """
    text = parsed["raw_text"]

    # 1. ParserManager — deterministic, multi-lingual (EN/AR) text parsing
    try:
        raw_product = _parser_manager.parse_message(
            text,
            {
                "message_id": parsed.get("message_id", ""),
                "channel": parsed.get("channel", ""),
                "timestamp": _normalize_timestamp(parsed.get("timestamp")),
            },
        )
        product = _product_builder.build(raw_product)
        # Optional knowledge repository can be passed into normalizer if available.
        normalized_product = _normalizer.normalize(product)

        price_obj = normalized_product["listing"]["price"]
        name = normalized_product["listing"]["title"]
        category = normalized_product["listing"]["category"]
        brand = normalized_product["listing"].get("brand", "Unknown")
    except Exception as exc:
        warnings.warn(
            f"ParserManager pipeline failed: {exc}. Falling back to legacy regex-based pipeline.",
            UserWarning,
        )
        parse_result = _legacy_parser_manager.parse_raw_content(text)
        product = _legacy_product_builder.build_from_parse_result(
            parse_result=parse_result,
            telegram_channel=parsed.get("channel"),
            telegram_message_id=parsed.get("message_id"),
        )
        normalized_product = _legacy_normalizer.normalize_product(product)

        price_obj = {
            "amount": normalized_product.price,
            "currency": normalized_product.currency.value
            if hasattr(normalized_product.currency, "value")
            else str(normalized_product.currency),
        }
        name = normalized_product.name
        category = normalized_product.category
        brand = normalized_product.brand

    return {
        "product_id": f"tg-{parsed['source_id']}",
        "source": {
            "platform": "telegram",
            "channel": parsed.get("channel", ""),
            "message_id": parsed["message_id"],
            "update_id": parsed["source_id"],
        },
        # Product Model fields — top-level, read directly by DashboardBackend.
        "name": normalized_product["listing"]["title"],
        "category": normalized_product["listing"]["category"],
        "brand": normalized_product["listing"].get("brand", "Unknown"),
        # DuplicateEngine/FingerprintEngine compatibility mirror only.
        "listing": {
            "title": normalized_product["listing"]["title"],
            "category": normalized_product["listing"]["category"],
            "description": normalized_product["listing"]["description"],
            "price": price_obj,
            # NOTE: condition is not produced by the ParserManager stack
            # (no ConditionExtractor exists) — see report "Blockers".
            "condition": "Unknown",
        },
        "seller": parsed["sender"],
        "metadata": {
            "acquired_at": _normalize_timestamp(parsed["timestamp"]),
            "parser_version": "2.0.0-parser-manager",
            "language": normalized_product["listing"].get("language", "en"),
            "colors": normalized_product.get("colors", []),
            "features": normalized_product.get("features", []),
            "keywords": normalized_product.get("keywords", []),
            "offer": normalized_product.get("offer", ""),
        },
        "status": "active",
    }


def save_products(products: list[dict], output_dir: str) -> int:
    os.makedirs(output_dir, exist_ok=True)
    saved = 0
    for product in products:
        product_id = product.get("product_id") or f"product-{saved + 1}"
        filename = f"{product_id}.json"
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(product, f, ensure_ascii=False, indent=2)
            saved += 1
        except Exception as exc:
            print(f"[!] Failed to save product {product_id}: {exc}")
    return saved


def run_pipeline(
    telegram_dir: str = "data/raw/telegram",
    products_dir: str = "data/products",
    clean: bool = False,
) -> dict:
    """
    Run the full pipeline.

    Returns:
        dict: Pipeline report with counts and statistics.
    """
    print("=" * 70)
    print("MARKETING BRAIN OS — PIPELINE")
    print("=" * 70)

    # Setup
    products_full_dir = os.path.join(PROJECT_ROOT, products_dir)
    if clean and os.path.exists(products_full_dir):
        print("\n[!] Cleaning products directory...")
        shutil.rmtree(products_full_dir)
    os.makedirs(products_full_dir, exist_ok=True)

    # Step 1: Load Telegram messages
    print("\n[1/5] Loading Telegram messages...")
    messages = load_telegram_messages(telegram_dir)
    print(f"      Loaded: {len(messages)} messages")

    if not messages:
        print("[!] No messages found. Exiting.")
        return {"status": "error", "reason": "no_messages"}

    # Step 2: Parse messages
    print("\n[2/5] Parsing messages...")
    parsed = [parse_message(m) for m in messages]
    print(f"      Parsed: {len(parsed)} messages")

    # Step 3: Build products (real Marketing Brain parsing stack)
    print("\n[3/5] Building products via ParserManager -> ProductBuilder -> ProductNormalizer...")
    products = [build_product_from_message(p) for p in parsed]
    print(f"      Products built: {len(products)}")

    # Step 4: Duplicate detection
    print("\n[4/6] Running duplicate detection...")
    dup_engine = DuplicateEngine(data_dir=products_full_dir)
    unique_products = []
    duplicates = []

    for product in products:
        result = dup_engine.check(product)
        if result.duplicate:
            duplicates.append({
                "product_id": product["product_id"],
                "level": result.level,
                "confidence": result.confidence,
                "matched": result.matched_product["product_id"] if result.matched_product else None,
                "reason": result.reason,
            })
        else:
            unique_products.append(product)
            dup_engine.add_to_catalog(product)

    print(f"      Unique products: {len(unique_products)}")
    print(f"      Duplicates found: {len(duplicates)}")
    for dup in duplicates:
        print(f"        - {dup['product_id']} [{dup['level']}] matches {dup['matched']}")

    # Step 5: Save unique products
    print("\n[5/6] Saving unique products to disk...")
    saved_products = save_products(unique_products, products_full_dir)
    print(f"      Saved {saved_products} products to {products_full_dir}")

    # Step 6: Dashboard
    print("\n[6/6] Building dashboard...")
    dashboard = DashboardBackend(data_dir=products_full_dir)
    newest = dashboard.newest(limit=5)
    stats = dashboard.statistics()
    dashboard_products = dashboard._load_all()

    print(f"      Dashboard products: {len(dashboard_products)}")
    print(f"      Total value: ${stats['total_value']:.2f}")
    print(f"      Average price: ${stats['average_price']:.2f}")
    print(f"      Categories: {len(stats['categories'])}")

    # Export
    export_dir = os.path.join(PROJECT_ROOT, "data/exports")
    os.makedirs(export_dir, exist_ok=True)
    export_path = os.path.join(export_dir, f"pipeline_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    dashboard.export(filepath=export_path)
    print(f"      Export saved: {export_path}")

    # Report
    report = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "pipeline": {
            "messages_loaded": len(messages),
            "products_built": len(products),
            "unique_products": len(unique_products),
            "duplicates_found": len(duplicates),
            "duplicates": duplicates,
        },
        "dashboard": {
            "products_count": len(dashboard_products),
            "statistics": stats,
            "newest_products": [p["product_id"] for p in newest],
        },
        "export_path": export_path,
    }

    # Save report
    report_path = os.path.join(PROJECT_ROOT, "data/reports", "pipeline_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'=' * 70}")
    print("PIPELINE COMPLETE")
    print(f"{'=' * 70}")
    print(f"Report: {report_path}")

    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Marketing Brain OS pipeline")
    parser.add_argument("--telegram-dir", default="data/raw/telegram", help="Telegram messages directory")
    parser.add_argument("--products-dir", default="data/products", help="Products output directory")
    parser.add_argument("--clean", action="store_true", help="Clean products directory before running")

    args = parser.parse_args()

    report = run_pipeline(
        telegram_dir=args.telegram_dir,
        products_dir=args.products_dir,
        clean=args.clean,
    )

    print("\n" + json.dumps(report, indent=2))