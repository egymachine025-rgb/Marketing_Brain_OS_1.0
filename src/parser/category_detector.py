from __future__ import annotations
import re

class CategoryDetector:
    """
    Maps localized content into standardized product categories based on semantic keyword mapping rules.
    """
    def __init__(self, category_mappings: dict[str, list[str]] | None = None) -> None:
        self.mappings = category_mappings or {
            "Electronics": ["smartphone", "laptop", "tv", "audio", "headphones", "device", "console"],
            "Apparel": ["shoes", "jacket", "shirt", "pants", "clothing", "apparel", "sneakers"],
            "Home & Living": ["sofa", "kitchen", "furniture", "appliance", "decor", "lighting"],
            "Automotive": ["car", "ev", "charger", "tires", "parts", "vehicle"]
        }

    def detect(self, text: str) -> list[str]:
        text_lower = text.lower()
        matched_categories: list[str] = []
        
        for category, keywords in self.mappings.items():
            for keyword in keywords:
                pattern = rf"\b{re.escape(keyword)}s?\b"
                if re.search(pattern, text_lower):
                    matched_categories.append(category)
                    break
        return matched_categories