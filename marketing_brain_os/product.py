from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from src.models.base import BaseModel, Currency


class Product(BaseModel):
    """
    Core Domain Model for Marketing Brain OS representing a parsed, 
    standardized, and fingerprinted product.
    """
    
    def __init__(
        self,
        id: uuid.UUID,
        name: str,
        brand: str,
        category: str,
        language: str,
        price: float,
        offer: str,
        colors: List[str],
        features: List[str],
        keywords: List[str],
        description: str,
        currency: Currency = Currency.USD,
        fingerprint: Optional[str] = None,
        created_at: Optional[datetime] = None,
        telegram_channel: Optional[str] = None,
        telegram_message_id: Optional[int] = None,
    ) -> None:
        self.id = id
        self.name = name
        self.brand = brand
        self.category = category
        self.language = language
        self.price = price
        self.offer = offer
        self.colors = colors
        self.features = features
        self.keywords = keywords
        self.description = description
        self.currency = currency
        self.fingerprint = fingerprint or ""
        self.created_at = created_at or datetime.utcnow()
        self.telegram_channel = telegram_channel
        self.telegram_message_id = telegram_message_id

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the active product instance structure into a plain dictionary.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "language": self.language,
            "price": self.price,
            "offer": self.offer,
            "colors": self.colors,
            "features": self.features,
            "keywords": self.keywords,
            "description": self.description,
            "currency": self.currency.value if hasattr(self.currency, "value") else str(self.currency),
            "fingerprint": self.fingerprint,
            "created_at": self.created_at.isoformat(),
            "telegram_channel": self.telegram_channel,
            "telegram_message_id": self.telegram_message_id,
        }