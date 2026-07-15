import json
import shutil
import unittest
import uuid
from pathlib import Path

from src.knowledge.knowledge_object import KnowledgeObject
from src.knowledge.knowledge_repository import KnowledgeRepository


class TestKnowledgeRepository(unittest.TestCase):
    TEST_DIR = Path("data/tmp_knowledge_repo_test")

    def setUp(self) -> None:
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)
        self.TEST_DIR.mkdir(parents=True, exist_ok=True)
        self.repo = KnowledgeRepository(data_dir=str(self.TEST_DIR))

    def tearDown(self) -> None:
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)

    def test_save_new_entity(self) -> None:
        obj = KnowledgeObject(
            type="brand",
            name="Nike",
            value="Nike",
            source="telegram_channel_x",
            confidence=0.95,
            language="en",
            metadata={"countries": ["Egypt"]},
        )

        saved = self.repo.save(obj)
        self.assertEqual(saved.type, "brand")
        self.assertEqual(saved.name, "Nike")
        self.assertEqual(saved.source, "telegram_channel_x")
        self.assertEqual(saved.confidence, 0.95)
        self.assertEqual(saved.language, "en")
        self.assertEqual(saved.metadata["countries"], ["Egypt"])

    def test_save_duplicate_merges_entity(self) -> None:
        obj1 = KnowledgeObject(
            type="brand",
            name="Nike",
            value="Nike",
            source="telegram_channel_x",
            confidence=0.90,
            language="en",
            metadata={"countries": ["EG"]},
        )
        obj2 = KnowledgeObject(
            type="brand",
            name="Nike",
            value="Nike Inc.",
            source="telegram_channel_y",
            confidence=0.70,
            language="en",
            metadata={"colors": ["Black"]},
        )

        saved1 = self.repo.save(obj1)
        saved2 = self.repo.save(obj2)

        self.assertEqual(saved1.id, saved2.id)
        self.assertEqual(saved2.created_at, saved1.created_at)
        self.assertEqual(saved2.confidence, 0.8)
        self.assertEqual(saved2.metadata["countries"], ["EG"])
        self.assertEqual(saved2.metadata["colors"], ["Black"])
        self.assertGreater(saved2.updated_at, saved1.updated_at)

    def test_get_by_composite_key(self) -> None:
        obj = KnowledgeObject(
            type="category",
            name="Shoes",
            value="Footwear",
            source="telegram_channel_x",
            confidence=1.0,
            language="en",
        )
        self.repo.save(obj)

        retrieved = self.repo.get_by_type_and_name("category", "Shoes", "en")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Shoes")

    def test_link_product(self) -> None:
        obj = KnowledgeObject(
            type="brand",
            name="Adidas",
            value="Adidas",
            source="telegram_channel_z",
            confidence=0.9,
            language="en",
        )
        saved = self.repo.save(obj)

        linked = self.repo.link_product(saved.id, "prod-001")
        self.assertTrue(linked)
        self.assertEqual(self.repo.get_linked_products(saved.id), ["prod-001"])

        linked_again = self.repo.link_product(saved.id, "prod-001")
        self.assertFalse(linked_again)

    def test_get_statistics(self) -> None:
        self.repo.save(
            KnowledgeObject(
                type="brand",
                name="Nike",
                value="Nike",
                source="telegram_channel_x",
                confidence=0.9,
                language="en",
            )
        )
        self.repo.save(
            KnowledgeObject(
                type="category",
                name="Shoes",
                value="Footwear",
                source="telegram_channel_y",
                confidence=0.8,
                language="en",
            )
        )

        stats = self.repo.get_statistics()
        self.assertEqual(stats["total_entities"], 2)
        self.assertEqual(stats["counts_by_type"], {"brand": 1, "category": 1})
        self.assertEqual(stats["avg_confidence"], 0.85)

    def test_delete(self) -> None:
        saved = self.repo.save(
            KnowledgeObject(
                type="brand",
                name="Puma",
                value="Puma",
                source="telegram_channel_x",
                confidence=0.9,
                language="en",
            )
        )

        deleted = self.repo.delete(saved.id)
        self.assertTrue(deleted)
        self.assertIsNone(self.repo.get_by_id(saved.id))


if __name__ == "__main__":
    unittest.main()
