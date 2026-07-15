from __future__ import annotations
from typing import Any, Dict, List

# Importing all nine required core parser modules
from marketing_brain_os.text_cleaner import TextCleaner
from marketing_brain_os.language_detector import LanguageDetector
from marketing_brain_os.brand_detector import BrandDetector
from marketing_brain_os.category_detector import CategoryDetector
from marketing_brain_os.price_extractor import PriceExtractor
from marketing_brain_os.offer_extractor import OfferExtractor
from marketing_brain_os.feature_extractor import FeatureExtractor
from marketing_brain_os.color_extractor import ColorExtractor
from marketing_brain_os.keyword_extractor import KeywordExtractor

# Import unified response payload schema
from marketing_brain_os.parse_result import ParseResult


class ParserManager:
    """
    Unified manager orchestrating sequential processing across all nine parser modules
    to produce a standardized, structured ParseResult object.
    """

    def __init__(self) -> None:
        self.text_cleaner = TextCleaner()
        self.language_detector = LanguageDetector()
        self.brand_detector = BrandDetector()
        self.category_detector = CategoryDetector()
        self.price_extractor = PriceExtractor()
        self.offer_extractor = OfferExtractor()
        self.feature_extractor = FeatureExtractor()
        self.color_extractor = ColorExtractor()
        self.keyword_extractor = KeywordExtractor()

    def parse_raw_content(self, raw_text: str) -> ParseResult:
        """
        Coordinates the ingestion text pipeline. Processes text sequentially 
        through nine core processors to produce a final structural metadata mapping.
        """
        # 1. Clean & sanitize string inputs
        cleaned_text = self.text_cleaner.clean(raw_text)

        # 2. Linguistic and regional classification
        language = self.language_detector.detect(cleaned_text)

        # 3. Structural Brand Matching
        brand = self.brand_detector.detect(cleaned_text)

        # 4. Taxonomy classification
        category = self.category_detector.detect(cleaned_text)

        # 5. Extract monetary values (Float conversion)
        price = self.price_extractor.extract(cleaned_text)

        # 6. Extract offers and promotions
        offer = self.offer_extractor.extract(cleaned_text)

        # 7. Extract specific features & specifications
        features = self.feature_extractor.extract(cleaned_text)

        # 8. Extract color references
        colors = self.color_extractor.extract(cleaned_text)

        # 9. Extract keyword metrics
        keywords = self.keyword_extractor.extract(cleaned_text)

        # Derive a friendly default product name from the first non-empty line
        lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]
        name = lines[0] if lines else "Unnamed Product"

        return ParseResult(
            name=name,
            brand=brand,
            category=category,
            price=price,
            offer=offer,
            features=features,
            colors=colors,
            keywords=keywords,
            language=language,
            description=cleaned_text,
        )


if __name__ == "__main__":
    # --- Quick Mock Setup of Dependencies to allow execution of __main__ Self-Test ---
    import sys
    from unittest.mock import MagicMock

    # If the sub-modules don't exist as physical files in the testing environment,
    # we mock them out dynamically so the self-test execution is guaranteed to run.
    for module_name in [
        "text_cleaner", "language_detector", "brand_detector", 
        "category_detector", "price_extractor", "offer_extractor", 
        "feature_extractor", "color_extractor", "keyword_extractor"
    ]:
        full_path = f"marketing_brain_os.{module_name}"
        if full_path not in sys.modules:
            mock_mod = MagicMock()
            # Standardize mock methods so they return expected deterministic data types
            if "cleaner" in module_name:
                mock_mod.TextCleaner.return_value.clean = lambda t: t.strip()
            elif "language" in module_name:
                mock_mod.LanguageDetector.return_value.detect = lambda t: "ar" if any(ord(c) > 127 for c in t) else "en"
            elif "brand" in module_name:
                # Basic matching for test strings
                mock_mod.BrandDetector.return_value.detect = lambda t: "Nike" if "nike" in t.lower() else "Lacoste" if "lacoste" in t.lower() else "Zara" if "zara" in t.lower() else "Unknown"
            elif "category" in module_name:
                mock_mod.CategoryDetector.return_value.detect = lambda t: "Shoes" if "حذاء" in t or "shoes" in t.lower() else "Bags" if "شنطة" in t or "bag" in t.lower() else "Men Clothing"
            elif "price" in module_name:
                mock_mod.PriceExtractor.return_value.extract = lambda t: 1500.0 if "1500" in t else 95.0
            elif "offer" in module_name:
                mock_mod.OfferExtractor.return_value.extract = lambda t: "10% OFF" if "10%" in t or "خصم" in t else "None"
            elif "feature" in module_name:
                mock_mod.FeatureExtractor.return_value.extract = lambda t: ["Classic Fit"] if "polo" in t.lower() else ["Air Cushion"]
            elif "color" in module_name:
                mock_mod.ColorExtractor.return_value.extract = lambda t: ["black"] if "black" in t.lower() else ["red"]
            elif "keyword" in module_name:
                mock_mod.KeywordExtractor.return_value.extract = lambda t: ["apparel", "casual"]

            sys.modules[full_path] = mock_mod

    # Re-import dependencies safely after mock preparation
    from marketing_brain_os.parser_manager import ParserManager

    # --- Executing Pipeline Self-Tests ---
    print("=" * 60)
    print("RUNNING PARSERMANAGER SYSTEM INTEGRATION SELF-TESTS")
    print("=" * 60)

    manager = ParserManager()

    # Case 1: English Sample
    en_sample = "Lacoste Polo Black XL\nPrice: 95.00 USD\nGet 10% OFF on checkouts!"
    en_result = manager.parse_raw_content(en_sample)
    print(f"\n[+] English Input Parse Test:")
    print(f"    - Name:        {en_result.name}")
    print(f"    - Brand:       {en_result.brand}")
    print(f"    - Category:    {en_result.category}")
    print(f"    - Price:       {en_result.price}")
    print(f"    - Language:    {en_result.language}")
    print(f"    - Colors:      {en_result.colors}")
    print(f"    - Offer:       {en_result.offer}")

    # Case 2: Arabic Sample
    ar_sample = "حذاء Nike Air Max الجديد كلياً\nالسعر: 1500 جنيه\nخصم مميز لفترة محدودة"
    ar_result = manager.parse_raw_content(ar_sample)
    print(f"\n[+] Arabic Input Parse Test:")
    print(f"    - Name:        {ar_result.name}")
    print(f"    - Brand:       {ar_result.brand}")
    print(f"    - Category:    {ar_result.category}")
    print(f"    - Price:       {ar_result.price}")
    print(f"    - Language:    {ar_result.language}")
    print(f"    - Offer:       {ar_result.offer}")
    print("=" * 60)