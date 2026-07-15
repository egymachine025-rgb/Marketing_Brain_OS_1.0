from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from src.models.base import BaseModel, DecisionStatus

@dataclass
class Decision(BaseModel):
    rationale_summary: str
    status: DecisionStatus = DecisionStatus.PENDING
    linked_analysis_ids: list[uuid.UUID] = field(default_factory=list)
    actionable_steps: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.rationale_summary.strip():
            raise ValueError("A cohesive execution summary rationale must accompany all decision contexts.")