from __future__ import annotations
from typing import List

class KeywordExtractor:
    """
    يستخرج الكلمات المفتاحية الأساسية لتصنيف المنتج.
    """
    def extract(self, text: str) -> List[str]:
        if not text:
            return []
        keywords = []
        lower_text = text.lower()
        targets = {
            "polo": "polo", "t-shirt": "t-shirt", "تيشيرت": "t-shirt",
            "shoes": "shoes", "حذاء": "shoes", "bag": "bags", "شنطة": "bags"
        }
        for key, val in targets.items():
            if key in lower_text:
                if val not in keywords:
                    keywords.append(val)
        return keywords