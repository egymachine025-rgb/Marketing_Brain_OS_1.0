from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class KnowledgeObject:
    """
    A foundational knowledge entity for the Marketing Brain knowledge layer.

    This object captures a single piece of structured knowledge along with
    provenance, confidence, language information, and optional metadata.

    Fields:
        type: Knowledge type/category, such as "fact", "insight", or "rule".
        name: Human-readable label for the knowledge item.
        value: The extracted knowledge payload or assertion.
        source: Origin of the knowledge, such as a channel, pipeline, or source system.
        confidence: Confidence score between 0.0 and 1.0.
        language: Language code for the knowledge value (e.g. "en", "ar").
        metadata: Optional supplemental attributes related to this knowledge.
        created_at: UTC timestamp when the knowledge object was created.
        updated_at: UTC timestamp when the knowledge object was last updated.
        id: Unique UUID identifier for the knowledge object.
    """

    type: str
    name: str
    value: Any
    source: str
    confidence: float = 1.0
    language: str = "en"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the knowledge object to a JSON-serializable dictionary."""
        return {
            "id": str(self.id),
            "type": self.type,
            "name": self.name,
            "value": self.value,
            "source": self.source,
            "confidence": self.confidence,
            "language": self.language,
            "metadata": {**self.metadata},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeObject":
        """Create a KnowledgeObject instance from a dictionary representation."""
        return cls(
            id=uuid.UUID(data["id"]) if isinstance(data.get("id"), str) else data.get("id", uuid.uuid4()),
            type=data["type"],
            name=data["name"],
            value=data["value"],
            source=data["source"],
            confidence=float(data.get("confidence", 1.0)),
            language=data.get("language", "en"),
            metadata=dict(data.get("metadata", {})),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at", datetime.utcnow()),
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data.get("updated_at"), str) else data.get("updated_at", datetime.utcnow()),
        )
