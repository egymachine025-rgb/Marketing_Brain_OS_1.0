from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.parsing.language_parsers.arabic_parser import ArabicParser
from src.parsing.language_parsers.english_parser import EnglishParser
from src.parsing.language_parsers.mixed_parser import MixedParser


class ParserManager:
    """High-level orchestration of language parsing strategies."""

    def __init__(self) -> None:
        self.english_parser = EnglishParser()
        self.arabic_parser = ArabicParser()
        self.mixed_parser = MixedParser()

    def detect_language(self, text: str) -> str:
        if not text or not text.strip():
            return "en"

        arabic_count = sum(1 for char in text if "\u0600" <= char <= "\u06FF")
        latin_count = sum(1 for char in text if "a" <= char.lower() <= "z")

        if arabic_count > 0 and latin_count > 0:
            if arabic_count >= latin_count:
                return "ar"
            return "mixed"
        if arabic_count > 0:
            return "ar"
        return "en"

    def get_parser_for(self, language: str):
        if language == "ar":
            return self.arabic_parser
        if language == "mixed":
            return self.mixed_parser
        return self.english_parser

    def parse_message(self, message_text: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        metadata = metadata or {}
        language = self.detect_language(message_text)
        parser = self.get_parser_for(language)

        amount, currency, price_confidence = parser.extract_price(message_text)
        brand, brand_confidence = parser.extract_brand(message_text)
        category, category_confidence = parser.extract_category(message_text)
        condition, condition_confidence = parser.extract_condition(message_text)
        feature_pairs = parser.extract_features(message_text)

        features = [feature for feature, _ in feature_pairs]
        feature_confidence = {feature: confidence for feature, confidence in feature_pairs}

        timestamp = metadata.get("timestamp") or datetime.now(timezone.utc).isoformat()

        return {
            "raw_title": message_text.split("\n", 1)[0].strip(),
            "raw_description": message_text.strip(),
            "detected_language": language,
            "extracted_price": amount,
            "extracted_currency": currency,
            "extracted_brand": brand,
            "extracted_category": category,
            "extracted_condition": condition,
            "extracted_features": features,
            "confidence_scores": {
                "price": price_confidence,
                "brand": brand_confidence,
                "category": category_confidence,
                "condition": condition_confidence,
                "features": feature_confidence,
            },
            "source_message_id": str(metadata.get("message_id", "")),
            "source_channel": str(metadata.get("channel", "")),
            "timestamp": str(timestamp),
        }
