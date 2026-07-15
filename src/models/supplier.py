from __future__ import annotations
from dataclasses import dataclass
from src.models.base import BaseModel

@dataclass
class Supplier(BaseModel):
    legal_name: str
    contact_email: str
    reliability_score: float = 1.0

    def __post_init__(self) -> None:
        if not self.legal_name.strip():
            raise ValueError("Supplier legal identity string name is mandatory.")
        if "@" not in self.contact_email:
            raise ValueError("Contact email must present standard structural routing patterns.")
        if not (0.0 <= self.reliability_score <= 1.0):
            raise ValueError("Reliability rating matrix constraint scales safely from 0.0 to 1.0.")