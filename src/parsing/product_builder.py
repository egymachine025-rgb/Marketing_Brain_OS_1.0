from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from src.knowledge.knowledge_repository import KnowledgeRepository
from src.knowledge.knowledge_object import KnowledgeObject


class ProductBuilder:
    """Transforms raw parser output into a normalized product domain dictionary."""

    def build(self, raw_product: dict[str, Any]) -> dict[str, Any]:
        title = raw_product.get("raw_title", "Unnamed Product").strip()
        description = raw_product.get("raw_description", "").strip()
        category = raw_product.get("extracted_category") or "Other"
        condition = raw_product.get("extracted_condition") or "Unknown"
        price_amount = raw_product.get("extracted_price") or 0.0
        currency = raw_product.get("extracted_currency") or "USD"
        brand = raw_product.get("extracted_brand") or "Unknown"
        features = raw_product.get("extracted_features") or []
        language = raw_product.get("detected_language", "en")

        product_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        return {
            "product_id": product_id,
            "listing": {
                "title": title,
                "description": description,
                "brand": brand,
                "category": category,
                "condition": condition,
                "price": {"amount": float(price_amount), "currency": currency},
                "features": list(features),
                "language": language,
            },
            "source": {
                "channel": raw_product.get("source_channel", ""),
                "message_id": raw_product.get("source_message_id", ""),
                "timestamp": raw_product.get("timestamp", now),
                "raw_text": raw_product.get("raw_description", ""),
            },
            "knowledge_links": {
                "brand_id": None,
                "category_id": None,
                "market_id": None,
                "audience_ids": [],
            },
            "confidence": self._compute_confidence(raw_product),
            "status": "pending_review",
            "created_at": now,
            "updated_at": now,
            "language": language,
            "features": list(features),
            "offer": raw_product.get("extracted_offer", ""),
            "colors": raw_product.get("extracted_colors", []),
            "keywords": raw_product.get("extracted_keywords", []),
        }

    def validate(self, product: dict[str, Any]) -> tuple[bool, list[str]]:
        errors: list[str] = []
        listing = product.get("listing", {})

        if not listing.get("title"):
            errors.append("Missing title")
        if not listing.get("category"):
            errors.append("Missing category")
        if not listing.get("price", {}).get("amount"):
            errors.append("Missing or invalid price")
        if not listing.get("price", {}).get("currency"):
            errors.append("Missing currency")

        return (len(errors) == 0, errors)

    def enrich_with_knowledge(
        self,
        product: dict[str, Any],
        knowledge_repository: KnowledgeRepository,
    ) -> dict[str, Any]:
        raw_brand = product["listing"].get("brand")

        if raw_brand:
            known_brand = knowledge_repository.get_by_type_and_name("brand", raw_brand, product["listing"].get("language", "en"))
            if known_brand:
                product["knowledge_links"]["brand_id"] = known_brand.id

        category_name = product["listing"].get("category")
        if category_name:
            known_category = knowledge_repository.get_by_type_and_name("category", category_name, product["listing"].get("language", "en"))
            if known_category:
                product["knowledge_links"]["category_id"] = known_category.id

        # Market link heuristics
        markets = knowledge_repository.get_by_type("market", product["listing"].get("language", "en"))
        if markets:
            product["knowledge_links"]["market_id"] = markets[0].id

        audiences = knowledge_repository.get_by_type("audience", product["listing"].get("language", "en"))
        if audiences:
            product["knowledge_links"]["audience_ids"] = [aud.id for aud in audiences[:2]]

        return product

    def _compute_confidence(self, raw_product: dict[str, Any]) -> float:
        scores = raw_product.get("confidence_scores", {})
        base = 0.0
        count = 0
        for key in ["price", "brand", "category", "condition"]:
            value = scores.get(key)
            if isinstance(value, (int, float)):
                base += value
                count += 1
        if count:
            return round(min(1.0, base / count), 4)
        return 0.0
