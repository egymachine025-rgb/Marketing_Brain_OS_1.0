from __future__ import annotations
from typing import Any, Dict

# Task 3: Modified parser namespaces to point strictly to 'src.parser' from 'src.parsers'
from src.parser.text_cleaner import TextCleaner
from src.parser.brand_detector import BrandDetector
from src.parser.category_detector import CategoryDetector
from src.parser.price_extractor import PriceExtractor
from src.parser.offer_extractor import OfferExtractor
from src.parser.keyword_extractor import KeywordExtractor
from src.parser.feature_extractor import FeatureExtractor
from src.parser.color_extractor import ColorExtractor

class ParserManager:
    """
    Coordinates linear execution across sub-parsers using the updated src.parser namespace structure.
    """
    def __init__(self) -> None:
        self.text_cleaner = TextCleaner()
        self.brand_detector = BrandDetector()
        self.category_detector = CategoryDetector()
        self.price_extractor = PriceExtractor()
        self.offer_extractor = OfferExtractor()
        self.keyword_extractor = KeywordExtractor()
        self.feature_extractor = FeatureExtractor()
        self.color_extractor = ColorExtractor()

    def parse_raw_content(self, raw_text: str) -> Dict[str, Any]:
        cleaned_text = self.text_cleaner.clean(raw_text)
        
        return {
            "name": cleaned_text.split("\n")[0] if cleaned_text else "Unnamed Product",
            "brand": self.brand_detector.detect(cleaned_text),
            "category": self.category_detector.detect(cleaned_text),
            "price": self.price_extractor.extract(cleaned_text),
            "offer": self.offer_extractor.extract(cleaned_text),
            "keywords": self.keyword_extractor.extract(cleaned_text),
            "features": self.feature_extractor.extract(cleaned_text),
            "colors": self.color_extractor.extract(cleaned_text),
            "description": cleaned_text,
        }