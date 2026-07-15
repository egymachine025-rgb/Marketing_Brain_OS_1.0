from __future__ import annotations
from typing import Protocol, Any
import uuid


class KnowledgeGraphContract(Protocol):
    """
    Contract defining the interface for a knowledge graph implementation.
    """

    def add_relationship(
        self,
        from_id: str | uuid.UUID,
        to_id: str | uuid.UUID,
        relation_type: str,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...

    def get_relationships(
        self, from_id: str | uuid.UUID, relation_type: str | None = None
    ) -> list[dict[str, Any]]:
        ...

    def get_related(
        self, to_id: str | uuid.UUID, relation_type: str | None = None
    ) -> list[dict[str, Any]]:
        ...

    def find_path(
        self,
        from_id: str | uuid.UUID,
        to_id: str | uuid.UUID,
        max_depth: int = 3,
    ) -> list[list[str]]:
        ...

    def get_neighbors(self, entity_id: str | uuid.UUID) -> dict[str, list[dict[str, Any]]]:
        ...

    def delete_relationship(
        self,
        from_id: str | uuid.UUID,
        to_id: str | uuid.UUID,
        relation_type: str,
    ) -> bool:
        ...

    def get_graph_statistics(self) -> dict[str, Any]:
        ...
