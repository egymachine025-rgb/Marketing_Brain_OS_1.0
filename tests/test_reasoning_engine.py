import shutil
import unittest
import uuid
from pathlib import Path

from src.knowledge.knowledge_graph import KnowledgeGraph
from src.knowledge.knowledge_repository import KnowledgeRepository
from src.knowledge.reasoning_engine import ReasoningEngine
from src.knowledge.knowledge_object import KnowledgeObject


class TestReasoningEngine(unittest.TestCase):
    GRAPH_DIR = Path("data/tmp_reasoning_graph_test")
    REPO_DIR = Path("data/tmp_reasoning_repo_test")

    def setUp(self) -> None:
        for path in (self.GRAPH_DIR, self.REPO_DIR):
            if path.exists():
                shutil.rmtree(path)
            path.mkdir(parents=True, exist_ok=True)

        self.repository = KnowledgeRepository(data_dir=str(self.REPO_DIR))
        self.graph = KnowledgeGraph(data_dir=str(self.GRAPH_DIR))
        self.engine = ReasoningEngine(self.repository, self.graph)

    def tearDown(self) -> None:
        for path in (self.GRAPH_DIR, self.REPO_DIR):
            if path.exists():
                shutil.rmtree(path)

    def _save_brand(self, name: str, market: str, categories: list[str]) -> KnowledgeObject:
        brand = self.repository.save(
            KnowledgeObject(
                type="brand",
                name=name,
                value=name,
                source="test",
                confidence=0.9,
                language="en",
                metadata={"market": market},
            )
        )
        market_node = self.repository.save(
            KnowledgeObject(
                type="market",
                name=market,
                value=market,
                source="test",
                confidence=0.9,
                language="en",
            )
        )
        self.graph.add_relationship(brand.id, market_node.id, "has_market")
        for category in categories:
            category_node = self.repository.save(
                KnowledgeObject(
                    type="category",
                    name=category,
                    value=category,
                    source="test",
                    confidence=0.9,
                    language="en",
                )
            )
            self.graph.add_relationship(brand.id, category_node.id, "has_category")
        return brand

    def _save_product(self, brand_name: str, product_id: str, price: float, category: str) -> KnowledgeObject:
        product = self.repository.save(
            KnowledgeObject(
                type="product",
                name=product_id,
                value=product_id,
                source="test",
                confidence=0.9,
                language="en",
                metadata={
                    "brand": brand_name,
                    "price": price,
                    "product_id": product_id,
                    "category": category,
                },
            )
        )
        return product

    def test_infer_competitive_landscape(self) -> None:
        nike = self._save_brand("Nike", "Egypt", ["Shoes", "Running"])
        adidas = self._save_brand("Adidas", "Egypt", ["Shoes", "Running", "Basketball"])
        self.repository.link_product(nike.id, "p-nike-1")
        self.repository.link_product(adidas.id, "p-adidas-1")
        self.repository.link_product(adidas.id, "p-adidas-2")

        landscape = self.engine.infer_competitive_landscape("Nike", "Egypt")
        self.assertEqual(landscape["brand"], "Nike")
        self.assertEqual(landscape["market"], "Egypt")
        self.assertTrue(any(item["name"] == "Adidas" for item in landscape["competitors"]))
        self.assertIn("Basketball", landscape["unique_categories"])
        self.assertIn(landscape["threat_level"], {"low", "medium", "high", "critical", "unknown"})

    def test_infer_market_gaps(self) -> None:
        self._save_brand("Nike", "Egypt", ["Shoes", "Running"])
        self._save_brand("Adidas", "Egypt", ["Shoes"])
        self._save_brand("Puma", "Egypt", ["Shoes"])

        gaps = self.engine.infer_market_gaps("Egypt")
        self.assertTrue(any(gap["category"] == "Running" for gap in gaps))
        self.assertTrue(all(gap["competitor_count"] < 3 for gap in gaps))

    def test_infer_audience_overlap(self) -> None:
        nike = self.repository.save(
            KnowledgeObject(
                type="brand",
                name="Nike",
                value="Nike",
                source="test",
                confidence=0.9,
                language="en",
            )
        )
        adidas = self.repository.save(
            KnowledgeObject(
                type="brand",
                name="Adidas",
                value="Adidas",
                source="test",
                confidence=0.9,
                language="en",
            )
        )
        men = self.repository.save(
            KnowledgeObject(
                type="audience",
                name="Men",
                value="Men",
                source="test",
                confidence=0.9,
                language="en",
            )
        )
        youth = self.repository.save(
            KnowledgeObject(
                type="audience",
                name="18-35",
                value="18-35",
                source="test",
                confidence=0.9,
                language="en",
            )
        )
        self.graph.add_relationship(nike.id, men.id, "has_audience")
        self.graph.add_relationship(nike.id, youth.id, "has_audience")
        self.graph.add_relationship(adidas.id, men.id, "has_audience")

        overlap = self.engine.infer_audience_overlap("Nike", "Adidas")
        self.assertEqual(overlap["shared_audiences"], ["Men"])
        self.assertEqual(overlap["overlap_score"], 0.5)
        self.assertEqual(overlap["unique_to_a"], ["18-35"])
        self.assertEqual(overlap["unique_to_b"], [])

    def test_infer_price_positioning(self) -> None:
        nike = self._save_brand("Nike", "Egypt", ["Shoes"])
        self._save_product("Nike", "p1", 100.0, "Shoes")
        self._save_product("Nike", "p2", 150.0, "Shoes")
        self.repository.link_product(nike.id, "p1")
        self.repository.link_product(nike.id, "p2")
        adidas = self._save_brand("Adidas", "Egypt", ["Shoes"])
        self._save_product("Adidas", "pa1", 90.0, "Shoes")
        self._save_product("Adidas", "pa2", 95.0, "Shoes")
        self.repository.link_product(adidas.id, "pa1")
        self.repository.link_product(adidas.id, "pa2")

        positioning = self.engine.infer_price_positioning("Nike")
        self.assertIn(positioning["tier"], {"high", "mid", "low", "unknown"})
        self.assertGreater(positioning["avg_price"], 0)
        self.assertIn("Adidas", positioning["vs_competitors"])
        self.assertIn(positioning["price_range"], {"high", "mid", "low", "unknown"})

    def test_infer_trending_categories(self) -> None:
        self._save_brand("Nike", "Egypt", ["Shoes", "Running"])
        self._save_brand("Adidas", "Egypt", ["Shoes"])
        trends = self.engine.infer_trending_categories("Egypt", limit=2)
        self.assertEqual(len(trends), 2)
        self.assertEqual(trends[0]["category"], "Shoes")

    def test_infer_recommendations(self) -> None:
        self._save_brand("Nike", "Egypt", ["Shoes"])
        recs = self.engine.infer_recommendations("Nike", "increase_market_share")
        self.assertTrue(isinstance(recs, list))
        self.assertTrue(all("strategy" in rec for rec in recs))


if __name__ == "__main__":
    unittest.main()
