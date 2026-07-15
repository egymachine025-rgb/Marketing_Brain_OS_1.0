from __future__ import annotations

import statistics
from typing import Any

from contracts.reasoning_engine_contract import ReasoningEngineContract
from contracts.knowledge_graph_contract import KnowledgeGraphContract
from contracts.knowledge_repository_contract import KnowledgeRepositoryContract
from src.knowledge.inference_rules import (
    rule_competitive_threat,
    rule_market_opportunity,
    rule_price_tier,
)
from src.knowledge.knowledge_object import KnowledgeObject


class ReasoningEngine(ReasoningEngineContract):
    """
    Reasoning engine that infers marketing insights from a knowledge graph and repository.
    """

    def __init__(
        self,
        repository: KnowledgeRepositoryContract,
        graph: KnowledgeGraphContract,
    ) -> None:
        self.repository = repository
        self.graph = graph

    def infer_competitive_landscape(self, brand_name: str, market: str | None = None) -> dict[str, Any]:
        brand = self.repository.get_by_type_and_name("brand", brand_name, "en")
        if brand is None:
            return {
                "brand": brand_name,
                "market": market,
                "competitors": [],
                "unique_categories": [],
                "threat_level": "unknown",
            }

        market_brands = self._brands_in_market(market) if market else self._all_brands()
        target_categories = self._categories_for_entity(brand.id)
        competitors: list[dict[str, Any]] = []

        all_competitor_categories: list[str] = []
        threat_scores: list[float] = []

        for competitor in market_brands:
            if competitor.id == brand.id:
                continue
            competitor_categories = self._categories_for_entity(competitor.id)
            shared_categories = self._shared_categories(brand.id, competitor.id)
            all_competitor_categories.extend(competitor_categories)
            competitor_products = self.repository.get_linked_products(competitor.id)
            market_share_estimate = round(len(competitor_products) / max(1, len(competitor_products) + 1), 4)
            if competitor_categories:
                threat_scores.append(len(shared_categories) / len(competitor_categories))
            competitors.append(
                {
                    "name": competitor.name,
                    "shared_categories": sorted(shared_categories),
                    "market_share_estimate": market_share_estimate,
                }
            )

        unique_categories = sorted(set(all_competitor_categories) - set(target_categories))
        threat_level = rule_competitive_threat(
            shared_categories=int(round(max(threat_scores, default=0.0) * max(1, len(target_categories)))),
            total_categories=max(1, len(target_categories)),
        )

        return {
            "brand": brand_name,
            "market": market,
            "competitors": sorted(competitors, key=lambda item: item["market_share_estimate"], reverse=True),
            "unique_categories": unique_categories,
            "threat_level": threat_level,
        }

    def infer_market_gaps(self, market_name: str) -> list[dict[str, Any]]:
        market_brands = self._brands_in_market(market_name)
        category_counts: dict[str, set[str]] = {}

        for brand in market_brands:
            for category in self._categories_for_entity(brand.id):
                category_counts.setdefault(category, set()).add(brand.id)

        opportunities: list[dict[str, Any]] = []
        for category, brands in category_counts.items():
            competitor_count = len(brands)
            if competitor_count < 3:
                score = rule_market_opportunity(competitor_count, category_demand=0.9)
                opportunities.append(
                    {
                        "category": category,
                        "competitor_count": competitor_count,
                        "opportunity_score": score,
                    }
                )

        return sorted(opportunities, key=lambda row: row["opportunity_score"], reverse=True)

    def infer_audience_overlap(self, brand_a: str, brand_b: str) -> dict[str, Any]:
        entity_a = self.repository.get_by_type_and_name("brand", brand_a, "en")
        entity_b = self.repository.get_by_type_and_name("brand", brand_b, "en")

        if not entity_a or not entity_b:
            return {
                "shared_audiences": [],
                "overlap_score": 0.0,
                "unique_to_a": [],
                "unique_to_b": [],
            }

        audiences_a = self._audiences_for_entity(entity_a.id)
        audiences_b = self._audiences_for_entity(entity_b.id)
        shared = sorted(audiences_a & audiences_b)
        union = audiences_a | audiences_b
        overlap_score = round(len(shared) / max(1, len(union)), 4)

        return {
            "shared_audiences": shared,
            "overlap_score": overlap_score,
            "unique_to_a": sorted(audiences_a - audiences_b),
            "unique_to_b": sorted(audiences_b - audiences_a),
        }

    def infer_price_positioning(self, product_or_brand: str) -> dict[str, Any]:
        target = self.repository.get_by_type_and_name("brand", product_or_brand, "en")
        if target is None:
            return {
                "tier": "unknown",
                "avg_price": 0.0,
                "vs_competitors": {},
                "price_range": "unknown",
            }

        target_products = self._products_for_entity(target.id)
        prices = [p.get("price", 0.0) for p in target_products if isinstance(p.get("price"), (int, float))]

        if not prices:
            return {
                "tier": "unknown",
                "avg_price": 0.0,
                "vs_competitors": {},
                "price_range": "unknown",
            }

        avg_price = round(statistics.mean(prices), 2)
        median_price = round(statistics.median(prices), 2)
        comps = self._competitor_prices_for_entity(target.id)
        vs_competitors = {}

        for name, comp_prices in comps.items():
            if not comp_prices:
                continue
            comp_avg = statistics.mean(comp_prices)
            vs_competitors[name] = round((avg_price / comp_avg - 1.0) * 100.0, 2)

        price_range = self._describe_price_range(avg_price, median_price)
        tier = rule_price_tier(avg_price, median_price)

        return {
            "tier": tier,
            "avg_price": avg_price,
            "vs_competitors": vs_competitors,
            "price_range": price_range,
        }

    def infer_trending_categories(self, market: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
        category_counts: dict[str, int] = {}

        for brand in self._brands_in_market(market) if market else self._all_brands():
            for category in self._categories_for_entity(brand.id):
                category_counts[category] = category_counts.get(category, 0) + 1

        ranked = sorted(category_counts.items(), key=lambda item: item[1], reverse=True)
        return [
            {"category": category, "momentum_score": round(count / max(1, ranked[0][1]), 4)}
            for category, count in ranked[:limit]
        ]

    def infer_recommendations(self, target_brand: str, goal: str) -> list[dict[str, Any]]:
        brand = self.repository.get_by_type_and_name("brand", target_brand, "en")
        if brand is None:
            return []

        market_gaps = self.infer_market_gaps(goal if goal.startswith("market:") else "Egypt")
        categories = [gap["category"] for gap in market_gaps[:3]]
        opportunities = []

        if categories:
            opportunities.append(
                {
                    "strategy": f"enter_{categories[0].lower().replace(' ', '_')}",
                    "confidence": round(market_gaps[0]["opportunity_score"] if market_gaps else 0.5, 4),
                    "rationale": f"Only {market_gaps[0]['competitor_count']} competitor(s) in {market_gaps[0]['category']}.",
                }
            )

        audiences = sorted(self._audiences_for_entity(brand.id))
        if audiences:
            opportunities.append(
                {
                    "strategy": "target_shared_audiences",
                    "confidence": 0.7,
                    "rationale": f"Focus on {', '.join(audiences[:2])} audiences already connected to the brand.",
                }
            )

        return opportunities

    def _brands_in_market(self, market: str | None) -> list[KnowledgeObject]:
        if market is None:
            return self._all_brands()

        market_node = self.repository.get_by_type_and_name("market", market, "en")
        if market_node is None:
            return []

        return [
            self.repository.get_by_id(rel["from_id"])
            for rel in self.graph.get_related(market_node.id, relation_type="has_market")
            if self.repository.get_by_id(rel["from_id"]) is not None
        ]

    def _all_brands(self) -> list[KnowledgeObject]:
        return self.repository.get_by_type("brand", "en")

    def _categories_for_entity(self, entity_id: str) -> list[str]:
        return [
            self.repository.get_by_id(rel["to_id"]).name
            for rel in self.graph.get_relationships(entity_id, relation_type="has_category")
            if self.repository.get_by_id(rel["to_id"]) is not None
        ]

    def _shared_categories(self, entity_a: str, entity_b: str) -> list[str]:
        return list(
            set(self._categories_for_entity(entity_a)) & set(self._categories_for_entity(entity_b))
        )

    def _audiences_for_entity(self, entity_id: str) -> set[str]:
        return {
            self.repository.get_by_id(rel["to_id"]).name
            for rel in self.graph.get_relationships(entity_id, relation_type="has_audience")
            if self.repository.get_by_id(rel["to_id"]) is not None
        }

    def _products_for_entity(self, entity_id: str) -> list[dict[str, Any]]:
        product_nodes = self.repository.find_by_metadata("brand", self.repository.get_by_id(entity_id).name) if self.repository.get_by_id(entity_id) else []
        return [node.metadata for node in product_nodes]

    def _competitor_prices_for_entity(self, entity_id: str) -> dict[str, list[float]]:
        competitor_prices: dict[str, list[float]] = {}
        categories = self._categories_for_entity(entity_id)
        for brand in self._all_brands():
            if brand.id == entity_id:
                continue
            if set(categories) & set(self._categories_for_entity(brand.id)):
                prices = [p.get("price", 0.0) for p in self._products_for_entity(brand.id) if isinstance(p.get("price"), (int, float))]
                competitor_prices[brand.name] = prices
        return competitor_prices

    def _describe_price_range(self, avg_price: float, median_price: float) -> str:
        if avg_price >= median_price * 1.25:
            return "high"
        if avg_price <= median_price * 0.85:
            return "low"
        return "mid"
