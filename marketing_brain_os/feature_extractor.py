from __future__ import annotations
from typing import List

class FeatureExtractor:
    """
    يستخرج المواصفات الفنية أو المقاسات المذكورة في النص.
    """
    def extract(self, text: str) -> List[str]:
        if not text:
            return []
        features = []
        lower_text = text.lower()
        for spec in ["fit", "original", "slim", "classic", "cotton", "قطن"]:
            if spec in lower_text:
                features.append(spec.capitalize())
        for size in [" xl ", " xxl ", " lg ", " md ", " sm "]:
            if size in lower_text:
                features.append(size.strip().upper())
        return features