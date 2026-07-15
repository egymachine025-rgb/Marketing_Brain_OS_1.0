from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Any
from src.acquisition.base import BaseAcquisitionRepository

@dataclass(frozen=True)
class TelegramRawMessage:
    message_id: str
    channel_id: str
    content_text: str | None
    media_metadata: dict[str, Any]
    forward_count: int
    view_count: int
    timestamp: datetime

class TelegramAcquisitionRepository(BaseAcquisitionRepository[TelegramRawMessage], Protocol):
    """
    Contract for raw Telegram data gathering across tracking channel feeds and chats.
    """
    async def fetch_channel_history(self, channel_id: str, limit: int = 100) -> list[TelegramRawMessage]: ...
    async def stream_live_messages(self, channel_ids: list[str]) -> Any: ...