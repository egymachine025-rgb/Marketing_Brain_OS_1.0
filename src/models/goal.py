from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from src.models.base import BaseModel

class GoalPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class GoalStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    ACHIEVED = "ACHIEVED"
    ABANDONED = "ABANDONED"

@dataclass
class Goal(BaseModel):
    title: str
    description: str
    target_date: datetime
    priority: GoalPriority = GoalPriority.MEDIUM
    status: GoalStatus = GoalStatus.PROPOSED
    progress_percentage: float = 0.0
    parent_goal_id: uuid.UUID | None = None
    success_metrics: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Goal title must contain a valid name.")
        if not (0.0 <= self.progress_percentage <= 100.0):
            raise ValueError("Goal progress percentage must sit strictly between 0.0 and 100.0.")