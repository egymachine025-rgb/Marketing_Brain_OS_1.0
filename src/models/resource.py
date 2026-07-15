from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from src.models.base import BaseModel, Currency

class ResourceType(str, Enum):
    HUMAN = "HUMAN"
    FINANCIAL = "FINANCIAL"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    SOFTWARE = "SOFTWARE"
    INTELLECTUAL = "INTELLECTUAL"

@dataclass
class Resource(BaseModel):
    name: str
    resource_type: ResourceType
    total_capacity: float
    allocated_units: float = 0.0
    monetary_cost_rate: float = 0.0
    currency: Currency = Currency.USD
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Resource name must be defined.")
        if self.total_capacity < 0.0:
            raise ValueError("Total resource capacity cannot fall below zero.")
        if self.allocated_units < 0.0 or self.allocated_units > self.total_capacity:
            raise ValueError("Allocated resource units must remain bound between 0.0 and total capacity.")
        if self.monetary_cost_rate < 0.0:
            raise ValueError("Monetary cost rate parameters must be non-negative values.")