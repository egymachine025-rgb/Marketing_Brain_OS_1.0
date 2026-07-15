from __future__ import annotations

class OfferExtractor:
    """
    يستخرج العروض والخصومات المذكورة في نصوص القنوات.
    """
    def extract(self, text: str) -> str:
        if not text:
            return "None"
        lower_text = text.lower()
        if "off" in lower_text or "%" in lower_text:
            for word in lower_text.split():
                if "%" in word or "off" in word:
                    return word.upper()
        if "خصم" in text or "عرض" in text:
            return "Promo Active"
        return "None"