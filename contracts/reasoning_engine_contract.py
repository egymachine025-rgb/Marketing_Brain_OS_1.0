from __future__ import annotations
from typing import Protocol, Any


class ReasoningEngineContract(Protocol):
    """
    Contract defining the inference interface for the reasoning engine.
    """

    def infer_competitive_landscape(self, brand_name: str, market: str | None = None) -> dict[str, Any]:
        ...

    def infer_market_gaps(self, market_name: str) -> list[dict[str, Any]]:
        ...

    def infer_audience_overlap(self, brand_a: str, brand_b: str) -> dict[str, Any]:
        ...

    def infer_price_positioning(self, product_or_brand: str) -> dict[str, Any]:
        ...

    def infer_trending_categories(self, market: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
        ...

    def infer_recommendations(self, target_brand: str, goal: str) -> list[dict[str, Any]]:
        ...
