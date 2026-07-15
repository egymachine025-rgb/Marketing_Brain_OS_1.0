"""
tests/test_duplicate_engine.py

Comprehensive tests for DuplicateEngine and FingerprintEngine.
No AI. Pure Python.
"""

import os
import sys
import json
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from marketing_brain_os.fingerprint_engine import FingerprintEngine, compute_similarity
from marketing_brain_os.duplicate_engine import DuplicateEngine, DuplicateResult


class TestFingerprintEngine(unittest.TestCase):

    def setUp(self):
        self.engine = FingerprintEngine()

    def test_same_product_same_fingerprint(self):
        product = {
            "listing": {
                "title": "iPhone 15 Pro Max 256GB Natural Titanium",
                "price": {"amount": 950.0},
                "category": "phone"
            }
        }
        fp1 = self.engine.generate(product)
        fp2 = self.engine.generate(product)
        self.assertEqual(fp1, fp2)

    def test_different_products_different_fingerprints(self):
        p1 = {
            "listing": {
                "title": "iPhone 15 Pro Max 256GB",
                "price": {"amount": 950.0},
                "category": "phone"
            }
        }
        p2 = {
            "listing": {
                "title": "Sony WH-1000XM5 Headphones",
                "price": {"amount": 280.0},
                "category": "audio"
            }
        }
        fp1 = self.engine.generate(p1)
        fp2 = self.engine.generate(p2)
        self.assertNotEqual(fp1, fp2)

    def test_extract_brand_apple_implicit(self):
        product = {"listing": {"title": "iPhone 14", "price": {"amount": 800}}}
        self.assertEqual(self.engine._extract_brand(product), "apple")

    def test_extract_brand_sony(self):
        product = {"listing": {"title": "Sony WH-1000XM5", "price": {"amount": 280}}}
        self.assertEqual(self.engine._extract_brand(product), "sony")

    def test_bucket_price_950(self):
        product = {"listing": {"price": {"amount": 950}}}
        self.assertEqual(self.engine._bucket_price(product), "500-1000")

    def test_bucket_price_2800(self):
        product = {"listing": {"price": {"amount": 2800}}}
        self.assertEqual(self.engine._bucket_price(product), "2000-5000")

    def test_normalize_name_sorts_tokens(self):
        product = {"listing": {"title": "Natural Titanium iPhone 15 Pro Max"}}
        norm = self.engine._normalize_name(product)
        tokens = norm.split()
        self.assertEqual(tokens, sorted(tokens))

    def test_extract_model_iphone(self):
        product = {"listing": {"title": "iPhone 15 Pro Max 256GB"}}
        model = self.engine._extract_model(product)
        self.assertIn("iphone 15 pro max", model)
        self.assertIn("256gb", model)

    def test_extract_model_macbook(self):
        product = {"listing": {"title": "MacBook Air M2 13-inch"}}
        model = self.engine._extract_model(product)
        self.assertIn("macbook air m2", model)

    def test_extract_model_canon(self):
        product = {"listing": {"title": "Canon EOS R6 Mark II Mirrorless Camera"}}
        model = self.engine._extract_model(product)
        self.assertIn("eos r6 mark ii", model)

    def test_extract_model_nintendo(self):
        product = {"listing": {"title": "Nintendo Switch OLED Model White"}}
        model = self.engine._extract_model(product)
        self.assertIn("switch oled", model)


class TestComputeSimilarity(unittest.TestCase):

    def test_identical_components(self):
        c = {"brand": "apple", "category": "phone", "normalized_name": "iphone 15", "price_range": "500-1000", "model": "iphone 15"}
        self.assertEqual(compute_similarity(c, c), 1.0)

    def test_zero_similarity(self):
        c1 = {"brand": "apple", "category": "phone", "normalized_name": "iphone", "price_range": "500-1000", "model": "iphone 15"}
        c2 = {"brand": "sony", "category": "audio", "normalized_name": "headphones", "price_range": "100-250", "model": "wh1000xm5"}
        sim = compute_similarity(c1, c2)
        self.assertLess(sim, 0.3)

    def test_partial_similarity(self):
        c1 = {"brand": "apple", "category": "phone", "normalized_name": "iphone 15 pro max", "price_range": "500-1000", "model": "iphone 15 pro max"}
        c2 = {"brand": "apple", "category": "phone", "normalized_name": "iphone 15 pro", "price_range": "500-1000", "model": "iphone 15 pro"}
        sim = compute_similarity(c1, c2)
        self.assertGreater(sim, 0.7)
        self.assertLess(sim, 1.0)


class TestDuplicateEngine(unittest.TestCase):

    TEST_DATA_DIR = "test_data_products"

    def setUp(self):
        if os.path.exists(self.TEST_DATA_DIR):
            shutil.rmtree(self.TEST_DATA_DIR)
        os.makedirs(self.TEST_DATA_DIR, exist_ok=True)

        self.catalog_products = [
            {
                "product_id": "tg-001",
                "listing": {
                    "title": "iPhone 15 Pro Max 256GB Natural Titanium",
                    "price": {"amount": 950.0, "currency": "USD"},
                    "category": "phone",
                    "condition": "Like New"
                },
                "seller": {"username": "alicesmith"}
            },
            {
                "product_id": "tg-002",
                "listing": {
                    "title": "MacBook Air M2 13-inch Midnight 16GB RAM 512GB SSD",
                    "price": {"amount": 1100.0, "currency": "USD"},
                    "category": "laptop",
                    "condition": "Good"
                },
                "seller": {"username": "bobjohnson"}
            },
            {
                "product_id": "tg-003",
                "listing": {
                    "title": "Sony WH-1000XM5 Wireless Noise Canceling Headphones Black",
                    "price": {"amount": 280.0, "currency": "USD"},
                    "category": "audio",
                    "condition": "Perfect"
                },
                "seller": {"username": "carolw"}
            },
        ]

        for p in self.catalog_products:
            with open(os.path.join(self.TEST_DATA_DIR, f"{p['product_id']}.json"), "w") as f:
                json.dump(p, f)

        self.engine = DuplicateEngine(data_dir=self.TEST_DATA_DIR)

    def tearDown(self):
        if os.path.exists(self.TEST_DATA_DIR):
            shutil.rmtree(self.TEST_DATA_DIR)

    # ------------------------------------------------------------------
    # EXACT duplicate tests
    # ------------------------------------------------------------------

    def test_exact_duplicate_same_product(self):
        incoming = {
            "product_id": "tg-001",
            "listing": {
                "title": "iPhone 15 Pro Max 256GB Natural Titanium",
                "price": {"amount": 950.0, "currency": "USD"},
                "category": "phone",
                "condition": "Like New"
            },
            "seller": {"username": "alicesmith"}
        }
        result = self.engine.check(incoming)
        self.assertTrue(result.duplicate)
        self.assertEqual(result.level, "EXACT")
        self.assertEqual(result.confidence, 1.0)

    # ------------------------------------------------------------------
    # HIGH duplicate tests (>= 90%)
    # ------------------------------------------------------------------

    def test_high_duplicate_minor_variation(self):
        incoming = {
            "product_id": "tg-001b",
            "listing": {
                "title": "iPhone 15 Pro Max 256GB Natural Titanium",
                "price": {"amount": 940.0, "currency": "USD"},
                "category": "phone",
                "condition": "Like New"
            },
            "seller": {"username": "alicesmith2"}
        }
        result = self.engine.check(incoming)
        self.assertTrue(result.duplicate)
        self.assertIn(result.level, ["EXACT", "HIGH"])
        self.assertGreaterEqual(result.confidence, 0.90)

    # ------------------------------------------------------------------
    # MEDIUM duplicate tests (>= 75%)
    # ------------------------------------------------------------------

    def test_medium_duplicate_different_condition(self):
        incoming = {
            "product_id": "tg-001c",
            "listing": {
                "title": "iPhone 15 Pro Max 256GB",
                "price": {"amount": 920.0, "currency": "USD"},
                "category": "phone",
                "condition": "Good"
            },
            "seller": {"username": "someone"}
        }
        result = self.engine.check(incoming)
        self.assertTrue(result.duplicate)
        self.assertIn(result.level, ["HIGH", "MEDIUM", "EXACT"])
        self.assertGreaterEqual(result.confidence, 0.75)

    # ------------------------------------------------------------------
    # LOW duplicate tests (>= 60%)
    # ------------------------------------------------------------------

    def test_low_duplicate_same_brand_category_different_model(self):
        """Same brand and category, different model (iPhone 15 Pro vs 15 Pro Max), same price bucket."""
        incoming = {
            "product_id": "tg-004",
            "listing": {
                "title": "iPhone 15 Pro 128GB",
                "price": {"amount": 850.0, "currency": "USD"},
                "category": "phone",
                "condition": "Good"
            },
            "seller": {"username": "someone"}
        }
        result = self.engine.check(incoming)
        self.assertTrue(result.duplicate)
        self.assertIn(result.level, ["LOW", "MEDIUM", "HIGH", "EXACT"])
        self.assertGreaterEqual(result.confidence, 0.60)

    # ------------------------------------------------------------------
    # NONE / New Product tests
    # ------------------------------------------------------------------

    def test_none_new_product_completely_different(self):
        incoming = {
            "product_id": "tg-999",
            "listing": {
                "title": "Nikon D850 DSLR Camera Body 45MP",
                "price": {"amount": 2200.0, "currency": "USD"},
                "category": "camera",
                "condition": "Excellent"
            },
            "seller": {"username": "photog"}
        }
        result = self.engine.check(incoming)
        self.assertFalse(result.duplicate)
        self.assertEqual(result.level, "NONE")
        self.assertLess(result.confidence, 0.60)

    def test_add_to_catalog_then_duplicate(self):
        new_product = {
            "product_id": "tg-new",
            "listing": {
                "title": "Nintendo Switch OLED White",
                "price": {"amount": 320.0, "currency": "USD"},
                "category": "gaming",
                "condition": "Like New"
            },
            "seller": {"username": "gamer"}
        }
        self.engine.add_to_catalog(new_product)
        result = self.engine.check(new_product)
        self.assertTrue(result.duplicate)
        self.assertEqual(result.level, "EXACT")

    def test_result_has_matched_product_for_non_none(self):
        incoming = {
            "product_id": "tg-001d",
            "listing": {
                "title": "iPhone 15 Pro Max 256GB Natural Titanium",
                "price": {"amount": 950.0, "currency": "USD"},
                "category": "phone",
                "condition": "Like New"
            },
            "seller": {"username": "alicesmith"}
        }
        result = self.engine.check(incoming)
        self.assertIsNotNone(result.matched_product)
        self.assertEqual(result.matched_product["product_id"], "tg-001")

    def test_result_dict_serializable(self):
        incoming = {
            "product_id": "tg-001",
            "listing": {
                "title": "iPhone 15 Pro Max 256GB Natural Titanium",
                "price": {"amount": 950.0, "currency": "USD"},
                "category": "phone"
            },
            "seller": {"username": "alicesmith"}
        }
        result = self.engine.check(incoming)
        d = result.to_dict()
        json_str = json.dumps(d)
        self.assertIsInstance(json_str, str)

    def test_medium_threshold_boundary(self):
        """iPhone 15 Pro Max 256GB vs iPhone 15 Pro Max 128GB - same model gen, same price, less storage."""
        incoming = {
            "product_id": "tg-medium-test",
            "listing": {
                "title": "iPhone 15 Pro Max 128GB Blue Titanium",
                "price": {"amount": 950.0, "currency": "USD"},
                "category": "phone",
                "condition": "Good"
            },
            "seller": {"username": "test"}
        }
        result = self.engine.check(incoming)
        self.assertTrue(result.confidence >= 0.75)
        self.assertIn(result.level, ["MEDIUM", "HIGH", "EXACT"])

    def test_low_threshold_boundary(self):
        """iPhone 15 (base model) vs iPhone 15 Pro Max - same gen, same price bucket, different tier."""
        incoming = {
            "product_id": "tg-low-test",
            "listing": {
                "title": "iPhone 15 128GB Pink",
                "price": {"amount": 650.0, "currency": "USD"},
                "category": "phone",
                "condition": "Good"
            },
            "seller": {"username": "test"}
        }
        result = self.engine.check(incoming)
        self.assertTrue(result.confidence >= 0.60)
        self.assertIn(result.level, ["LOW", "MEDIUM", "HIGH", "EXACT"])


if __name__ == "__main__":
    unittest.main(verbosity=2)