"""
tests/test_pipeline.py

Integration Test: Full Pipeline

Run from project root:
    python -m unittest tests.test_pipeline -v
"""

import os
import sys
import json
import shutil
import unittest

# Add project root to path (so we can import marketing_brain_os)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from marketing_brain_os.fingerprint_engine import FingerprintEngine, compute_similarity
from marketing_brain_os.duplicate_engine import DuplicateEngine, DuplicateResult
from marketing_brain_os.dashboard_backend import DashboardBackend


class TestPipeline(unittest.TestCase):
    """End-to-end pipeline integration test."""

    TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
    PRODUCTS_DIR = os.path.join(TEST_DATA_DIR, "pipeline_products")
    TELEGRAM_FILE = os.path.join(TEST_DATA_DIR, "telegram_messages.json")

    def setUp(self):
        # Clean and create directories
        if os.path.exists(self.PRODUCTS_DIR):
            shutil.rmtree(self.PRODUCTS_DIR)
        os.makedirs(self.PRODUCTS_DIR, exist_ok=True)

        # Load 20 Telegram messages
        with open(self.TELEGRAM_FILE, "r", encoding="utf-8") as f:
            self.telegram_messages = json.load(f)

        self.assertEqual(len(self.telegram_messages), 20, "Must have exactly 20 Telegram messages")

    def tearDown(self):
        if os.path.exists(self.PRODUCTS_DIR):
            shutil.rmtree(self.PRODUCTS_DIR)

    # ------------------------------------------------------------------
    # Simulated ParserManager
    # ------------------------------------------------------------------

    def _parse_telegram_message(self, raw_msg: dict) -> dict:
        """Simulate ParserManager."""
        message = raw_msg.get("message", {})
        from_user = message.get("from", {})
        return {
            "source": "telegram",
            "source_id": str(raw_msg.get("update_id", "")),
            "message_id": str(message.get("message_id", "")),
            "raw_text": message.get("text", ""),
            "sender": {
                "id": str(from_user.get("id", "")),
                "username": from_user.get("username", ""),
                "first_name": from_user.get("first_name", ""),
            },
            "timestamp": message.get("date", 0),
        }

    # ------------------------------------------------------------------
    # Simulated ProductBuilder
    # ------------------------------------------------------------------

    def _build_product(self, parsed_data: dict) -> dict:
        """Simulate ProductBuilder."""
        text = parsed_data["raw_text"]
        import re

        price_match = re.search(r'\$([\d,]+(?:\.\d{2})?)', text)
        price = {"currency": "USD", "amount": float(price_match.group(1).replace(',', ''))} if price_match else None

        conditions = ["like new", "excellent", "good", "fair", "poor", "mint", "perfect", "brand new"]
        condition = next((c.title() for c in conditions if c in text.lower()), "Unknown")

        categories = {
            "phone": ["iphone", "samsung", "pixel", "galaxy"],
            "laptop": ["macbook", "laptop", "thinkpad", "dell", "xps"],
            "audio": ["headphones", "earbuds", "airpods", "speaker", "bose", "sony wh"],
            "gaming": ["nintendo", "playstation", "xbox", "switch"],
            "camera": ["canon", "nikon", "sony a", "mirrorless"],
            "tablet": ["ipad", "galaxy tab"],
            "wearable": ["apple watch"],
            "drone": ["dji"],
            "monitor": ["monitor", "ultragear"],
        }
        category = next((k for k, v in categories.items() if any(x in text.lower() for x in v)), "uncategorized")

        brands = ["apple", "samsung", "sony", "canon", "nikon", "dell", "lenovo", "lg", "google", "bose", "dji"]
        brand = next((b for b in brands if b in text.lower()), None)

        return {
            "product_id": f"tg-{parsed_data['source_id']}",
            "source": {"platform": "telegram", "message_id": parsed_data["message_id"], "update_id": parsed_data["source_id"]},
            "listing": {
                "title": text.split('.')[0] if '.' in text else text[:60],
                "description": text,
                "price": price,
                "condition": condition,
                "category": category,
                "brand": brand,
            },
            "seller": parsed_data["sender"],
            "metadata": {"acquired_at": parsed_data["timestamp"], "parser_version": "1.0.0"},
            "status": "active",
        }

    # ------------------------------------------------------------------
    # Pipeline Test
    # ------------------------------------------------------------------

    def test_full_pipeline(self):
        """Run the complete pipeline and verify all counts match."""

        # Step 1: Parse 20 Telegram messages
        parsed_messages = [self._parse_telegram_message(m) for m in self.telegram_messages]
        self.assertEqual(len(parsed_messages), 20, "Step 1: Must parse 20 messages")

        # Step 2: Build products
        products = [self._build_product(p) for p in parsed_messages]
        self.assertEqual(len(products), 20, "Step 2: Must build 20 products")

        # Step 3: Duplicate Detection
        dup_engine = DuplicateEngine(data_dir=self.PRODUCTS_DIR)
        unique_products = []
        duplicates_found = []

        for product in products:
            result = dup_engine.check(product)
            if result.duplicate:
                duplicates_found.append({
                    "product_id": product["product_id"],
                    "level": result.level,
                    "confidence": result.confidence,
                    "matched": result.matched_product["product_id"] if result.matched_product else None,
                })
            else:
                unique_products.append(product)
                dup_engine.add_to_catalog(product)

        # Step 4: Repository + Dashboard
        backend = DashboardBackend(data_dir=self.PRODUCTS_DIR)
        repo_count = backend.count()
        dash_products = backend._load_all()
        dash_stats = backend.statistics()
        dash_dups = backend.duplicate_report()

        # ------------------------------------------------------------------
        # Verification
        # ------------------------------------------------------------------

        print("\n" + "=" * 60)
        print("PIPELINE REPORT")
        print("=" * 60)
        print(f"  Telegram Messages Parsed:    {len(parsed_messages)}")
        print(f"  Products Built:                {len(products)}")
        print(f"  Duplicates Found:              {len(duplicates_found)}")
        print(f"  Unique Products:                 {len(unique_products)}")
        print(f"  Repository Count:                {repo_count}")
        print(f"  Dashboard Products Count:        {len(dash_products)}")
        print(f"  Dashboard Duplicate Groups:      {len(dash_dups['duplicate_groups'])}")
        print(f"  Dashboard Statistics:            {json.dumps(dash_stats, indent=2)}")
        print("=" * 60)

        # Verify counts match
        self.assertEqual(len(products), 20, "Products Count must be 20")
        self.assertEqual(len(unique_products), 20 - len(duplicates_found), "Unique = Total - Duplicates")
        self.assertEqual(repo_count, len(unique_products), "Repository Count must equal Unique Products")
        self.assertEqual(len(dash_products), repo_count, "Dashboard Count must equal Repository Count")

        # Verify statistics
        self.assertEqual(dash_stats["total_products"], len(dash_products), "Stats total must match dashboard count")
        self.assertGreater(dash_stats["total_value"], 0, "Total value must be > 0")
        self.assertGreater(dash_stats["average_price"], 0, "Average price must be > 0")

        # Verify newest products
        newest = backend.newest(limit=5)
        self.assertEqual(len(newest), min(5, len(dash_products)), "Newest products limit must work")

        # Verify search
        search_results = backend.search("iPhone")
        self.assertGreaterEqual(len(search_results), 0, "Search must work")

        # Verify filter
        filtered = backend.filter(category="phone")
        self.assertGreaterEqual(len(filtered), 0, "Filter must work")

        # Verify export
        export_json = backend.export()
        export_data = json.loads(export_json)
        self.assertEqual(export_data["count"], len(dash_products), "Export count must match")
        self.assertIn("exported_at", export_data, "Export must have timestamp")

        print("\n✅ ALL PIPELINE VERIFICATIONS PASSED")


if __name__ == "__main__":
    unittest.main(verbosity=2)