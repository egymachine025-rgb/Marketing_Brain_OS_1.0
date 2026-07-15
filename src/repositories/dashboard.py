from __future__ import annotations
from typing import Protocol
from src.models.dashboard_statistics import DashboardStatistics

class DashboardRepository(Protocol):
    """
    Persistence and analytics sync contract tracking high-level system KPIs.
    """
    async def get_current_statistics(self) -> DashboardStatistics: ...
    async def update_statistics(self, stats: DashboardStatistics) -> None: ...