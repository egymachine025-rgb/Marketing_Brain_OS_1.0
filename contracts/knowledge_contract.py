from __future__ import annotations
from typing import Protocol, Any
import uuid


class KnowledgeObjectContract(Protocol):
    """
    Contract defining the shape and behavior expected from a knowledge object.
    """

    id: uuid.UUID
    type: str
    name: str
    value: Any
    source: str
    confidence: float
    language: str
    metadata: dict[str, Any]
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeObjectContract":
        ...
