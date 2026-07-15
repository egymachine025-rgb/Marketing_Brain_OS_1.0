from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from src.models.base import BaseModel

@dataclass
class DashboardFilters(BaseModel):
    """
    Schema representation of query criteria, active scopes, 
    and date ranges used to partition dashboard data.
    """
    start_date: datetime | None = None
    end_date: datetime | None = None
    selected_market_ids: list[str] = field(default_factory=list)
    selected_channels: list[str] = field(default_factory=list)
    search_query: str = ""
    min_price_threshold: float | None = None
    max_price_threshold: float | None = None

    def __post_init__(self) -> None:
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("Temporal inconsistency: end_date cannot precede start_date.")
        if self.min_price_threshold is not None and self.min_price_threshold < 0.0:
            raise ValueError("Minimum price threshold parameter cannot drop below 0.0.")