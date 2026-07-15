from __future__ import annotations
from dataclasses import dataclass, field
from src.models.base import BaseModel, Currency

@dataclass
class Market(BaseModel):
    region_code: str
    local_currency: Currency
    languages: list[str] = field(default_factory=list)
    market_size_estimate: float = 0.0

    def __post_init__(self) -> None:
        if not self.region_code.strip():
            raise ValueError("Region code must conform to non-empty string definitions.")
        if self.market_size_estimate < 0.0:
            raise ValueError("Market size estimate cannot drop below 0.0.")