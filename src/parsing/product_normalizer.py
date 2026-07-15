from __future__ import annotations

import math
from typing import Any

from src.knowledge.knowledge_repository import KnowledgeRepository
from src.knowledge.knowledge_object import KnowledgeObject


class ProductNormalizer:
    """Normalizes product payload fields for consistency and downstream ingestion."""

    STATIC_CURRENCY_RATES = {
        "USD": 1.0,
        "EGP": 0.032,
        "AED": 0.27,
        "EUR": 1.08,
        "GBP": 1.25,
    }

    def normalize(self, product: dict[str, Any]) -> dict[str, Any]:
        listing = product["listing"]

        listing["title"] = self.normalize_title(listing.get("title", ""), listing.get("language", "en"))
        listing["description"] = listing.get("description", "").strip()
        listing["category"] = self.normalize_category(listing.get("category", ""), product.get("knowledge_repo"))
        listing["brand"] = self.normalize_brand(listing.get("brand", ""), product.get("knowledge_repo")) or "Unknown"

        normalized_price = self.normalize_price(
            listing.get("price", {}).get("amount", 0.0),
            listing.get("price", {}).get("currency", "USD"),
        )
        listing["price"] = normalized_price

        listing["features"] = self.standardize_features(listing.get("features", []))

        product["confidence"] = self._round_confidence(product.get("confidence", 0.0))
        product["updated_at"] = product.get("updated_at") or product.get("created_at")

        return product

    def normalize_title(self, title: str, language: str) -> str:
        cleaned = title.strip()
        if language == "en":
            return " ".join(word.capitalize() for word in cleaned.split())
        return cleaned

    def normalize_price(self, amount: float, currency: str) -> dict[str, Any]:
        if amount is None:
            amount = 0.0
        currency = currency.upper() if isinstance(currency, str) else "USD"
        rate = self.STATIC_CURRENCY_RATES.get(currency, 1.0)
        normalized_amount = round(float(amount) * rate, 2)
        return {"amount": normalized_amount, "currency": "USD"}

    def normalize_category(self, raw_category: str, knowledge_repository: KnowledgeRepository | None) -> str:
        clean = raw_category.strip().title()
        if not clean:
            return "Other"
        if knowledge_repository is None:
            return clean
        known = knowledge_repository.get_by_type_and_name("category", clean, "en")
        if known:
            return known.name
        return clean

    def normalize_brand(self, raw_brand: str, knowledge_repository: KnowledgeRepository | None) -> str | None:
        if not raw_brand or not raw_brand.strip():
            return None
        clean = raw_brand.strip().title()
        if knowledge_repository is None:
            return clean
        known = knowledge_repository.get_by_type_and_name("brand", clean, "en")
        if known:
            return known.name
        if self._brand_confidence(raw_brand) > 0.8:
            brand_obj = KnowledgeObject(
                type="brand",
                name=clean,
                value=clean,
                source="parser_manager",
                confidence=0.85,
                language="en",
            )
            knowledge_repository.save(brand_obj)
            return brand_obj.name
        return None

    def standardize_features(self, features: list[str]) -> list[str]:
        normalized: set[str] = set()
        for feat in features:
            clean = feat.strip().strip("-•*.")
            if not clean:
                continue
            normalized.add(" ".join(word.capitalize() for word in clean.split()))
        return sorted(normalized)

    def _brand_confidence(self, raw_brand: str) -> float:
        if not raw_brand:
            return 0.0
        return 0.9 if len(raw_brand.strip()) > 2 else 0.0

    def _round_confidence(self, value: float) -> float:
        return round(min(1.0, max(0.0, value)), 4)
