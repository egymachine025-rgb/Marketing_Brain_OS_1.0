from __future__ import annotations

class LanguageDetector:
    """
    يحدد لغة النص حتمياً بناءً على فحص وجود الحروف العربية.
    """
    def detect(self, text: str) -> str:
        if not text:
            return "en"
        # إذا احتوى النص على أي حرف عربي يتم اعتباره عربياً
        for char in text:
            if 0x0600 <= ord(char) <= 0x06FF:
                return "ar"
        return "en"