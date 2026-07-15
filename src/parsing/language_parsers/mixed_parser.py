from __future__ import annotations

from src.parsing.language_parsers.english_parser import EnglishParser
from src.parsing.language_parsers.arabic_parser import ArabicParser
from src.parsing.language_parsers.base_parser import BaseParser


class MixedParser(BaseParser):
    def __init__(self) -> None:
        self.english_parser = EnglishParser()
        self.arabic_parser = ArabicParser()

    def extract_price(self, text: str):
        amount, currency, confidence = self.english_parser.extract_price(text)
        if amount is not None:
            return amount, currency, confidence
        return self.arabic_parser.extract_price(text)

    def extract_brand(self, text: str):
        brand, confidence = self.english_parser.extract_brand(text)
        if brand is not None:
            return brand, confidence
        return self.arabic_parser.extract_brand(text)

    def extract_category(self, text: str):
        category, confidence = self.english_parser.extract_category(text)
        if category is not None:
            return category, confidence
        return self.arabic_parser.extract_category(text)

    def extract_condition(self, text: str):
        condition, confidence = self.english_parser.extract_condition(text)
        if condition is not None:
            return condition, confidence
        return self.arabic_parser.extract_condition(text)

    def extract_features(self, text: str):
        features = self.english_parser.extract_features(text)
        if features:
            return features
        return self.arabic_parser.extract_features(text)
