import shutil
import unittest
import uuid
from pathlib import Path

from src.knowledge.decision_engine import DecisionEngine
from src.knowledge.decision_scorer import score_roi, score_risk, score_timing
from src.knowledge.knowledge_graph import KnowledgeGraph
from src.knowledge.knowledge_repository import KnowledgeRepository
from src.knowledge.knowledge_object import KnowledgeObject
from src.knowledge.reasoning_engine import ReasoningEngine


class TestDecisionEngine(unittest.TestCase):
    GRAPH_DIR = Path("data/tmp_decision_graph_test")
    REPO_DIR = Path("data/tmp_decision_repo_test")

    def setUp(self) -> None:
        for path in (self.GRAPH_DIR, self.REPO_DIR):
            if path.exists():
                shutil.rmtree(path)
            path.mkdir(parents=True, exist_ok=True)

        self.repository = KnowledgeRepository(data_dir=str(self.REPO_DIR))
        self.graph = KnowledgeGraph(data_dir=str(self.GRAPH_DIR))
        self.reasoning = ReasoningEngine(self.repository, self.graph)
        self.engine = DecisionEngine(self.reasoning, self.repository, self.graph)
        self.market = "Egypt"
        self.brand = "Nike"

    def tearDown(self) -> None:
        for path in (self.GRAPH_DIR, self.REPO_DIR):
            if path.exists():
                shutil.rmtree(path)

    def _save_brand_with_category(self, brand_name: str, market: str, categories: list[str]) -> KnowledgeObject:
        brand = self.repository.save(
            KnowledgeObject(
                type="brand",
                name=brand_name,
                value=brand_name,
                source="test",
                confidence=0.9,
                language="en",
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

    def test_evaluate_opportunities_ranking(self) -> None:
        self._save_brand_with_category("Nike", self.market, ["Shoes"])
        self._save_brand_with_category("Adidas", self.market, ["Shoes", "Running"])
        opportunities = self.engine.evaluate_opportunities(self.brand, self.market, budget=50000)
        self.assertIsInstance(opportunities, list)
        self.assertGreater(len(opportunities), 0)
        self.assertTrue(all("confidence" in opp for opp in opportunities))

    def test_decide_market_entry_go_no_go(self) -> None:
        self._save_brand_with_category("Nike", self.market, ["Shoes"])
        self._save_brand_with_category("Adidas", self.market, ["Shoes", "Running"])
        decision = self.engine.decide_market_entry(self.brand, "Saudi Arabia")
        self.assertIn(decision["decision"], {"GO", "NO-GO", "DEFER"})
        self.assertIn("confidence", decision)
        self.assertIn("projected_revenue_year_1", decision)

    def test_pricing_strategy_selection(self) -> None:
        self._save_brand_with_category("Nike", self.market, ["Shoes"])
        strategy = self.engine.decide_pricing_strategy(self.brand, "Shoes")
        self.assertIn(strategy["strategy"], {"premium_match", "undercut", "penetration"})
        self.assertIn("target_price_range", strategy)
        self.assertIn("justification", strategy)

    def test_launch_plan_generation(self) -> None:
        launch_plan = self.engine.decide_product_launch(self.brand, "Swimwear", self.market)
        self.assertEqual(launch_plan["brand"], self.brand)
        self.assertEqual(launch_plan["category"], "Swimwear")
        self.assertEqual(launch_plan["market"], self.market)
        self.assertEqual(len(launch_plan["phases"]), 3)

    def test_budget_allocation(self) -> None:
        allocation = self.engine.decide_marketing_spend(self.brand, "increase_share", 100000)
        self.assertEqual(allocation["allocation"]["social"], 40000.0)
        self.assertEqual(allocation["allocation"]["display"], 10000.0)
        self.assertEqual(allocation["confidence"], round(min(1.0, 0.6 + min(1.0, 100000.0 / 200000.0)), 4))

    def test_confidence_scoring(self) -> None:
        self.engine.evaluate_opportunities(self.brand, self.market, budget=50000)
        confidence = self.engine.get_decision_confidence("opp-Shoes")
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_decision_scorer_helpers(self) -> None:
        self.assertEqual(score_roi(30000, 10000), 2.0)
        self.assertEqual(score_risk(["a", "b"], 0.8), 0.6)
        self.assertEqual(score_timing(0.8, 0.2), 0.8)


if __name__ == "__main__":
    unittest.main()
