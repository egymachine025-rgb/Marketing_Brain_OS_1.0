from __future__ import annotations
import re

class ColorExtractor:
    """
    Extracts distinct design colors and aesthetic values found within descriptions.
    """
    def __init__(self, target_colors: list[str] | None = None) -> None:
        self.target_colors = target_colors or [
            "black", "white", "silver", "space gray", "gold", "rose gold", 
            "blue", "green", "red", "yellow", "pink", "purple", "orange"
        ]

    def extract(self, text: str) -> list[str]:
        text_lower = text.lower()
        extracted: list[str] = []
        for color in self.target_colors:
            pattern = rf"\b{re.escape(color)}\b"
            if re.search(pattern, text_lower):
                extracted.append(color)
        return extracted