from __future__ import annotations

import re
from typing import Any
from src.parsing.language_parsers.base_parser import BaseParser


class EnglishParser(BaseParser):
    def __init__(self) -> None:
        self.price_patterns = [
            re.compile(r"\$\s?([0-9]+(?:[.,][0-9]{1,2})?)"),
            re.compile(r"([0-9]+(?:[.,][0-9]{1,2})?)\s?(USD|usd|EUR|eur|GBP|gbp|AED|aed|EGP|egp)"),
            re.compile(r"price\s*[:\-]\s*([0-9]+(?:[.,][0-9]{1,2})?)", re.IGNORECASE),
        ]
        self.brand_tokens = ["Nike", "Adidas", "Apple", "Samsung", "Sony", "Microsoft", "Amazon", "Tesla"]
        self.category_tokens = ["shoes", "sneakers", "jacket", "shirt", "phone", "laptop", "watch", "bag"]
        self.condition_tokens = ["new", "used", "open box", "refurbished", "excellent", "good", "fair"]

    def extract_price(self, text: str) -> tuple[float | None, str | None, float]:
        for pattern in self.price_patterns:
            match = pattern.search(text)
            if match:
                amount = float(match.group(1).replace(",", "."))
                currency = "USD"
                if len(match.groups()) > 1 and match.group(2):
                    currency = match.group(2).upper()
                return amount, currency, 0.9
        return None, None, 0.0

    def extract_brand(self, text: str) -> tuple[str | None, float]:
        lower = text.lower()
        for token in self.brand_tokens:
            if token.lower() in lower:
                return token, 0.9
        return None, 0.0

    def extract_category(self, text: str) -> tuple[str | None, float]:
        lower = text.lower()
        for token in self.category_tokens:
            if token in lower:
                return token.title(), 0.85
        return None, 0.0

    def extract_condition(self, text: str) -> tuple[str | None, float]:
        lower = text.lower()
        for token in self.condition_tokens:
            if token in lower:
                return token.title(), 0.8
        return None, 0.0

    def extract_features(self, text: str) -> list[tuple[str, float]]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        features: list[tuple[str, float]] = []
        for line in lines:
            if any(word in line.lower() for word in ["feature", "with", "includes", "comes with"]):
                clean = re.sub(r"^(feature[s]?\s*[:\-]?|with\s*|includes\s*|comes with\s*)", "", line, flags=re.IGNORECASE)
                clean = clean.strip(" .,-")
                if clean:
                    for part in [part.strip() for part in re.split(r",|;", clean) if part.strip()]:
                        features.append((part, 0.8))
        if not features:
            candidates = [token.strip() for token in re.split(r"[;\n]+", text) if token.strip()]
            for candidate in candidates:
                if "feature" in candidate.lower() or "with" in candidate.lower() or "includes" in candidate.lower() or "comes with" in candidate.lower():
                    parts = [part.strip(" .,-") for part in re.split(r",|;", candidate) if part.strip()]
                    for part in parts:
                        if len(part) > 3 and "price" not in part.lower() and "usd" not in part.lower():
                            features.append((part, 0.7))
                else:
                    token = candidate.strip(".,")
                    if len(token) > 3 and "price" not in token.lower() and "usd" not in token.lower():
                        features.append((token, 0.4))
        return features
