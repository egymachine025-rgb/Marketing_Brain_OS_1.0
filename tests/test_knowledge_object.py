import unittest
import uuid
from datetime import datetime

from src.knowledge.knowledge_object import KnowledgeObject


class TestKnowledgeObject(unittest.TestCase):
    def test_create_default_confidence_and_metadata(self):
        obj = KnowledgeObject(
            type="fact",
            name="Product color",
            value="red",
            source="parser",
            language="en"
        )

        self.assertIsInstance(obj.id, uuid.UUID)
        self.assertEqual(obj.confidence, 1.0)
        self.assertEqual(obj.metadata, {})
        self.assertEqual(obj.type, "fact")
        self.assertEqual(obj.name, "Product color")
        self.assertEqual(obj.value, "red")
        self.assertEqual(obj.source, "parser")
        self.assertEqual(obj.language, "en")
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_to_dict_and_from_dict_roundtrip(self):
        original = KnowledgeObject(
            id=uuid.uuid4(),
            type="insight",
            name="Price trend",
            value={"direction": "up", "percent": 12},
            source="knowledge_engine",
            confidence=0.92,
            language="ar",
            metadata={"source_channel": "telegram", "tags": ["trend", "price"]},
        )

        serialized = original.to_dict()
        self.assertEqual(serialized["type"], "insight")
        self.assertEqual(serialized["confidence"], 0.92)
        self.assertEqual(serialized["language"], "ar")
        self.assertEqual(serialized["metadata"], {"source_channel": "telegram", "tags": ["trend", "price"]})

        restored = KnowledgeObject.from_dict(serialized)
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.type, original.type)
        self.assertEqual(restored.name, original.name)
        self.assertEqual(restored.value, original.value)
        self.assertEqual(restored.source, original.source)
        self.assertEqual(restored.confidence, original.confidence)
        self.assertEqual(restored.language, original.language)
        self.assertEqual(restored.metadata, original.metadata)
        self.assertEqual(restored.created_at, original.created_at)
        self.assertEqual(restored.updated_at, original.updated_at)

    def test_immutability(self):
        obj = KnowledgeObject(
            type="fact",
            name="Seller rating",
            value=4.8,
            source="review_parser",
            language="en"
        )

        with self.assertRaises(AttributeError):
            obj.name = "Changed"


if __name__ == "__main__":
    unittest.main()
