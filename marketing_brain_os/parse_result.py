from __future__ import annotations
from typing import Any, Dict, List

class ParseResult:
    """
    A unified container representing the structured output of the ParserManager pipeline.
    """

    def __init__(
        self,
        name: str,
        brand: str,
        category: str,
        price: float,
        offer: str,
        features: List[str],
        colors: List[str],
        keywords: List[str],
        language: str,
        description: str,
    ) -> None:
        self.name = name
        self.brand = brand
        self.category = category
        self.price = price
        self.offer = offer
        self.features = features
        self.colors = colors
        self.keywords = keywords
        self.language = language
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the parse result state into a standard Python dictionary.
        """
        return {
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "price": self.price,
            "offer": self.offer,
            "features": self.features,
            "colors": self.colors,
            "keywords": self.keywords,
            "language": self.language,
            "description": self.description,
        }

    def __repr__(self) -> str:
        return f"ParseResult(name={self.name!r}, brand={self.brand!r}, category={self.category!r}, price={self.price})"