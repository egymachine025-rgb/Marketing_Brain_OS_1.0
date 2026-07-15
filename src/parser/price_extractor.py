from __future__ import annotations
import re

class PriceExtractor:
    """
    Extracts absolute pricing values and converts currency symbols 
    into standardized Currency codes.
    """
    def __init__(self) -> None:
        # Matches symbols or codes: $, €, £, ¥, USD, EUR, etc. followed by or preceding decimal values
        self.price_pattern = re.compile(
            r"(?:\$|€|£|¥|USD|EUR|GBP|JPY)\s?\d+(?:[.,]\d{2})?|\d+(?:[.,]\d{2})?\s?(?:\$|€|£|¥|USD|EUR|GBP|JPY)",
            re.IGNORECASE
        )
        self.currency_map = {
            "$": "USD", "USD": "USD",
            "€": "EUR", "EUR": "EUR",
            "£": "GBP", "GBP": "GBP",
            "¥": "JPY", "JPY": "JPY"
        }

    def extract(self, text: str) -> list[dict[str, Any]]:
        matches = self.price_pattern.findall(text)
        results: list[dict[str, Any]] = []
        
        for match in matches:
            # Isolate numerical float elements
            val_match = re.search(r"\d+(?:[.,]\d{2})?", match)
            if not val_match:
                continue
                
            raw_val = val_match.group(0).replace(",", ".")
            try:
                price_val = float(raw_val)
            except ValueError:
                continue

            # Detect corresponding currency context
            currency = "USD"  # Default fallback representation
            for symbol, code in self.currency_map.items():
                if symbol in match.upper():
                    currency = code
                    break
                    
            results.append({
                "value": price_val,
                "currency": currency,
                "raw_match": match
            })
        return results