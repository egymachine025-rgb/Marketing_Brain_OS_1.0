from __future__ import annotations
import re

class FeatureExtractor:
    """
    Extracts structural product features and marketing value claims 
    (e.g., bulleted product benefits or spec indicators).
    """
    def __init__(self) -> None:
        # Match pattern looking for specification keywords like: "resolution", "battery", "waterproof", etc.
        self.spec_indicators = re.compile(
            r"\b(?:waterproof|battery\s+life|warranty|screen|display|resolution|storage|compatible|wireless)\b",
            re.IGNORECASE
        )
        # Matches points structured like: "- Feature" or "* Feature"
        self.bullet_pattern = re.compile(r"^[*-]\s*(.+)$", re.MULTILINE)

    def extract(self, text: str) -> list[str]:
        features: list[str] = []
        
        # 1. Capture explicitly structured list markers
        for match in self.bullet_pattern.finditer(text):
            features.append(match.group(1).strip())
            
        # 2. Extract context lines displaying specific physical hardware specs
        for line in text.splitlines():
            if self.spec_indicators.search(line):
                trimmed = line.strip()
                if trimmed not in features and len(trimmed) < 100:
                    features.append(trimmed)
                    
        return features