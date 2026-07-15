from __future__ import annotations
from typing import Protocol, Any


class DecisionEngineContract(Protocol):
    """
    Contract defining the interface for the decision engine.
    """

    def evaluate_opportunities(
        self,
        brand: str,
        market: str,
        budget: float | None = None,
    ) -> list[dict[str, Any]]:
        ...

    def decide_market_entry(
        self,
        brand: str,
        target_market: str,
    ) -> dict[str, Any]:
        ...

    def decide_pricing_strategy(
        self,
        brand: str,
        product_category: str,
    ) -> dict[str, Any]:
        ...

    def decide_product_launch(
        self,
        brand: str,
        category: str,
        market: str,
    ) -> dict[str, Any]:
        ...

    def decide_marketing_spend(
        self,
        brand: str,
        goal: str,
        budget: float,
    ) -> dict[str, Any]:
        ...

    def get_decision_confidence(self, decision_id: str) -> float:
        ...
