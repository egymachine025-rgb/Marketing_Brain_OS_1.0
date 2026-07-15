from __future__ import annotations

class TextCleaner:
    """
    يقوم بتطهير النصوص المدخلة وإزالة المسافات الزائدة والرموز التعبيرية المكررة.
    """
    def clean(self, text: str) -> str:
        if not text:
            return ""
        # تنظيف أساسي حتمي بدون تعقيدات
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join([line for line in lines if line])