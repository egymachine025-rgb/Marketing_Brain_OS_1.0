from __future__ import annotations
import re

class KeywordExtractor:
    """
    Extracts relevant keywords from normalized text bodies by removing stop words 
    and analyzing high-frequency terms.
    """
    def __init__(self, stop_words: set[str] | None = None) -> None:
        self.stop_words = stop_words or {
            "the", "and", "our", "you", "for", "with", "this", "that", "your", 
            "from", "will", "this", "their", "they", "were", "are", "was", "not"
        }

    def extract(self, text: str, max_keywords: int = 10) -> list[str]:
        # Filter down to alphanumeric terms greater than 2 characters
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        frequency_map: dict[str, int] = {}
        
        for word in words:
            if word not in self.stop_words:
                frequency_map[word] = frequency_map.get(word, 0) + 1
                
        # Sort by frequency descending
        sorted_keywords = sorted(frequency_map.keys(), key=lambda k: frequency_map[k], reverse=True)
        return sorted_keywords[:max_keywords]