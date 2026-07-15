from __future__ import annotations
from dataclasses import dataclass, field
from src.models.base import BaseModel

@dataclass
class Mission(BaseModel):
    statement: str
    vision: str
    core_values: list[str] = field(default_factory=list)
    strategic_focus_areas: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("Mission statement cannot be empty or whitespace.")
        if not self.vision.strip():
            raise ValueError("Vision statement must possess structural direction.")