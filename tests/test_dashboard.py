"""
tests/test_dashboard.py

Tests for dashboard_repository.py and dashboard_service.py.
No UI. Pure Backend.
"""

import os
import sys
import json
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from marketing_brain_os.dashboard_repository import DashboardRepository
from marketing_brain_os.dashboard_service import DashboardService


class TestDashboardRepository(unittest.TestCase):

    TEST_DIR = "test_dashboard_repo"

    def setUp(self):
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)
        os.makedirs(self.TEST_DIR, exist_ok=True)
        self.repo = DashboardRepository(data_dir=self.TEST_DIR)

    def tearDown(self):
        for d in [self.TEST_DIR, "test_empty_stats"]:
            if os.path.exists(d):
                shutil.rmtree(d)

    def test_load_all_empty(self):
        products = self.repo.load_all()
        self.assertEqual(products, [])

    def test_save_and_load(self):
        product = {
            "product_id": "tg-001",
            "listing": {"title": "iPhone 15", "price": {"amount": 950}},
            "seller": {"username": "alice"}
        }
        self.repo.save(product)
        loaded = self.repo.load_all()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["product_id"], "tg-001")

    def test_load_by_id(self):
        product = {
            "product_id": "tg-002",
            "listing": {"title": "MacBook Air", "price": {"amount": 1100}},
            "seller": {"username": "bob"}
        }
        self.repo.save(product)
        found = self.repo.load_by_id("tg-002")
        self.assertIsNotNone(found)
        self.assertEqual(found["listing"]["title"], "MacBook Air")

    def test_load_by_id_not_found(self):
        found = self.repo.load_by_id("nonexistent")
        self.assertIsNone(found)

    def test_delete(self):
        product = {"product_id": "tg-003", "listing": {"title": "X"}, "seller": {}}
        self.repo.save(product)
        self.assertTrue(self.repo.delete("tg-003"))
        self.assertEqual(self.repo.count(), 0)

    def test_count(self):
        self.assertEqual(self.repo.count(), 0)
        self.repo.save({"product_id": "a", "listing": {}, "seller": {}})
        self.assertEqual(self.repo.count(), 1)


class TestDashboardService(unittest.TestCase):

    TEST_DIR = "test_dashboard_service"

    def setUp(self):
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)
        os.makedirs(self.TEST_DIR, exist_ok=True)

        # Seed with sample products
        self.products = [
            {
                "product_id": "tg-001",
                "listing": {
                    "title": "iPhone 15 Pro Max 256GB",
                    "description": "Like new iPhone",
                    "price": {"amount": 950.0, "currency": "USD"},
                    "category": "phone",
                    "condition": "Like New"
                },
                "seller": {"username": "alicesmith", "display_name": "Alice Smith"},
                "metadata": {"acquired_at": "2023-07-14T08:00:00Z"},
                "status": "active"
            },
            {
                "product_id": "tg-002",
                "listing": {
                    "title": "MacBook Air M2",
                    "description": "Great laptop",
                    "price": {"amount": 1100.0, "currency": "USD"},
                    "category": "laptop",
                    "condition": "Good"
                },
                "seller": {"username": "bobjohnson", "display_name": "Bob Johnson"},
                "metadata": {"acquired_at": "2023-07-15T08:00:00Z"},
                "status": "active"
            },
            {
                "product_id": "tg-003",
                "listing": {
                    "title": "Sony WH-1000XM5",
                    "description": "Noise canceling headphones",
                    "price": {"amount": 280.0, "currency": "USD"},
                    "category": "audio",
                    "condition": "Perfect"
                },
                "seller": {"username": "carolw", "display_name": "Carol Williams"},
                "metadata": {"acquired_at": "2023-07-16T08:00:00Z"},
                "status": "active"
            },
        ]

        for p in self.products:
            filepath = os.path.join(self.TEST_DIR, f"{p['product_id']}.json")
            with open(filepath, "w") as f:
                json.dump(p, f)

        self.service = DashboardService(data_dir=self.TEST_DIR)

    def tearDown(self):
        for d in [self.TEST_DIR, "test_empty_stats"]:
            if os.path.exists(d):
                shutil.rmtree(d)

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def test_get_all_products(self):
        products = self.service.get_all_products()
        self.assertEqual(len(products), 3)

    def test_get_product_by_id(self):
        product = self.service.get_product_by_id("tg-002")
        self.assertIsNotNone(product)
        self.assertEqual(product["listing"]["title"], "MacBook Air M2")

    def test_get_product_by_id_not_found(self):
        product = self.service.get_product_by_id("xxx")
        self.assertIsNone(product)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def test_search_by_title(self):
        results = self.service.search("iPhone")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["product_id"], "tg-001")

    def test_search_by_seller(self):
        results = self.service.search("bobjohnson")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["product_id"], "tg-002")

    def test_search_by_category(self):
        results = self.service.search("audio")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["product_id"], "tg-003")

    def test_search_no_results(self):
        results = self.service.search("nonexistent")
        self.assertEqual(len(results), 0)

    # ------------------------------------------------------------------
    # Filter
    # ------------------------------------------------------------------

    def test_filter_by_category(self):
        results = self.service.filter_products(category="phone")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["product_id"], "tg-001")

    def test_filter_by_condition(self):
        results = self.service.filter_products(condition="Good")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["product_id"], "tg-002")

    def test_filter_by_price_range(self):
        results = self.service.filter_products(min_price=500, max_price=1000)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["product_id"], "tg-001")

    def test_filter_by_brand(self):
        results = self.service.filter_products(brand="iphone")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["product_id"], "tg-001")

    def test_filter_combined(self):
        results = self.service.filter_products(category="phone", min_price=900)
        self.assertEqual(len(results), 1)

    # ------------------------------------------------------------------
    # Sort
    # ------------------------------------------------------------------

    def test_sort_by_price_ascending(self):
        products = self.service.get_all_products()
        sorted_products = self.service.sort_products(products, sort_by="price", ascending=True)
        prices = [p["listing"]["price"]["amount"] for p in sorted_products]
        self.assertEqual(prices, [280.0, 950.0, 1100.0])

    def test_sort_by_price_descending(self):
        products = self.service.get_all_products()
        sorted_products = self.service.sort_products(products, sort_by="price", ascending=False)
        prices = [p["listing"]["price"]["amount"] for p in sorted_products]
        self.assertEqual(prices, [1100.0, 950.0, 280.0])

    def test_sort_by_title(self):
        products = self.service.get_all_products()
        sorted_products = self.service.sort_products(products, sort_by="title", ascending=True)
        titles = [p["listing"]["title"] for p in sorted_products]
        self.assertEqual(titles, ["iPhone 15 Pro Max 256GB", "MacBook Air M2", "Sony WH-1000XM5"])

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def test_statistics(self):
        stats = self.service.get_statistics()
        self.assertEqual(stats["total_products"], 3)
        self.assertEqual(stats["total_value"], 2330.0)
        self.assertEqual(stats["average_price"], 776.67)
        self.assertEqual(stats["min_price"], 280.0)
        self.assertEqual(stats["max_price"], 1100.0)
        self.assertEqual(stats["categories"]["phone"], 1)
        self.assertEqual(stats["categories"]["laptop"], 1)
        self.assertEqual(stats["categories"]["audio"], 1)

    def test_statistics_empty(self):
        empty_dir = "test_empty_stats"
        if os.path.exists(empty_dir):
            shutil.rmtree(empty_dir)
        os.makedirs(empty_dir, exist_ok=True)
        service = DashboardService(data_dir=empty_dir)
        stats = service.get_statistics()
        self.assertEqual(stats["total_products"], 0)
        self.assertEqual(stats["total_value"], 0.0)
        shutil.rmtree(empty_dir)

    # ------------------------------------------------------------------
    # Newest Products
    # ------------------------------------------------------------------

    def test_get_newest_products(self):
        newest = self.service.get_newest_products(limit=2)
        self.assertEqual(len(newest), 2)
        # tg-003 has latest acquired_at
        self.assertEqual(newest[0]["product_id"], "tg-003")

    # ------------------------------------------------------------------
    # Export JSON
    # ------------------------------------------------------------------

    def test_export_json(self):
        json_str = self.service.export_json()
        data = json.loads(json_str)
        self.assertEqual(data["count"], 3)
        self.assertIn("exported_at", data)
        self.assertEqual(len(data["products"]), 3)

    def test_export_json_to_file(self):
        export_path = os.path.join(self.TEST_DIR, "export.json")
        self.service.export_json(filepath=export_path)
        self.assertTrue(os.path.exists(export_path))
        with open(export_path, "r") as f:
            data = json.load(f)
        self.assertEqual(data["count"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)