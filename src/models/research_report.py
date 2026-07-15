from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from src.models.base import BaseModel
from src.models.snapshots import MarketSnapshot, AudienceSnapshot, TrendSnapshot, CompetitorSnapshot

@dataclass
class ResearchReport(BaseModel):
    report_title: str
    generation_timestamp: datetime = field(default_factory=datetime.utcnow)
    market_state: MarketSnapshot = field(default_factory=lambda: MarketSnapshot())
    audience_state: AudienceSnapshot = field(default_factory=lambda: AudienceSnapshot())
    tracked_trends: list[TrendSnapshot] = field(default_factory=list)
    observed_competitors: list[CompetitorSnapshot] = field(default_factory=list)
    executive_summary_points: list[str] = field(default_factory=list)
    raw_metric_matrix: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.report_title.strip():
            raise ValueError("Research report initialization schema requires a descriptive title string.")