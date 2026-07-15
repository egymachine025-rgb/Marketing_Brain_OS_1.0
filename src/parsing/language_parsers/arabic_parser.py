from __future__ import annotations

import re
from typing import Any
from src.parsing.language_parsers.base_parser import BaseParser


class ArabicParser(BaseParser):
    def __init__(self) -> None:
        self.arabic_digits = str.maketrans(
            "٠١٢٣٤٥٦٧٨٩",
            "0123456789"
        )
        self.price_patterns = [
            re.compile(r"سعر\s*[:\-]?\s*([0-9٠١٢٣٤٥٦٧٨٩]+(?:[.,][0-9٠١٢٣٤٥٦٧٨٩]{1,2})?)"),
            re.compile(r"([0-9٠١٢٣٤٥٦٧٨٩]+(?:[.,][0-9٠١٢٣٤٥٦٧٨٩]{1,2})?)\s*(?:جنيه|جنيهات|درهم|دولار|ريال|ر\.س\.|EGP|AED)", re.IGNORECASE),
        ]
        self.brand_tokens = ["Nike", "Adidas", "Apple", "Samsung", "Sony", "Microsoft", "Amazon", "Tesla"]
        self.category_tokens = ["حذاء", "شاحن", "قميص", "بنطال", "حقيبة", "ساعة", "هاتف", "لابتوب"]
        self.condition_tokens = ["جديد", "مستعمل", "كسر زيرو", "ترميم", "ممتاز", "جيد", "مستعمل بحالة ممتازة"]

    def _arabic_to_latin_number(self, value: str) -> str:
        return value.translate(self.arabic_digits)

    def extract_price(self, text: str) -> tuple[float | None, str | None, float]:
        for pattern in self.price_patterns:
            match = pattern.search(text)
            if match:
                raw = self._arabic_to_latin_number(match.group(1)).replace(",", ".")
                try:
                    amount = float(raw)
                except ValueError:
                    continue
                currency = "EGP"
                if "درهم" in text or "AED" in text.upper():
                    currency = "AED"
                if "دولار" in text or "USD" in text.upper():
                    currency = "USD"
                return amount, currency, 0.9
        return None, None, 0.0

    def extract_brand(self, text: str) -> tuple[str | None, float]:
        for token in self.brand_tokens:
            if token.lower() in text.lower() or token in text:
                return token, 0.85
        return None, 0.0

    def extract_category(self, text: str) -> tuple[str | None, float]:
        for token in self.category_tokens:
            if token in text:
                return token, 0.85
        return None, 0.0

    def extract_condition(self, text: str) -> tuple[str | None, float]:
        for token in self.condition_tokens:
            if token in text:
                return token, 0.8
        return None, 0.0

    def extract_features(self, text: str) -> list[tuple[str, float]]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        features: list[tuple[str, float]] = []
        for line in lines:
            if any(keyword in line for keyword in ["مواصفات", "خصائص", "مع", "بما في ذلك", "تشمل"]):
                clean = re.sub(r"^(مواصفات|خصائص|مع|بما في ذلك|تشمل)\s*[:\-]?\s*", "", line)
                clean = clean.strip(" .,-")
                if clean:
                    features.append((clean, 0.8))
        if not features:
            for line in lines:
                token = line.strip(".,")
                if len(token) > 3 and "سعر" not in token:
                    features.append((token, 0.4))
        return features
