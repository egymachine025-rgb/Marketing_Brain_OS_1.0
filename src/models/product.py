from __future__ import annotations
from dataclasses import dataclass, field
from src.models.base import BaseModel, Currency

@dataclass
class Product(BaseModel):
    name: str
    sku: str
    base_price: float
    currency: Currency = Currency.USD
    attributes: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Product name cannot be empty or blank whitespace.")
        if not self.sku.strip():
            raise ValueError("SKU identification string is required.")
        if self.base_price < 0.0:
            raise ValueError("Base price cannot evaluate to a negative float value.")