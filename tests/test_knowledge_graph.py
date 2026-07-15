import shutil
import unittest
import uuid
from pathlib import Path

from marketing_brain_os.product import Product
from src.knowledge.graph_builder import GraphBuilder
from src.knowledge.knowledge_graph import KnowledgeGraph
from src.knowledge.knowledge_repository import KnowledgeRepository
from src.models.base import Currency


class TestKnowledgeGraph(unittest.TestCase):
    GRAPH_DIR = Path("data/tmp_knowledge_graph_test")
    REPO_DIR = Path("data/tmp_knowledge_graph_repo")

    def setUp(self) -> None:
        for path in (self.GRAPH_DIR, self.REPO_DIR):
            if path.exists():
                shutil.rmtree(path)
            path.mkdir(parents=True, exist_ok=True)

        self.graph = KnowledgeGraph(data_dir=str(self.GRAPH_DIR))
        self.repository = KnowledgeRepository(data_dir=str(self.REPO_DIR))
        self.builder = GraphBuilder()

    def tearDown(self) -> None:
        for path in (self.GRAPH_DIR, self.REPO_DIR):
            if path.exists():
                shutil.rmtree(path)

    def test_add_and_retrieve_relationship(self) -> None:
        from_id = uuid.uuid4()
        to_id = uuid.uuid4()

        relationship = self.graph.add_relationship(
            from_id,
            to_id,
            "has_category",
            weight=0.8,
            metadata={"source": "unit_test"},
        )

        self.assertEqual(relationship["from_id"], str(from_id))
        self.assertEqual(relationship["to_id"], str(to_id))
        self.assertEqual(relationship["relation_type"], "has_category")
        self.assertEqual(relationship["weight"], 0.8)

        outgoing = self.graph.get_relationships(from_id)
        self.assertEqual(len(outgoing), 1)
        self.assertEqual(outgoing[0]["to_id"], str(to_id))

        incoming = self.graph.get_related(to_id)
        self.assertEqual(len(incoming), 1)
        self.assertEqual(incoming[0]["from_id"], str(from_id))

    def test_get_neighbors_grouped_by_type(self) -> None:
        source = uuid.uuid4()
        category = uuid.uuid4()
        market = uuid.uuid4()

        self.graph.add_relationship(source, category, "has_category")
        self.graph.add_relationship(source, market, "has_market")

        neighbors = self.graph.get_neighbors(source)
        self.assertIn("has_category", neighbors)
        self.assertIn("has_market", neighbors)
        self.assertEqual(neighbors["has_category"][0]["to_id"], str(category))
        self.assertEqual(neighbors["has_market"][0]["to_id"], str(market))

    def test_find_path_between_entities(self) -> None:
        start = uuid.uuid4()
        middle = uuid.uuid4()
        end = uuid.uuid4()

        self.graph.add_relationship(start, middle, "has_category")
        self.graph.add_relationship(middle, end, "has_market")

        paths = self.graph.find_path(start, end, max_depth=3)
        self.assertEqual(paths, [[str(start), str(middle), str(end)]])

    def test_delete_relationship(self) -> None:
        source = uuid.uuid4()
        target = uuid.uuid4()

        self.graph.add_relationship(source, target, "has_category")
        deleted = self.graph.delete_relationship(source, target, "has_category")

        self.assertTrue(deleted)
        self.assertEqual(self.graph.get_relationships(source), [])
        self.assertEqual(self.graph.get_related(target), [])

    def test_graph_statistics(self) -> None:
        a = uuid.uuid4()
        b = uuid.uuid4()
        c = uuid.uuid4()

        self.graph.add_relationship(a, b, "has_category")
        self.graph.add_relationship(a, c, "has_market")
        self.graph.add_relationship(b, c, "has_tier")

        stats = self.graph.get_graph_statistics()
        self.assertEqual(stats["total_relationships"], 3)
        self.assertEqual(stats["relationships_by_type"], {
            "has_category": 1,
            "has_market": 1,
            "has_tier": 1,
        })
        self.assertEqual(stats["unique_entities"], 3)

    def test_build_graph_from_mock_products(self) -> None:
        products = [
            Product(
                id=uuid.uuid4(),
                name="Runner 1",
                brand="Nike",
                category="Shoes",
                language="en",
                price=100.0,
                offer="Best running shoes",
                colors=["Black"],
                features=["Lightweight", "Breathable"],
                keywords=["running", "sports"],
                description="A lightweight running shoe",
                currency=Currency.USD,
            ),
            Product(
                id=uuid.uuid4(),
                name="Runner 2",
                brand="Nike",
                category="Shoes",
                language="en",
                price=110.0,
                offer="Comfortable running shoe",
                colors=["Blue"],
                features=["Breathable"],
                keywords=["running"],
                description="A comfortable running shoe",
                currency=Currency.USD,
            ),
            Product(
                id=uuid.uuid4(),
                name="Sneaker",
                brand="Adidas",
                category="Shoes",
                language="en",
                price=320.0,
                offer="Premium sneaker",
                colors=["White"],
                features=["Premium sole"],
                keywords=["sneaker"],
                description="A premium sneaker for everyday wear",
                currency=Currency.USD,
            ),
        ]

        products[0].attributes = {"market": "Egypt", "audience": "Men, 18-35"}
        products[1].attributes = {"market": "Egypt"}
        products[2].attributes = {"market": "Egypt", "audience": "Women"}

        self.builder.build_from_products(products, self.repository, self.graph)

        brand_entity = self.repository.get_by_type_and_name("brand", "Nike", "en")
        self.assertIsNotNone(brand_entity)

        category_entity = self.repository.get_by_type_and_name("category", "Shoes", "en")
        self.assertIsNotNone(category_entity)

        self.assertTrue(
            any(
                rel["relation_type"] == "has_category"
                and rel["from_id"] == str(brand_entity.id)
                and rel["to_id"] == str(category_entity.id)
                for rel in self.graph.get_relationships(brand_entity.id)
            )
        )

        similar_relationships = []
        for product in products[:2]:
            product_entity = self.repository.find_by_metadata("product_id", str(product.id))
            self.assertTrue(product_entity, f"Product node not found for {product.name}")
            for node in product_entity:
                similar_relationships.extend(
                    rel
                    for rel in self.graph.get_relationships(node.id)
                    if rel["relation_type"] == "similar_to"
                )

        self.assertTrue(len(similar_relationships) >= 1)

        audience_entity = self.repository.get_by_type_and_name("audience", "Men", "en")
        self.assertIsNotNone(audience_entity)
        self.assertTrue(
            any(
                rel["relation_type"] == "has_audience"
                and rel["to_id"] == str(audience_entity.id)
                for rel in self.graph.get_related(audience_entity.id)
            )
        )


if __name__ == "__main__":
    unittest.main()
