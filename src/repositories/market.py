from __future__ import annotations
from typing import Protocol
from src.models.market import Market
from src.repositories.base import BaseRepository

class MarketRepository(BaseRepository[Market], Protocol):
    """
    Persistence contract governing geographic regions, economic attributes, and localization settings.
    """
    async def get_by_region_code(self, region_code: str) -> Market | None: ...
    async def list_all_active_markets(self) -> list[Market]: ...