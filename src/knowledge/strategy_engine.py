from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from contracts.decision_engine_contract import DecisionEngineContract
from contracts.strategy_engine_contract import StrategyEngineContract
from contracts.knowledge_graph_contract import KnowledgeGraphContract
from src.knowledge.reasoning_engine import ReasoningEngine
from src.knowledge.strategy_templates import get_template


class StrategyEngine(StrategyEngineContract):
    """
    Strategy engine that turns decision outputs into full business strategy plans.
    """

    def __init__(
        self,
        decision_engine: DecisionEngineContract,
        reasoning_engine: ReasoningEngine,
        graph: KnowledgeGraphContract,
    ) -> None:
        self.decision_engine = decision_engine
        self.reasoning_engine = reasoning_engine
        self.graph = graph
        self._strategies: dict[str, dict[str, Any]] = {}

    def generate_strategy(
        self,
        brand: str,
        goal: str,
        market: str,
        budget: float,
        timeline_months: int = 12,
    ) -> dict[str, Any]:
        opportunities = self.decision_engine.evaluate_opportunities(brand, market, budget)
        top_opportunities = opportunities[:3]
        template = get_template("market_development")
        primary_opportunity = top_opportunities[0]["opportunity"] if top_opportunities else "core_product"

        phases = [
            {
                "phase": 1,
                "name": "Foundation",
                "months": "1-3",
                "focus": "product_line_expansion",
                "actions": [
                    {
                        "action": f"launch_{primary_opportunity.lower().replace(' ', '_')}_line",
                        "budget": round(budget * 0.16, 2),
                        "owner": "Product Team",
                    },
                    {
                        "action": "partner_local_retailers",
                        "budget": round(budget * 0.08, 2),
                        "owner": "BD Team",
                    },
                ],
                "deliverables": [
                    f"{primary_opportunity}_catalog_20_items",
                    "5_local_partnerships",
                ],
                "kpis": {"products_live": 20, "partnerships_signed": 5},
            },
            {
                "phase": 2,
                "name": "Growth",
                "months": "4-8",
                "focus": "marketing_scale",
                "actions": [
                    {
                        "action": "launch_digital_brand_campaign",
                        "budget": round(budget * 0.24, 2),
                        "owner": "Marketing Team",
                    },
                    {
                        "action": "expand_distribution_network",
                        "budget": round(budget * 0.12, 2),
                        "owner": "Operations Team",
                    },
                ],
                "deliverables": ["200k_impressions", "10k_new_customers"],
                "kpis": {"revenue": round(budget * 0.4, 2), "market_share": 0.15},
            },
            {
                "phase": 3,
                "name": "Optimization",
                "months": "9-12",
                "focus": "profitability",
                "actions": [
                    {
                        "action": "implement_loyalty_program",
                        "budget": round(budget * 0.1, 2),
                        "owner": "CRM Team",
                    },
                    {
                        "action": "refine_promotional_calendar",
                        "budget": round(budget * 0.06, 2),
                        "owner": "Sales Team",
                    },
                ],
                "deliverables": ["customer_retention_plan", "margin_expansion_report"],
                "kpis": {"roi": 2.5, "customer_retention": 0.65},
            },
        ]

        total_expected_roi = round(
            sum(item["expected_roi"] for item in top_opportunities) / max(1, len(top_opportunities)),
            2,
        )
        strategy_id = str(uuid.uuid4())
        strategy = {
            "strategy_id": strategy_id,
            "brand": brand,
            "goal": goal,
            "market": market,
            "budget": budget,
            "timeline_months": timeline_months,
            "template": template,
            "phases": phases,
            "total_expected_roi": total_expected_roi,
            "risk_mitigation": [
                {
                    "risk": "seasonal_demand",
                    "mitigation": "launch_pre_summer",
                    "contingency_budget": round(budget * 0.05, 2),
                }
            ],
            "success_criteria": {
                "revenue_target": round(budget * 1.2, 2),
                "market_share_target": 0.18,
                "brand_awareness_target": 0.45,
            },
        }
        self._strategies[strategy_id] = strategy
        return strategy

    def generate_launch_plan(
        self,
        product: str,
        market: str,
        decision: dict[str, Any],
    ) -> dict[str, Any]:
        timeline_id = str(uuid.uuid4())
        plan = {
            "launch_id": timeline_id,
            "product": product,
            "market": market,
            "decision_basis": decision,
            "phases": [
                {
                    "name": "Pre-launch",
                    "months": "-2 to 0",
                    "budget": round(decision.get("investment_required", 10000) * 0.25, 2),
                    "channels": ["sampling", "influencer_seeding"],
                    "content_types": ["teaser_video", "sampling_kits"],
                    "success_metrics": ["prelaunch_signups", "influencer_engagement"],
                },
                {
                    "name": "Launch",
                    "months": "0",
                    "budget": round(decision.get("investment_required", 10000) * 0.35, 2),
                    "channels": ["event", "PR", "digital_blast"],
                    "content_types": ["launch_video", "press_release"],
                    "success_metrics": ["launch_attendance", "coverage_reach"],
                },
                {
                    "name": "Post-launch",
                    "months": "1-3",
                    "budget": round(decision.get("investment_required", 10000) * 0.4, 2),
                    "channels": ["performance_marketing", "retargeting"],
                    "content_types": ["social_ads", "email_sequence"],
                    "success_metrics": ["conversion_rate", "repeat_purchase"],
                },
            ],
        }
        return plan

    def generate_marketing_campaign(
        self,
        brand: str,
        goal: str,
        budget: float,
        channels: list[str],
    ) -> dict[str, Any]:
        allocation = {
            "social": round(budget * 0.4, 2),
            "influencer": round(budget * 0.3, 2),
            "search": round(budget * 0.2, 2),
            "display": round(budget * 0.1, 2),
        }
        campaign = {
            "brand": brand,
            "goal": goal,
            "budget": budget,
            "allocation": {channel: allocation.get(channel, 0.0) for channel in channels},
            "content_calendar": [
                {"week": 1, "theme": "brand_story"},
                {"week": 2, "theme": "product_benefits"},
                {"week": 3, "theme": "social_proof"},
                {"week": 4, "theme": "conversion"},
            ],
            "audience_targeting": {
                "social": ["18-35", "sports_enthusiasts"],
                "influencer": ["fashion_seekers", "fitness_enthusiasts"],
                "search": ["purchase_intent"],
            },
            "ab_test_plan": [
                {"channel": "social", "variant_a": "video", "variant_b": "carousel"},
                {"channel": "search", "variant_a": "headline_a", "variant_b": "headline_b"},
            ],
            "expected_kpis": {
                "social": {"cac": 12.0, "ctr": 0.035, "conversion": 0.012},
                "influencer": {"cac": 18.0, "ctr": 0.028, "conversion": 0.010},
                "search": {"cac": 10.0, "ctr": 0.045, "conversion": 0.015},
            },
        }
        return campaign

    def generate_pricing_schedule(
        self,
        brand: str,
        category: str,
        strategy: str,
    ) -> dict[str, Any]:
        base_price = 100.0
        schedule = {
            "brand": brand,
            "category": category,
            "strategy": strategy,
            "price_tiers": [],
            "promotional_calendar": [
                {"event": "Black Friday", "discount": "15%"},
                {"event": "Ramadan", "discount": "10%"},
                {"event": "Year End", "discount": "12%"},
            ],
            "discount_rules": {
                "early_bird": "5% off for first 100 units",
                "bundle": "10% off on 2+ SKUs",
            },
            "competitive_triggers": [
                "match_competitor_promotion",
                "activate_retention_offer_if_discount_exceeds_15%",
            ],
        }

        if strategy == "premium_match":
            schedule["price_tiers"] = [
                {"tier": "entry", "price": base_price * 1.05},
                {"tier": "core", "price": base_price * 1.2},
                {"tier": "premium", "price": base_price * 1.4},
            ]
        elif strategy == "undercut":
            schedule["price_tiers"] = [
                {"tier": "entry", "price": base_price * 0.9},
                {"tier": "core", "price": base_price * 1.0},
                {"tier": "premium", "price": base_price * 1.15},
            ]
        elif strategy == "penetration":
            schedule["price_tiers"] = [
                {"tier": "entry", "price": base_price * 0.8},
                {"tier": "core", "price": base_price * 0.9},
                {"tier": "premium", "price": base_price * 1.05},
            ]
        else:
            schedule["price_tiers"] = [
                {"tier": "entry", "price": base_price},
                {"tier": "core", "price": base_price * 1.1},
                {"tier": "premium", "price": base_price * 1.25},
            ]

        schedule["price_tiers"] = [
            {**tier, "price": round(tier["price"], 2)} for tier in schedule["price_tiers"]
        ]
        return schedule

    def generate_expansion_roadmap(
        self,
        brand: str,
        current_markets: list[str],
        target_markets: list[str],
    ) -> dict[str, Any]:
        scores: list[tuple[str, float]] = []
        for market in target_markets:
            market_size = self._market_size_score(market)
            competition_density = self._competition_density_score(market)
            logistics_ease = self._logistics_score(market)
            recognition = self._brand_recognition_score(brand, market)
            score = market_size * 0.4 + (1.0 - competition_density) * 0.25 + logistics_ease * 0.2 + recognition * 0.15
            scores.append((market, round(score, 4)))

        roadmap = []
        for ranking, (market, score) in enumerate(sorted(scores, key=lambda item: item[1], reverse=True), start=1):
            roadmap.append(
                {
                    "market": market,
                    "priority": ranking,
                    "entry_mode": self._entry_mode_for_market(market),
                    "estimated_timeline_months": 6 + ranking * 2,
                    "dependencies": [m for m in current_markets if m != market][:1],
                }
            )

        return {
            "brand": brand,
            "current_markets": current_markets,
            "target_markets": target_markets,
            "roadmap": roadmap,
        }

    def get_milestone_timeline(self, strategy_id: str) -> list[dict[str, Any]]:
        strategy = self._strategies.get(strategy_id, {})
        milestones = []
        if not strategy:
            return milestones

        for phase in strategy.get("phases", []):
            for idx, action in enumerate(phase.get("actions", []), start=1):
                milestones.append(
                    {
                        "strategy_id": strategy_id,
                        "phase": phase["name"],
                        "action": action["action"],
                        "month_window": phase["months"],
                        "owner": action["owner"],
                        "dependency": phase["name"] if idx > 1 else None,
                        "gate": "go/no-go" if idx == 1 else "review",
                    }
                )
        return milestones

    def calculate_kpis(self, strategy: dict[str, Any]) -> dict[str, Any]:
        aggregated: dict[str, Any] = {
            "total_revenue_target": strategy.get("success_criteria", {}).get("revenue_target", 0.0),
            "expected_roi": strategy.get("total_expected_roi", 0.0),
            "market_share_target": strategy.get("success_criteria", {}).get("market_share_target", 0.0),
            "brand_awareness_target": strategy.get("success_criteria", {}).get("brand_awareness_target", 0.0),
            "leading_indicators": {},
        }

        leading: dict[str, float] = {}
        for phase in strategy.get("phases", []):
            for kpi, value in phase.get("kpis", {}).items():
                if isinstance(value, (int, float)):
                    leading[kpi] = leading.get(kpi, 0.0) + float(value)

        aggregated["leading_indicators"] = {
            "expected_products_live": leading.get("products_live", 0.0),
            "expected_partnerships": leading.get("partnerships_signed", 0.0),
            "expected_revenue": leading.get("revenue", 0.0),
        }
        aggregated["risk_adjusted_projection"] = round(aggregated["expected_roi"] * 0.9, 2)
        return aggregated

    def _market_size_score(self, market: str) -> float:
        mapping = {"Saudi Arabia": 0.9, "UAE": 0.75, "Kuwait": 0.65, "Egypt": 0.8}
        return mapping.get(market, 0.5)

    def _competition_density_score(self, market: str) -> float:
        mapping = {"Saudi Arabia": 0.7, "UAE": 0.6, "Kuwait": 0.55, "Egypt": 0.8}
        return mapping.get(market, 0.6)

    def _logistics_score(self, market: str) -> float:
        mapping = {"Saudi Arabia": 0.7, "UAE": 0.8, "Kuwait": 0.75, "Egypt": 0.6}
        return mapping.get(market, 0.5)

    def _brand_recognition_score(self, brand: str, market: str) -> float:
        if market == "Egypt":
            return 0.85
        return 0.6

    def _entry_mode_for_market(self, market: str) -> str:
        if market in {"Saudi Arabia", "UAE"}:
            return "partner"
        if market == "Kuwait":
            return "direct"
        return "franchise"
