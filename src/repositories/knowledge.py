from __future__ import annotations
import uuid
from typing import Protocol, Any
from src.repositories.base import BaseRepository

class KnowledgeRepository(Protocol):
    """
    High-level composite search and retrieval contract across vectorized nodes, 
    unstructured documents, and raw context blocks stored in the Brain OS.
    """
    async def store_chunk(self, content: str, metadata: dict[str, Any], associated_entity_id: uuid.UUID | None = None) -> uuid.UUID: ...
    async def retrieve_similar_contexts(self, query: str, limit: int = 10) -> list[dict[str, Any]]: ...
    async def delete_by_associated_entity(self, entity_id: uuid.UUID) -> bool: ...