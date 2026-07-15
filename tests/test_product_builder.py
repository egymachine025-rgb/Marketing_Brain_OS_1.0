from __future__ import annotations
import unittest
from datetime import datetime
from src.acquisition.telegram import TelegramRawMessage
from marketing_brain_os.product_builder import ProductBuilder
from src.models.base import Currency

class TestProductBuilder(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = ProductBuilder()
        
        # Set up a generic valid raw message context
        self.valid_message = TelegramRawMessage(
            message_id="99823",
            channel_id="deals_tech_channel",
            content_text="Check out this brand new Sony headphones! Only $299.99 on our store. Color: Black and Silver.",
            media_metadata={
                "images": ["https://cdn.store/headphones_1.jpg"],
                "videos": [],
                "seller": "SuperStore Inc"
            },
            forward_count=5,
            view_count=120,
            timestamp=datetime.utcnow()
        )

    def test_build_product_success(self) -> None:
        parse_result = {
            "cleaned_text": "Check out this brand new Sony headphones!\nOnly $299.99 on our store.\nColor: Black and Silver.",
            "brands": ["Sony"],
            "categories": ["Electronics"],
            "pricing": [{"value": 299.99, "currency": "USD"}],
            "colors": ["black", "silver"],
            "features": ["wireless", "noise-canceling"]
        }

        product = self.builder.build_from_telegram(self.valid_message, parse_result)
        
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "Check out this brand new Sony headphones!")
        self.assertEqual(product.brand, "Sony")
        self.assertEqual(product.category, "Electronics")
        self.assertEqual(product.price, 299.99)
        self.assertEqual(product.currency, Currency.USD)
        self.assertIn("black", product.colors)
        self.assertEqual(product.telegram_message_id, "99823")
        self.assertEqual(product.telegram_channel, "deals_tech_channel")
        self.assertTrue(len(product.fingerprint) > 0)

    def test_validation_ignore_no_category(self) -> None:
        parse_result_no_cat = {
            "cleaned_text": "No category headphones Sony!",
            "brands": ["Sony"],
            "categories": [],  # Empty Category
            "pricing": [{"value": 299.99, "currency": "USD"}]
        }

        product = self.builder.build_from_telegram(self.valid_message, parse_result_no_cat)
        self.assertNil = self.assertIsNone(product)

    def test_validation_ignore_no_useful_info(self) -> None:
        parse_result_empty = {
            "cleaned_text": "", # No Text
            "brands": [],
            "categories": [],
            "pricing": []
        }

        product = self.builder.build_from_telegram(self.valid_message, parse_result_empty)
        self.assertIsNone(product)


if __name__ == "__main__":
    unittest.main()