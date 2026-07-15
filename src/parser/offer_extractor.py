from __future__ import annotations
import re

class OfferExtractor:
    """
    Extracts campaign discounts, percent reductions, and coupon-based structural offers.
    """
    def __init__(self) -> None:
        self.percentage_pattern = re.compile(r"(\d+)\s*%\s*(?:off|discount|sale)", re.IGNORECASE)
        self.bogo_pattern = re.compile(r"\b(buy\s+\d+\s+get\s+\d+\s*(?:free|half\s+price)?|bogo)\b", re.IGNORECASE)
        self.coupon_pattern = re.compile(r"\b(?:use\s+code|coupon|promo\s+code):\s*([A-Z0-9_-]+)\b", re.IGNORECASE)

    def extract(self, text: str) -> dict[str, Any]:
        offers: dict[str, Any] = {
            "discounts": [],
            "bogo_detected": False,
            "promo_codes": []
        }
        
        for match in self.percentage_pattern.finditer(text):
            offers["discounts"].append({
                "type": "percentage",
                "value": float(match.group(1))
            })
            
        if self.bogo_pattern.search(text):
            offers["bogo_detected"] = True
            
        for match in self.coupon_pattern.finditer(text):
            offers["promo_codes"].append(match.group(1))
            
        return offers