from __future__ import annotations
import re
import math
import hashlib
from typing import Any
from src.models.base import Currency
from marketing_brain_os.product import Product

class ProductNormalizer:
    """
    Pure Python deterministic normalization engine.
    Ensures absolute consistency across unstructured product attributes.
    """

    def __init__(self) -> None:
        # Canonical brand mappings (Lower -> Standard)
        self.brand_registry = {
            "apple": "Apple", "iphone": "Apple", "macbook": "Apple", "ipad": "Apple",
            "sony": "Sony", "playstation": "Sony",
            "samsung": "Samsung", "galaxy": "Samsung",
            "nike": "Nike", "adidas": "Adidas", "adids": "Adidas",
            "microsoft": "Microsoft", "xbox": "Microsoft",
            "amazon": "Amazon", "kindle": "Amazon",
            "tesla": "Tesla"
        }

        # Canonical categories
        self.category_registry = {
            "electronics": "Electronics", "tech": "Electronics", "gadget": "Electronics",
            "apparel": "Apparel", "clothing": "Apparel", "shoes": "Apparel", "fashion": "Apparel",
            "home": "Home & Living", "kitchen": "Home & Living", "furniture": "Home & Living",
            "automotive": "Automotive", "car": "Automotive", "parts": "Automotive"
        }

        # Standard color registry (normalized to lower case)
        self.color_palette = {
            "black", "white", "silver", "gold", "gray", "grey", "space gray", 
            "rose gold", "blue", "green", "red", "yellow", "pink", "purple", "orange"
        }

        # Regular expression to catch numerical units (e.g. "16gb", "10lbs", "2.5m")
        self.unit_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*([a-zA-Z]+)")

    def normalize_brand(self, raw_brand: str) -> str:
        """Standardizes casing and maps colloquial terms to canonical brands."""
        clean = raw_brand.strip().lower()
        if not clean:
            return "Generic"
        return self.brand_registry.get(clean, raw_brand.strip())

    def normalize_category(self, raw_category: str) -> str:
        """Maps varied categories into standardized, clean high-level taxomies."""
        clean = raw_category.strip().lower()
        if not clean:
            return "Other"
        return self.category_registry.get(clean, raw_category.strip().title())

    def normalize_currency(self, raw_currency: Any) -> Currency:
        """Safely parses raw strings/symbols or enums into our Currency enum."""
        if isinstance(raw_currency, Currency):
            return raw_currency

        clean = str(raw_currency).strip().upper()
        symbol_map = {
            "$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY"
        }
        mapped_code = symbol_map.get(clean, clean)

        try:
            return Currency[mapped_code]
        except KeyError:
            return Currency.USD

    def normalize_price(self, raw_price: Any) -> float:
        """Coerces pricing types into highly precise float limits."""
        try:
            val = float(raw_price)
            # Round to 2 decimal places first
            rounded = round(val, 2)
            # If the rounding lost significant value (e.g., 999.987 -> 999.99), 
            # and we're close to a whole number, round up to nearest integer
            if val > rounded and rounded % 1 >= 0.99:
                rounded = math.ceil(val)
            return max(0.0, float(rounded))
        except (ValueError, TypeError):
            return 0.0

    def normalize_colors(self, raw_colors: list[str]) -> list[str]:
        """Maps colors to a standardized lowercase color palette, eliminating duplicates."""
        normalized = set()
        for color in raw_colors:
            clean = color.strip().lower()
            if clean in self.color_palette:
                normalized.add(clean)
            elif "gray" in clean or "grey" in clean:
                normalized.add("gray")
        return sorted(list(normalized))

    def normalize_features(self, raw_features: list[str]) -> list[str]:
        """Cleans syntax, strips empty lines, and normalizes feature strings."""
        normalized = set()
        for feat in raw_features:
            clean = feat.strip().strip("-*•").strip()
            if clean and len(clean) > 2:
                # Standardize sentence capitalization
                normalized.add(clean[0].upper() + clean[1:])
        return sorted(list(normalized))

    def normalize_keywords(self, raw_keywords: list[str]) -> list[str]:
        """Normalizes and filters keyword tags."""
        normalized = set()
        for kw in raw_keywords:
            clean = re.sub(r"[^\w\s-]", "", kw.strip().lower())
            if clean and len(clean) > 1:
                normalized.add(clean)
        return sorted(list(normalized))

    def normalize_units(self, text: str) -> str:
        """
        Normalizes units of measure embedded within text strings.
        Example: "16gb" -> "16 GB", "10lbs" -> "10 lbs", "3.5m" -> "3.5 m"
        """
        def replacer(match: re.Match) -> str:
            value = match.group(1)
            unit = match.group(2).upper()

            # Specific mappings
            if unit == "GB":
                return f"{value} GB"
            if unit == "LBS" or unit == "LB":
                return f"{value} lbs"
            if unit == "M":
                return f"{value} m"
            if unit == "KG":
                return f"{value} kg"

            return f"{value} {match.group(2).lower()}"

        return self.unit_pattern.sub(replacer, text)

    def normalize_product(self, product: Product) -> Product:
        """
        Accepts a dynamic Product instance, normalizes all properties in-place,
        recalculates its core cryptographic fingerprint, and returns it.
        """
        # Normalize simple fields
        product.brand = self.normalize_brand(product.brand)
        product.category = self.normalize_category(product.category)
        product.price = self.normalize_price(product.price)
        product.currency = self.normalize_currency(product.currency)

        # Normalize structural collections
        product.colors = self.normalize_colors(product.colors)
        product.features = self.normalize_features(product.features)

        # Normalize unit representations inside description
        product.description = self.normalize_units(product.description)
        product.name = self.normalize_units(product.name)

        # Recalculate deterministic fingerprint based on newly standardized variables
        normalized_brand = product.brand.strip().lower()
        normalized_name = product.name.strip().lower()
        normalized_cat = product.category.strip().lower()
        normalized_price = f"{product.price:.2f}"
        normalized_curr = product.currency.value

        fingerprint_source = f"{normalized_brand}|{normalized_name}|{normalized_cat}|{normalized_price}|{normalized_curr}"
        product.fingerprint = hashlib.sha256(fingerprint_source.encode("utf-8")).hexdigest()

        return product