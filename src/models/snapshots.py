from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from src.models.base import BaseModel
from src.models.market import Market
from src.models.audience import Audience
from src.models.trend import Trend
from src.models.competitor import Competitor

@dataclass
class MarketSnapshot(BaseModel):
    captured_at: datetime = field(default_factory=datetime.utcnow)
    target_market: Market = field(default_factory=lambda: Market(region_code="UNKNOWN", local_currency="USD"))
    active_competitor_count: int = 0
    average_pricing_index: float = 1.0
    macro_economic_signals: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.active_competitor_count < 0:
            raise ValueError("Active competitor snapshot count cannot drop below 0.")
        if self.average_pricing_index < 0.0:
            raise ValueError("Pricing indexing references must evaluate as non-negative float vectors.")


@dataclass
class AudienceSnapshot(BaseModel):
    captured_at: datetime = field(default_factory=datetime.utcnow)
    target_audience: Audience = field(default_factory=lambda: Audience(segment_name="UNKNOWN"))
    estimated_market_penetration_rate: float = 0.0  # Percentage scale e.g. 12.50 for 12.5%
    core_engagement_velocity: float = 0.0
    primary_communication_channels: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not (0.0 <= self.estimated_market_penetration_rate <= 100.0):
            raise ValueError("Estimated penetration bounds must balance inside a strict 0.0 to 100.0 scale mapping.")


@dataclass
class TrendSnapshot(BaseModel):
    captured_at: datetime = field(default_factory=datetime.utcnow)
    underlying_trend: Trend = field(default_factory=lambda: Trend(topic_keywords=[], sentiment="NEUTRAL", momentum_velocity_score=0.0, observed_at=datetime.utcnow()))
    relevance_confidence_score: float = 1.0
    impact_projections: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (0.0 <= self.relevance_confidence_score <=  1.0):
            raise ValueError("Relevance statistical confidence matrix demands scalar boundaries from 0.0 to 1.0.")


@dataclass
class CompetitorSnapshot(BaseModel):
    captured_at: datetime = field(default_factory=datetime.utcnow)
    target_competitor: Competitor = field(default_factory=lambda: Competitor(brand_name="UNKNOWN", market_share_percentage=0.0))
    detected_pricing_shifts: list[str] = field(default_factory=list)
    estimated_monthly_ad_spend: float = 0.0

    def __post_init__(self) -> None:
        if self.estimated_monthly_ad_spend < 0.0:
            raise ValueError("Ad monetary spend estimates cannot present negative values.")