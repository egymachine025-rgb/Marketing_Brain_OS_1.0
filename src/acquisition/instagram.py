from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Any
from src.acquisition.base import BaseAcquisitionRepository

@dataclass(frozen=True)
class InstagramRawMedia:
    media_id: str
    username: str
    media_type: str  # IMAGE, VIDEO, or CAROUSEL_ALBUM
    caption_text: str | None
    like_count: int
    comments_count: int
    insights_raw: dict[str, Any]
    timestamp: datetime

class InstagramAcquisitionRepository(BaseAcquisitionRepository[InstagramRawMedia], Protocol):
    """
    Contract framing ingestion of Instagram Graph metrics, public tracking hashtags, and profiles.
    """
    async def fetch_profile_media(self, username: str, limit: int = 50) -> list[InstagramRawMedia]: ...
    async def fetch_by_hashtag(self, hashtag: str, limit: int = 50) -> list[InstagramRawMedia]: ...