import shutil
import unittest
from pathlib import Path

from src.parsing.parser_manager import ParserManager
from src.parsing.product_builder import ProductBuilder
from src.parsing.product_normalizer import ProductNormalizer
from src.knowledge.knowledge_repository import KnowledgeRepository
from src.knowledge.knowledge_object import KnowledgeObject


class TestParserIntegration(unittest.TestCase):
    GRAPH_DIR = Path("data/tmp_parser_knowledge")

    def setUp(self) -> None:
        if self.GRAPH_DIR.exists():
            shutil.rmtree(self.GRAPH_DIR)
        self.GRAPH_DIR.mkdir(parents=True, exist_ok=True)

        self.knowledge_repo = KnowledgeRepository(data_dir=str(self.GRAPH_DIR))
        self.parser_manager = ParserManager()
        self.builder = ProductBuilder()
        self.normalizer = ProductNormalizer()

        self.knowledge_repo.save(
            KnowledgeObject(
                type="brand",
                name="Nike",
                value="Nike",
                source="test",
                confidence=0.95,
                language="en",
            )
        )
        self.knowledge_repo.save(
            KnowledgeObject(
                type="category",
                name="Shoes",
                value="Shoes",
                source="test",
                confidence=0.95,
                language="en",
            )
        )
        self.knowledge_repo.save(
            KnowledgeObject(
                type="market",
                name="Egypt",
                value="Egypt",
                source="test",
                confidence=0.9,
                language="en",
            )
        )

    def tearDown(self) -> None:
        if self.GRAPH_DIR.exists():
            shutil.rmtree(self.GRAPH_DIR)

    def test_parse_english_message(self) -> None:
        raw_text = "Nike Running Shoes\nPrice: 120 USD\nCondition: New\nFeatures: breathable mesh, lightweight"
        result = self.parser_manager.parse_message(raw_text, {"message_id": "123", "channel": "telegram"})

        self.assertEqual(result["detected_language"], "en")
        self.assertEqual(result["extracted_brand"], "Nike")
        self.assertEqual(result["extracted_category"], "Shoes")
        self.assertEqual(result["extracted_price"], 120.0)
        self.assertEqual(result["extracted_currency"], "USD")
        self.assertEqual(result["extracted_condition"], "New")
        self.assertIn("breathable mesh", result["extracted_features"])

    def test_parse_arabic_message(self) -> None:
        raw_text = "حذاء Nike الرياضي\nالسعر: ٨٥٠ جنيه\nحالة: جديد\nالمواصفات: خفيف، تنفس"
        result = self.parser_manager.parse_message(raw_text, {"message_id": "456", "channel": "telegram"})

        self.assertEqual(result["detected_language"], "ar")
        self.assertEqual(result["extracted_brand"], "Nike")
        self.assertEqual(result["extracted_category"], "حذاء")
        self.assertEqual(result["extracted_price"], 850.0)
        self.assertEqual(result["extracted_currency"], "EGP")
        self.assertEqual(result["extracted_condition"], "جديد")
        self.assertTrue(result["extracted_features"])

    def test_parse_mixed_message(self) -> None:
        raw_text = "حذاء جديد Nike Air Max\nPrice: 95 USD\nالمواصفات: nyaman, cushioned"
        result = self.parser_manager.parse_message(raw_text, {"message_id": "789", "channel": "telegram"})

        self.assertEqual(result["detected_language"], "mixed")
        self.assertEqual(result["extracted_brand"], "Nike")
        self.assertEqual(result["extracted_price"], 95.0)
        self.assertEqual(result["extracted_currency"], "USD")

    def test_build_product_from_raw_product(self) -> None:
        raw_product = {
            "raw_title": "Nike Running Shoes",
            "raw_description": "Full description",
            "detected_language": "en",
            "extracted_price": 120.0,
            "extracted_currency": "USD",
            "extracted_brand": "Nike",
            "extracted_category": "Shoes",
            "extracted_condition": "New",
            "extracted_features": ["breathable mesh"],
            "confidence_scores": {"price": 0.9, "brand": 0.9, "category": 0.85, "condition": 0.8},
            "source_message_id": "123",
            "source_channel": "telegram",
            "timestamp": "2026-01-01T00:00:00Z",
        }
        product = self.builder.build(raw_product)

        self.assertEqual(product["listing"]["title"], "Nike Running Shoes")
        self.assertEqual(product["listing"]["category"], "Shoes")
        self.assertEqual(product["listing"]["price"]["amount"], 120.0)
        self.assertEqual(product["knowledge_links"]["brand_id"], None)

    def test_normalize_product(self) -> None:
        raw_product = {
            "listing": {
                "title": "nike running shoes",
                "description": "best running shoes",
                "category": "shoes",
                "condition": "New",
                "price": {"amount": 120.0, "currency": "USD"},
                "features": ["breathable mesh", "Breathable mesh"],
                "language": "en",
            },
            "confidence": 0.9,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        normalized = self.normalizer.normalize({**raw_product, "knowledge_repo": self.knowledge_repo})

        self.assertEqual(normalized["listing"]["title"], "Nike Running Shoes")
        self.assertEqual(normalized["listing"]["price"]["currency"], "USD")
        self.assertEqual(normalized["listing"]["category"], "Shoes")
        self.assertEqual(normalized["listing"]["features"], ["Breathable Mesh"])

    def test_full_pipeline_and_knowledge_linking(self) -> None:
        raw_text = "Nike Running Shoes\nPrice: 120 USD\nCondition: New\nFeatures: breathable mesh"
        raw_result = self.parser_manager.parse_message(raw_text, {"message_id": "321", "channel": "telegram"})
        product = self.builder.build(raw_result)
        product["knowledge_repo"] = self.knowledge_repo
        normalized = self.normalizer.normalize(product)

        self.assertEqual(normalized["listing"]["category"], "Shoes")
        self.assertEqual(normalized["listing"]["price"]["currency"], "USD")
        self.assertTrue(normalized["confidence"] > 0)

    def test_handle_missing_fields_gracefully(self) -> None:
        raw_text = "Unknown item without price or category"
        raw_result = self.parser_manager.parse_message(raw_text, {"message_id": "999", "channel": "telegram"})
        product = self.builder.build(raw_result)
        valid, errors = self.builder.validate(product)

        self.assertFalse(valid)
        self.assertIn("Missing or invalid price", errors)


if __name__ == "__main__":
    unittest.main()
