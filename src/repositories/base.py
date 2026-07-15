from __future__ import annotations
from typing import Protocol, TypeVar, Generic
from uuid import UUID

T = TypeVar("T", covariant=True)

class BaseRepository(Protocol[T]):
    """
    Root storage interface establishing core persistence invariants for systemic entities.
    """
    async def save(self, model: T) -> T: ...
    async def get_by_id(self, entity_id: UUID) -> T | None: ...
    async def delete(self, entity_id: UUID) -> bool: ...