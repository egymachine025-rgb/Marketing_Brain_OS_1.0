from __future__ import annotations
from dataclasses import dataclass, field
from src.models.base import BaseModel

@dataclass
class Analysis(BaseModel):
    analytical_scope: str
    structured_metrics: dict[str, float] = field(default_factory=dict)
    key_findings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.analytical_scope.strip():
            raise ValueError("Analytical scope verification tracking requires an explicit domain focus name.")