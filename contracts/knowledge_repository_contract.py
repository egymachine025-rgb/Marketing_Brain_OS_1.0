from __future__ import annotations
from typing import Protocol, Any
import uuid

from src.knowledge.knowledge_object import KnowledgeObject


class KnowledgeRepositoryContract(Protocol):
    """
    Contract defining the interface for a knowledge repository.
    """

    def save(self, knowledge_object: KnowledgeObject) -> KnowledgeObject:
        ...

    def get_by_id(self, obj_id: str | uuid.UUID) -> KnowledgeObject | None:
        ...

    def get_by_type_and_name(
        self, obj_type: str, name: str, language: str = "en"
    ) -> KnowledgeObject | None:
        ...

    def get_by_type(self, obj_type: str, language: str = "en") -> list[KnowledgeObject]:
        ...

    def get_all(self) -> list[KnowledgeObject]:
        ...

    def get_linked_products(self, obj_id: str | uuid.UUID) -> list[str]:
        ...

    def link_product(self, obj_id: str | uuid.UUID, product_id: str) -> bool:
        ...

    def get_statistics(self) -> dict[str, Any]:
        ...

    def find_by_metadata(self, key: str, value: Any) -> list[KnowledgeObject]:
        ...

    def delete(self, obj_id: str | uuid.UUID) -> bool:
        ...
