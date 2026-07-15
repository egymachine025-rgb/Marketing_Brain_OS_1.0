from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Any
from src.acquisition.base import BaseAcquisitionRepository

@dataclass(frozen=True)
class TikTokRawVideo:
    video_id: str
    author_username: str
    video_description: str | None
    play_count: int
    digg_count: int  # Likes equivalent
    share_count: int
    comment_count: int
    music_info: dict[str, Any]
    created_timestamp: datetime

class TikTokAcquisitionRepository(BaseAcquisitionRepository[TikTokRawVideo], Protocol):
    """
    Interface definition monitoring incoming viral audio configurations and regional platform trends.
    """
    async def fetch_trending_videos(self, region_code: str, limit: int = 30) -> list[TikTokRawVideo]: ...
    async def fetch_user_feed(self, username: str, limit: int = 20) -> list[TikTokRawVideo]: ...