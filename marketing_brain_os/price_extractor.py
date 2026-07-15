from __future__ import annotations

class PriceExtractor:
    """
    يستخرج القيم الرقمية للأسعار من النصوص حتمياً بدون Regex.
    """
    def extract(self, text: str) -> float:
        if not text:
            return 0.0
        words = text.replace(":", " ").replace(",", "").split()
        for word in words:
            # محاولة العثور على أول قيمة عددية تعبر عن السعر
            try:
                val = float(word)
                if val > 0:
                    return val
            except ValueError:
                continue
        return 0.0