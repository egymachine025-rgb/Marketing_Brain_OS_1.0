from __future__ import annotations
from typing import List

class ColorExtractor:
    """
    يستخرج الألوان المذكورة في المنشور باللغتين العربية والانجليزية.
    """
    def extract(self, text: str) -> List[str]:
        if not text:
            return []
        found_colors = []
        lower_text = text.lower()
        color_map = {
            "black": "black", "أسود": "black", "اسود": "black",
            "white": "white", "أبيض": "white", "ابيض": "white",
            "red": "red", "أحمر": "red", "احمر": "red",
            "blue": "blue", "أزرق": "blue", "ازرق": "blue",
        }
        for keyword, canonical in color_map.items():
            if keyword in lower_text:
                if canonical not in found_colors:
                    found_colors.append(canonical)
        return found_colors