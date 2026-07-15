from __future__ import annotations
from typing import Protocol, Any


class StrategyEngineContract(Protocol):
    """
    Contract defining the interface for the strategy engine.
    """

    def generate_strategy(
        self,
        brand: str,
        goal: str,
        market: str,
        budget: float,
        timeline_months: int = 12,
    ) -> dict[str, Any]:
        ...

    def generate_launch_plan(
        self,
        product: str,
        market: str,
        decision: dict[str, Any],
    ) -> dict[str, Any]:
        ...

    def generate_marketing_campaign(
        self,
        brand: str,
        goal: str,
        budget: float,
        channels: list[str],
    ) -> dict[str, Any]:
        ...

    def generate_pricing_schedule(
        self,
        brand: str,
        category: str,
        strategy: str,
    ) -> dict[str, Any]:
        ...

    def generate_expansion_roadmap(
        self,
        brand: str,
        current_markets: list[str],
        target_markets: list[str],
    ) -> dict[str, Any]:
        ...

    def get_milestone_timeline(self, strategy_id: str) -> list[dict[str, Any]]:
        ...

    def calculate_kpis(self, strategy: dict[str, Any]) -> dict[str, Any]:
        ...
