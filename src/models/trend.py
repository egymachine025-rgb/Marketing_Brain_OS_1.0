from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from src.models.base import BaseModel, TrendSentiment

@dataclass
class Trend(BaseModel):
    topic_keywords: list[str]
    sentiment: TrendSentiment
    momentum_velocity_score: float
    observed_at: datetime

    def __post_init__(self) -> None:
        if not self.topic_keywords:
            raise ValueError("Trend context demands at least one core identifying topic keyword mapping.")