from __future__ import annotations
from typing import Protocol, TypeVar, Generic, Any
from uuid import UUID
from datetime import datetime

T = TypeVar("T", covariant=True)

class BaseAcquisitionRepository(Protocol[T]):
    """
    Core systemic contract defining immutable ingestion rules for inbound operational data streams.
    """
    async def get_by_id(self, item_id: UUID) -> T | None: ...
    async def get_by_external_id(self, external_id: str) -> T | None: ...
    async def fetch_recent(self, limit: int = 100, offset: int = 0) -> list[T]: ...
    async def fetch_by_date_range(self, start_date: datetime, end_date: datetime) -> list[T]: ...