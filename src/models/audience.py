from __future__ import annotations
from dataclasses import dataclass, field
from src.models.base import BaseModel

@dataclass
class Audience(BaseModel):
    segment_name: str
    demographics: dict[str, Any] = field(default_factory=dict)
    psychographics: list[str] = field(default_factory=list)
    estimated_reach: int = 0

    def __post_init__(self) -> None:
        if not self.segment_name.strip():
            raise ValueError("Segment name cannot be empty.")
        if self.estimated_reach < 0:
            raise ValueError("Estimated reach metrics must be structural positive integers.")