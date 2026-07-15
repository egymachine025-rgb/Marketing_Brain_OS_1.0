from __future__ import annotations
from dataclasses import dataclass, field
from src.models.base import BaseModel

@dataclass
class Competitor(BaseModel):
    brand_name: str
    market_share_percentage: float
    tracked_product_skus: list[str] = field(default_factory=list)
    perceived_strengths: list[str] = field(default_factory=list)
    perceived_weaknesses: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.brand_name.strip():
            raise ValueError("Competitor brand name must be populated.")
        if not (0.0 <= self.market_share_percentage <= 100.0):
            raise ValueError("Market share percentage bound context must rest between 0.0 and 100.0.")