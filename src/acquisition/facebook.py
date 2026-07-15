from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from src.acquisition.base import BaseAcquisitionRepository

@dataclass(frozen=True)
class FacebookRawPost:
    post_id: str
    page_id: str
    permalink_url: str
    message_body: str | None
    like_count: int
    share_count: int
    comment_count: int
    created_time: datetime

class FacebookAcquisitionRepository(BaseAcquisitionRepository[FacebookRawPost], Protocol):
    """
    Contract managing standard ingestion for raw Facebook Graph endpoints and tracked Page assets.
    """
    async def fetch_page_posts(self, page_id: str, historical_depth_days: int = 30) -> list[FacebookRawPost]: ...