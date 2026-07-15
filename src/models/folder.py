from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from src.models.base import BaseModel

@dataclass
class Folder(BaseModel):
    display_name: str
    parent_folder_id: uuid.UUID | None = None
    contained_model_references: list[uuid.UUID] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.display_name.strip():
            raise ValueError("Folder naming schemes require transparent non-empty values.")
        if self.parent_folder_id == self.id and self.parent_folder_id is not None:
            raise ValueError("Self-referential cycles within systemic folders are structurally illegal.")