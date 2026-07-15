from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from src.models.base import BaseModel, CampaignStatus

@dataclass
class Campaign(BaseModel):
    title: str
    allocated_budget: float
    status: CampaignStatus = CampaignStatus.DRAFT
    target_audiences: list[uuid.UUID] = field(default_factory=list)
    launch_window_start: datetime | None = None
    launch_window_end: datetime | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Campaign Title must contain safe string literals.")
        if self.allocated_budget < 0.0:
            raise ValueError("Campaign funding parameters cannot express negative budgets.")
        if self.launch_window_start and self.launch_window_end:
            if self.launch_window_end < self.launch_window_start:
                raise ValueError("Temporal execution error: End window cannot precede launch window start boundaries.")