from __future__ import annotations
from datetime import datetime
from typing import Protocol
from src.models.trend import Trend
from src.models.base import TrendSentiment
from src.repositories.base import BaseRepository

class TrendRepository(BaseRepository[Trend], Protocol):
    """
    Persistence contract tracing structural patterns, key topic velocities, and market sentiments.
    """
    async def get_high_velocity_trends(self, threshold: float) -> list[Trend]: ...
    async def fetch_trends_by_sentiment(self, sentiment: TrendSentiment) -> list[Trend]: ...
    async def get_historical_trends(self, start_time: datetime, end_time: datetime) -> list[Trend]: ...