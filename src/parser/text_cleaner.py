from __future__ import annotations
import re
import html
import unicodedata

class TextCleaner:
    """
    Handles deterministic stripping, Unicode normalization, HTML entity unescaping, 
    and sanitization of text inputs prior to execution of structural extraction rules.
    """
    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""
        
        # 1. Unescape HTML entities (e.g., &amp; -> &, &quot; -> ")
        cleaned = html.unescape(text)
        
        # 2. Normalize unicode formats (NFKC converts compatibility characters to standard equivalents)
        cleaned = unicodedata.normalize("NFKC", cleaned)
        
        # 3. Strip raw markup / HTML tags safely
        cleaned = re.sub(r"<[^>]*>", " ", cleaned)
        
        # 4. Collapse consecutive whitespace sequences
        cleaned = re.sub(r"\s+", " ", cleaned)
        
        return cleaned.strip()