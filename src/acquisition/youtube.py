from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from src.acquisition.base import BaseAcquisitionRepository

@dataclass(frozen=True)
class YouTubeRawVideo:
    video_id: str
    channel_id: str
    title: str
    description: str | None
    view_count: int
    like_count: int
    comment_count: int
    published_at: datetime

class YouTubeAcquisitionRepository(BaseAcquisitionRepository[YouTubeRawVideo], Protocol):
    """
    Contract regulating extraction maps targeting historical and newly broadcasted public video streams.
    """
    async def fetch_channel_uploads(self, channel_id: str, limit: int = 50) -> list[YouTubeRawVideo]: ...
    async def search_by_query(self, query: str, limit: int = 25) -> list[YouTubeRawVideo]: ...