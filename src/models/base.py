from __future__ import annotations
import uuid
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, date
from enum import Enum
from typing import Any, get_type_hints, get_origin, get_args, Type, TypeVar

T = TypeVar("T", bound="BaseModel")

@dataclass
class BaseModel:
    """
    Abstract Base Model driving serialization, deserialization, 
    and dynamic inline mutations for Marketing Brain OS 1.0 core entities.
    """
    id: uuid.UUID = field(default_factory=uuid.uuid4, kw_only=True)
    created_at: datetime = field(default_factory=datetime.utcnow, kw_only=True)
    updated_at: datetime = field(default_factory=datetime.utcnow, kw_only=True)

    def to_dict(self) -> dict[str, Any]:
        """Recursively serializes dataclass fields to JSON-serializable primitives."""
        result: dict[str, Any] = {}
        for f in fields(self):
            val = getattr(self, f.name)
            result[f.name] = self._serialize_value(val)
        return result

    @classmethod
    def _serialize_value(cls, val: Any) -> Any:
        if isinstance(val, BaseModel):
            return val.to_dict()
        if isinstance(val, Enum):
            return val.value
        if isinstance(val, (datetime, date)):
            return val.isoformat()
        if isinstance(val, uuid.UUID):
            return str(val)
        if isinstance(val, list):
            return [cls._serialize_value(item) for item in val]
        if isinstance(val, dict):
            return {str(k): cls._serialize_value(v) for k, v in val.items()}
        return val

    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> T:
        """Parses a raw dictionary structure into a fully typed domain graph."""
        type_hints = get_type_hints(cls)
        init_kwargs: dict[str, Any] = {}

        for f in fields(cls):
            if f.name not in data:
                continue
            
            raw_val = data[f.name]
            field_type = type_hints[f.name]
            init_kwargs[f.name] = cls._deserialize_value(raw_val, field_type)

        return cls(**init_kwargs)

    @classmethod
    def _deserialize_value(cls, val: Any, field_type: Any) -> Any:
        if val is None:
            return None

        origin = get_origin(field_type)
        args = get_args(field_type)

        # Handle Optional/Union types
        if origin is Union or str(origin) == "typing.Union": # Fallback check for older runtime variants
            valid_types = [a for a in args if a is not type(None)]
            if valid_types:
                field_type = valid_types[0]
                origin = get_origin(field_type)
                args = get_args(field_type)

        if is_dataclass(field_type) and isinstance(val, dict):
            return field_type.from_dict(val)
        
        if origin is list and isinstance(val, list):
            item_type = args[0] if args else Any
            return [cls._deserialize_value(item, item_type) for item in val]

        if origin is dict and isinstance(val, dict):
            key_type, val_type = args if len(args) == 2 else (Any, Any)
            return {cls._deserialize_value(k, key_type): cls._deserialize_value(v, val_type) for k, v in val.items()}

        if isinstance(field_type, type) and issubclass(field_type, Enum):
            return field_type(val)

        if field_type is uuid.UUID and isinstance(val, str):
            return uuid.UUID(val)

        if field_type is datetime and isinstance(val, str):
            return datetime.fromisoformat(val)

        if field_type is date and isinstance(val, str):
            return date.fromisoformat(val)

        return val

    def update(self, data: dict[str, Any]) -> None:
        """In-place mutable update driven by schema hints."""
        type_hints = get_type_hints(self.__class__)
        
        for key, raw_val in data.items():
            if not hasattr(self, key) or key in ("id", "created_at"):
                continue

            field_type = type_hints[key]
            current_val = getattr(self, key)

            if isinstance(current_val, BaseModel) and isinstance(raw_val, dict):
                current_val.update(raw_val)
            else:
                parsed_val = self._deserialize_value(raw_val, field_type)
                setattr(self, key, parsed_val)
                
        self.updated_at = datetime.utcnow()


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    EGP = "EGP"


class TrendSentiment(str, Enum):
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"


class CampaignStatus(str, Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"


class DecisionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IMPLEMENTED = "IMPLEMENTED"