"""
fingerprint_engine.py

Generates deterministic fingerprints from Product objects.
No AI. Pure Python.
"""

import hashlib
import re


class FingerprintEngine:
    """
    Generates a fingerprint from:
    - brand
    - category
    - normalized_name
    - price_range
    - model (if exists)
    """

    PRICE_BUCKETS = [
        (0, 50),
        (50, 100),
        (100, 250),
        (250, 500),
        (500, 1000),
        (1000, 2000),
        (2000, 5000),
        (5000, float('inf')),
    ]

    # Map product name keywords to brand (when brand not explicitly in title)
    IMPLICIT_BRANDS = {
        "iphone": "apple",
        "ipad": "apple",
        "macbook": "apple",
        "imac": "apple",
        "airpods": "apple",
        "galaxy": "samsung",
        "pixel": "google",
        "playstation": "sony",
        "xbox": "microsoft",
        "thinkpad": "lenovo",
        "eos": "canon",
    }

    def __init__(self):
        pass

    def generate(self, product: dict) -> str:
        """
        Generate a fingerprint string from a product dictionary.
        Returns a hex digest (SHA-256 of normalized components).
        """
        brand = self._extract_brand(product)
        category = self._extract_category(product)
        normalized_name = self._normalize_name(product)
        price_range = self._bucket_price(product)
        model = self._extract_model(product)

        fingerprint_raw = f"{brand}|{category}|{normalized_name}|{price_range}|{model}"
        fingerprint_hash = hashlib.sha256(fingerprint_raw.encode('utf-8')).hexdigest()

        return fingerprint_hash

    def generate_components(self, product: dict) -> dict:
        """
        Return the raw fingerprint components (for debugging/similarity calc).
        """
        return {
            "brand": self._extract_brand(product),
            "category": self._extract_category(product),
            "normalized_name": self._normalize_name(product),
            "price_range": self._bucket_price(product),
            "model": self._extract_model(product),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_brand(self, product: dict) -> str:
        """Extract brand from listing title or seller metadata."""
        title = self._get_title(product)
        title_lower = title.lower()

        # Check explicit brands first
        brands = [
            "apple", "samsung", "sony", "canon", "nikon", "fujifilm",
            "nintendo", "microsoft", "dell", "hp", "lenovo", "asus",
            "google", "oneplus", "xiaomi", "lg", "bose", "jbl",
            "logitech", "razer", "corsair", "amd", "intel", "nvidia"
        ]
        for brand in brands:
            if brand in title_lower:
                return brand

        # Check implicit brand mapping
        for keyword, brand in self.IMPLICIT_BRANDS.items():
            if keyword in title_lower:
                return brand

        return "unknown"

    def _extract_category(self, product: dict) -> str:
        """Extract category from product listing."""
        return product.get("listing", {}).get("category", "uncategorized").lower()

    def _normalize_name(self, product: dict) -> str:
        """
        Normalize product name:
        - lowercase
        - remove punctuation
        - remove common filler words
        - sort tokens alphabetically for consistency
        """
        title = self._get_title(product)
        title = title.lower()
        title = re.sub(r"[^a-z0-9\s]", "", title)

        filler = {
            "selling", "sell", "for", "sale", "used", "new", "like",
            "excellent", "good", "perfect", "condition", "obo", "firm",
            "includes", "include", "with", "and", "the", "a", "an",
            "original", "box", "charger", "cable", "case", "strap",
            "battery", "batteries", "only", "local", "pickup", "minor",
            "wear", "corner", "purchased", "warranty", "until", "asking",
            "comes", "shutter", "count", "body", "no", "sensor", "dust",
            "wireless", "noise", "canceling", "canceling", "headphones",
            "black", "white", "midnight", "natural", "titanium", "blue"
        }

        tokens = [t for t in title.split() if t and t not in filler]
        tokens.sort()
        return " ".join(tokens)

    def _bucket_price(self, product: dict) -> str:
        """Bucket price into discrete ranges."""
        price_obj = product.get("listing", {}).get("price")
        if not price_obj:
            return "unknown"
        amount = price_obj.get("amount", 0)
        for low, high in self.PRICE_BUCKETS:
            if low <= amount < high:
                return f"{low}-{high}"
        return "unknown"

    def _extract_model(self, product: dict) -> str:
        """
        Extract model identifier from title.
        Looks for common patterns: alphanumeric model codes, series numbers.
        """
        title = self._get_title(product)
        title_lower = title.lower()
        models = []

        # iPhone patterns
        iphone_match = re.search(r"iphone\s+(\d+)\s*(pro\s+max|pro|max|plus|mini)?", title_lower)
        if iphone_match:
            model_str = f"iphone {iphone_match.group(1)}"
            if iphone_match.group(2):
                model_str += f" {iphone_match.group(2).strip()}"
            models.append(model_str)

        # MacBook patterns
        macbook_match = re.search(r"macbook\s+(air|pro)\s+(m\d+)", title_lower)
        if macbook_match:
            models.append(f"macbook {macbook_match.group(1)} {macbook_match.group(2)}")

        # iPad patterns
        ipad_match = re.search(r"ipad\s+(pro|air|mini)?\s*(\d*)?", title_lower)
        if ipad_match and (ipad_match.group(1) or ipad_match.group(2)):
            models.append(f"ipad {ipad_match.group(1) or ''} {ipad_match.group(2) or ''}".strip())

        # Galaxy patterns
        galaxy_match = re.search(r"galaxy\s+s(\d+)\s*(ultra|plus|fe)?", title_lower)
        if galaxy_match:
            models.append(f"galaxy s{galaxy_match.group(1)} {galaxy_match.group(2) or ''}".strip())

        # Pixel patterns
        pixel_match = re.search(r"pixel\s+(\d+)\s*(pro|xl)?", title_lower)
        if pixel_match:
            models.append(f"pixel {pixel_match.group(1)} {pixel_match.group(2) or ''}".strip())

        # Canon EOS patterns
        eos_match = re.search(r"eos\s+r(\d+)\s*(mark\s+ii|mark\s+iii|ii|iii)?", title_lower)
        if eos_match:
            models.append(f"eos r{eos_match.group(1)} {eos_match.group(2) or ''}".strip())

        # Sony WH patterns
        wh_match = re.search(r"wh-(\d+)xm(\d+)", title_lower)
        if wh_match:
            models.append(f"wh-{wh_match.group(1)}xm{wh_match.group(2)}")

        # Nintendo Switch
        if "switch" in title_lower and "oled" in title_lower:
            models.append("switch oled")
        elif "switch" in title_lower:
            models.append("switch")

        # PlayStation
        ps_match = re.search(r"playstation\s+(\d+)", title_lower)
        if ps_match:
            models.append(f"playstation {ps_match.group(1)}")

        # Xbox
        xbox_match = re.search(r"xbox\s+series\s+([xs])", title_lower)
        if xbox_match:
            models.append(f"xbox series {xbox_match.group(1)}")

        # ThinkPad
        thinkpad_match = re.search(r"thinkpad\s+([xteps])(\d+)", title_lower)
        if thinkpad_match:
            models.append(f"thinkpad {thinkpad_match.group(1)}{thinkpad_match.group(2)}")

        # Storage capacity
        storage_match = re.search(r"\b(\d{2,4})\s*(gb|tb)\b", title_lower)
        if storage_match:
            models.append(f"{storage_match.group(1)}{storage_match.group(2)}")

        return " ".join(models) if models else "none"

    def _get_title(self, product: dict) -> str:
        return product.get("listing", {}).get("title", "")


def compute_similarity(components_a: dict, components_b: dict) -> float:
    """
    Compute weighted similarity between two component dicts.
    Returns 0.0 - 1.0.

    Weights:
    - brand:      20%
    - category:   20%
    - price_range: 20%
    - model:      25%
    - normalized_name: 15% (token Jaccard)
    """
    weights = {
        "brand": 0.20,
        "category": 0.20,
        "price_range": 0.20,
        "model": 0.25,
        "normalized_name": 0.15,
    }

    total_score = 0.0

    for key, weight in weights.items():
        val_a = components_a.get(key, "")
        val_b = components_b.get(key, "")

        if key == "normalized_name":
            set_a = set(val_a.split())
            set_b = set(val_b.split())
            if not set_a and not set_b:
                score = 1.0
            elif not set_a or not set_b:
                score = 0.0
            else:
                intersection = len(set_a & set_b)
                union = len(set_a | set_b)
                score = intersection / union
        elif key == "model":
            # Token-level Jaccard for partial model matching
            set_a = set(val_a.split())
            set_b = set(val_b.split())
            if not set_a and not set_b:
                score = 1.0
            elif not set_a or not set_b:
                score = 0.0
            else:
                intersection = len(set_a & set_b)
                union = len(set_a | set_b)
                score = intersection / union
        else:
            if val_a == val_b and val_a not in ("unknown", "none"):
                score = 1.0
            elif val_a == val_b:
                score = 0.3  # partial credit for matching unknowns/nones
            else:
                score = 0.0

        total_score += score * weight

    return total_score