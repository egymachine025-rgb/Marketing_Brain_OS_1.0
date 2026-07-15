from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from src.models.base import BaseModel

class ConstraintSeverity(str, Enum):
    ADVISORY = "ADVISORY"   # Warn only
    SOFT = "SOFT"           # Can be bypassed under special conditions
    HARD = "HARD"           # Strictly non-negotiable threshold boundary

@dataclass
class Constraint(BaseModel):
    short_code: str
    rule_description: str
    severity: ConstraintSeverity = ConstraintSeverity.HARD
    is_active: bool = True

    def __post_init__(self) -> None:
        if not self.short_code.strip():
            raise ValueError("Constraint tracking demands a short_code identifier.")
        if not self.rule_description.strip():
            raise ValueError("A clear, descriptive validation rule explanation must be supplied.")