from __future__ import annotations
from typing import Protocol
from src.models.audience import Audience
from src.repositories.base import BaseRepository

class AudienceRepository(BaseRepository[Audience], Protocol):
    """
    Persistence contract targeting structured consumer segments, psychographics, and outreach footprints.
    """
    async def find_by_segment_name(self, segment_name: str) -> Audience | None: ...
    async def query_by_minimum_reach(self, min_reach: int) -> list[Audience]: ...