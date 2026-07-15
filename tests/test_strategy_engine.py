import shutil
import unittest
from pathlib import Path

from src.knowledge.decision_engine import DecisionEngine
from src.knowledge.knowledge_graph import KnowledgeGraph
from src.knowledge.knowledge_repository import KnowledgeRepository
from src.knowledge.reasoning_engine import ReasoningEngine
from src.knowledge.strategy_engine import StrategyEngine
from src.knowledge.knowledge_object import KnowledgeObject


class TestStrategyEngine(unittest.TestCase):
    GRAPH_DIR = Path("data/tmp_strategy_graph_test")
    REPO_DIR = Path("data/tmp_strategy_repo_test")

    def setUp(self) -> None:
        for path in (self.GRAPH_DIR, self.REPO_DIR):
            if path.exists():
                shutil.rmtree(path)
            path.mkdir(parents=True, exist_ok=True)

        self.repository = KnowledgeRepository(data_dir=str(self.REPO_DIR))
        self.graph = KnowledgeGraph(data_dir=str(self.GRAPH_DIR))
        self.reasoning = ReasoningEngine(self.repository, self.graph)
        self.decision_engine = DecisionEngine(self.reasoning, self.repository, self.graph)
        self.engine = StrategyEngine(self.decision_engine, self.reasoning, self.graph)

        self.brand = "Nike"
        self.market = "Egypt"
        self._seed_market_data()

    def tearDown(self) -> None:
        for path in (self.GRAPH_DIR, self.REPO_DIR):
            if path.exists():
                shutil.rmtree(path)

    def _seed_market_data(self) -> None:
        brand = self.repository.save(
            KnowledgeObject(
                type="brand",
                name="Nike",
                value="Nike",
                source="test",
                confidence=0.9,
                language="en",
            )
        )
        market = self.repository.save(
            KnowledgeObject(
                type="market",
                name="Egypt",
                value="Egypt",
                source="test",
                confidence=0.9,
                language="en",
            )
        )
        self.graph.add_relationship(brand.id, market.id, "has_market")

    def test_generate_strategy(self) -> None:
        strategy = self.engine.generate_strategy(self.brand, "increase_market_share", self.market, 500000, 12)
        self.assertEqual(strategy["brand"], self.brand)
        self.assertEqual(strategy["goal"], "increase_market_share")
        self.assertEqual(strategy["market"], self.market)
        self.assertEqual(len(strategy["phases"]), 3)
        self.assertIn("strategy_id", strategy)
        self.assertGreater(strategy["total_expected_roi"], 0)

    def test_generate_launch_plan(self) -> None:
        decision = {"investment_required": 20000}
        launch_plan = self.engine.generate_launch_plan("Nike Swimwear", self.market, decision)
        self.assertEqual(launch_plan["product"], "Nike Swimwear")
        self.assertEqual(launch_plan["market"], self.market)
        self.assertEqual(len(launch_plan["phases"]), 3)
        self.assertTrue(any(phase["name"] == "Launch" for phase in launch_plan["phases"]))

    def test_generate_marketing_campaign(self) -> None:
        campaign = self.engine.generate_marketing_campaign(self.brand, "brand_awareness", 100000, ["social", "influencer", "search"])
        self.assertEqual(campaign["brand"], self.brand)
        self.assertEqual(campaign["goal"], "brand_awareness")
        self.assertEqual(campaign["allocation"]["social"], 40000.0)
        self.assertIn("expected_kpis", campaign)

    def test_generate_pricing_schedule(self) -> None:
        schedule = self.engine.generate_pricing_schedule(self.brand, "Shoes", "premium_match")
        self.assertEqual(schedule["strategy"], "premium_match")
        self.assertTrue(all(tier["price"] > 0 for tier in schedule["price_tiers"]))
        self.assertTrue(any(rule["event"] == "Black Friday" for rule in schedule["promotional_calendar"]))

    def test_generate_expansion_roadmap(self) -> None:
        roadmap = self.engine.generate_expansion_roadmap(self.brand, [self.market], ["Saudi Arabia", "UAE", "Kuwait"])
        self.assertEqual(roadmap["brand"], self.brand)
        self.assertEqual(len(roadmap["roadmap"]), 3)
        self.assertEqual(roadmap["roadmap"][0]["priority"], 1)
        self.assertIn(roadmap["roadmap"][0]["entry_mode"], {"partner", "direct", "franchise"})

    def test_milestone_timeline_generation(self) -> None:
        strategy = self.engine.generate_strategy(self.brand, "increase_market_share", self.market, 500000, 12)
        timeline = self.engine.get_milestone_timeline(strategy["strategy_id"])
        self.assertTrue(len(timeline) > 0)
        self.assertIn("action", timeline[0])

    def test_kpi_calculation(self) -> None:
        strategy = self.engine.generate_strategy(self.brand, "increase_market_share", self.market, 500000, 12)
        kpis = self.engine.calculate_kpis(strategy)
        self.assertIn("total_revenue_target", kpis)
        self.assertIn("expected_roi", kpis)
        self.assertIn("risk_adjusted_projection", kpis)
        self.assertGreaterEqual(kpis["risk_adjusted_projection"], 0)


if __name__ == "__main__":
    unittest.main()
