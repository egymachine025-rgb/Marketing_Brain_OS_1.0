from __future__ import annotations

import uuid
from typing import Any

from contracts.decision_engine_contract import DecisionEngineContract
from src.knowledge.decision_scorer import score_roi, score_risk, score_timing
from src.knowledge.reasoning_engine import ReasoningEngine
from contracts.knowledge_repository_contract import KnowledgeRepositoryContract
from contracts.knowledge_graph_contract import KnowledgeGraphContract


class DecisionEngine(DecisionEngineContract):
    """
    Decision engine that turns reasoning insights into prioritized actionable plans.
    """

    def __init__(
        self,
        reasoning_engine: ReasoningEngine,
        repository: KnowledgeRepositoryContract,
        graph: KnowledgeGraphContract,
    ) -> None:
        self.reasoning_engine = reasoning_engine
        self.repository = repository
        self.graph = graph
        self._decision_confidence: dict[str, float] = {}

    def evaluate_opportunities(
        self,
        brand: str,
        market: str,
        budget: float | None = None,
    ) -> list[dict[str, Any]]:
        budget = budget or 100000.0
        gaps = self.reasoning_engine.infer_market_gaps(market)
        landscape = self.reasoning_engine.infer_competitive_landscape(brand, market)

        ranked: list[dict[str, Any]] = []
        for gap in gaps:
            base_score = gap["opportunity_score"] * (1.0 / (gap["competitor_count"] + 1))
            investment_required = min(budget, 15000.0 * (gap["competitor_count"] + 1))
            roi_value = score_roi(expected_revenue=investment_required * 3.0, investment=investment_required)
            confidence = round(min(1.0, base_score * 0.9 + roi_value * 0.1), 4)
            ranked.append(
                {
                    "opportunity": gap["category"],
                    "action": "launch_product_line",
                    "expected_roi": roi_value,
                    "investment_required": investment_required,
                    "timeline_months": 3,
                    "confidence": confidence,
                    "risks": ["seasonal_demand", "supplier_availability"],
                    "rationale": f"Only {gap['competitor_count']} competitor(s) in {gap['category']}, brand positioning is favorable.",
                }
            )
            self._decision_confidence[f"opp-{gap['category']}"] = confidence

        if not ranked:
            fallback_investment = min(budget, 10000.0)
            fallback_roi = score_roi(expected_revenue=fallback_investment * 2.0, investment=fallback_investment)
            ranked.append(
                {
                    "opportunity": "core_brand_presence",
                    "action": "strengthen_brand_presence",
                    "expected_roi": fallback_roi,
                    "investment_required": fallback_investment,
                    "timeline_months": 4,
                    "confidence": 0.5,
                    "risks": ["market_awareness", "execution_delay"],
                    "rationale": "No clear market gaps detected, so prioritize brand presence and awareness growth.",
                }
            )
            self._decision_confidence["opp-core_brand_presence"] = 0.5

        return sorted(ranked, key=lambda item: item["confidence"], reverse=True)

    def decide_market_entry(self, brand: str, target_market: str) -> dict[str, Any]:
        landscape = self.reasoning_engine.infer_competitive_landscape(brand, target_market)
        competitor_count = len(landscape["competitors"])
        unique_categories = len(landscape["unique_categories"])
        in_market = any(brand == market_brand["name"] for market_brand in landscape["competitors"])

        decision = "DEFER"
        if competitor_count < 3 and unique_categories >= 1 and not in_market:
            decision = "GO"
        elif competitor_count >= 5:
            decision = "NO-GO"

        confidence = round(min(1.0, 0.6 + unique_categories * 0.08 - competitor_count * 0.05), 4)
        self._decision_confidence[f"market-entry-{brand}-{target_market}"] = confidence

        return {
            "decision": decision,
            "confidence": confidence,
            "conditions": ["partner_with_local_distributor", "price_10_percent_below_Adidas"],
            "risks": ["high_competition", "logistics_cost"],
            "projected_revenue_year_1": 250000.0 if decision == "GO" else 0.0,
            "break_even_months": 8 if decision == "GO" else 0.0,
        }

    def decide_pricing_strategy(self, brand: str, product_category: str) -> dict[str, Any]:
        positioning = self.reasoning_engine.infer_price_positioning(brand)
        margin = positioning["vs_competitors"].get("Adidas", 0.0)
        strategy = "premium_match"
        target_price_range = [0.0, 0.0]

        if positioning["tier"] == "high":
            strategy = "premium_match"
            target_price_range = [positioning["avg_price"] * 0.95, positioning["avg_price"] * 1.1]
        elif positioning["tier"] == "mid":
            strategy = "undercut"
            target_price_range = [positioning["avg_price"] * 0.9, positioning["avg_price"] * 0.98]
        else:
            strategy = "penetration"
            target_price_range = [positioning["avg_price"] * 0.8, positioning["avg_price"] * 0.95]

        expected_volume_impact = "-5%" if strategy == "premium_match" else "+10%"
        expected_margin_impact = "+18%" if strategy == "premium_match" else "+10%"
        confidence = round(min(1.0, 0.7 + abs(margin) * 0.01), 4)
        self._decision_confidence[f"pricing-{brand}-{product_category}"] = confidence

        return {
            "strategy": strategy,
            "target_price_range": [round(target_price_range[0], 2), round(target_price_range[1], 2)],
            "vs_market_median": f"{margin:+.0f}%",
            "justification": "Brand equity supports premium." if strategy == "premium_match" else "Price positioning supports category entry.",
            "expected_volume_impact": expected_volume_impact,
            "expected_margin_impact": expected_margin_impact,
        }

    def decide_product_launch(self, brand: str, category: str, market: str) -> dict[str, Any]:
        decision_id = f"launch-{brand}-{category}-{market}"
        confidence = round(min(1.0, 0.7 + len(category) * 0.01), 4)
        self._decision_confidence[decision_id] = confidence

        return {
            "brand": brand,
            "category": category,
            "market": market,
            "phases": [
                {"phase": "test", "months": [1, 2], "units": 500, "price": 45.0},
                {"phase": "scale", "months": [3, 6], "units": 2000, "price": 55.0},
                {"phase": "market", "months": [7, 12], "units": 5000, "price": 65.0},
            ],
            "channels": ["social", "influencer", "search"],
            "success_metrics": ["sell_through", "customer_acquisition_cost", "market_share"],
            "confidence": confidence,
        }

    def decide_marketing_spend(self, brand: str, goal: str, budget: float) -> dict[str, Any]:
        allocation = {
            "social": round(budget * 0.4, 2),
            "influencer": round(budget * 0.3, 2),
            "search": round(budget * 0.2, 2),
            "display": round(budget * 0.1, 2),
        }
        decision_id = f"marketing-{brand}-{goal}" 
        confidence = round(min(1.0, 0.6 + min(1.0, budget / 200000.0)), 4)
        self._decision_confidence[decision_id] = confidence

        return {
            "brand": brand,
            "goal": goal,
            "budget": budget,
            "allocation": allocation,
            "expected_kpis": {
                "reach": int(budget * 20),
                "engagement_rate": "3%",
                "lead_conversion": "1.2%",
            },
            "confidence": confidence,
        }

    def get_decision_confidence(self, decision_id: str) -> float:
        return self._decision_confidence.get(decision_id, 0.0)
