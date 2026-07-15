from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional

# Task 2: Unified imports list to completely remove duplicate declarations
from src.models.base import BaseModel
from src.repositories.base import BaseRepository

class MediaAsset(BaseModel):
    def __init__(self, asset_id: uuid.UUID, file_path: str, mime_type: str) -> None:
        self.asset_id = asset_id
        self.file_path = file_path
        self.mime_type = mime_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": str(self.asset_id),
            "file_path": self.file_path,
            "mime_type": self.mime_type
        }


class MediaRepository(BaseRepository[MediaAsset]):
    """
    Manages physical asset metadata lookup tables. Duplicate imports cleaned up.
    """
    def __init__(self) -> None:
        self._storage: Dict[uuid.UUID, MediaAsset] = {}

    async def save(self, entity: MediaAsset) -> MediaAsset:
        self._storage[entity.asset_id] = entity
        return entity

    async def get_by_id(self, entity_id: uuid.UUID) -> Optional[MediaAsset]:
        return self._storage.get(entity_id)

    async def delete(self, entity_id: uuid.UUID) -> bool:
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False