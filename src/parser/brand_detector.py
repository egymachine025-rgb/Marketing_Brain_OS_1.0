from __future__ import annotations
import re

class BrandDetector:
    """
    Scans normalized content blocks against registered brand dictionaries, 
    matching boundary-safe word structures.
    """
    def __init__(self, target_brands: list[str] | None = None) -> None:
        # Default target brands to look for if none are injected
        self.target_brands = target_brands or ["Apple", "Nike", "Adidas", "Samsung", "Sony", "Microsoft", "Amazon", "Tesla"]

    def detect(self, text: str) -> list[str]:
        detected: list[str] = []
        for brand in self.target_brands:
            # Match boundary-sensitive exact strings (case-insensitive)
            pattern = rf"\b{re.escape(brand)}\b"
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(brand)
        return detected