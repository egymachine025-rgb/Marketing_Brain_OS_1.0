"""
dashboard_backend.py

Consolidated Dashboard Backend.
No UI. Pure Backend.

Responsibilities:
- Load products from repository
- Search, Filter, Sort
- Statistics aggregation
- Newest products
- Duplicate detection report
- Export JSON
"""

import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any


try:
    from .fingerprint_engine import FingerprintEngine, compute_similarity
    from .duplicate_engine import DuplicateEngine
except ImportError:
    from fingerprint_engine import FingerprintEngine, compute_similarity
    from duplicate_engine import DuplicateEngine


class DashboardBackend:
    """
    Single entry-point for all dashboard operations.
    """

    def __init__(self, data_dir: str = "data/products"):
        self.data_dir = data_dir
        self._ensure_dir()

    def _ensure_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

    def _load_all(self) -> List[dict]:
        """Load all product JSON files."""
        products = []
        if not os.path.exists(self.data_dir):
            return products
        for filename in sorted(os.listdir(self.data_dir)):
            if filename.endswith(".json"):
                with open(os.path.join(self.data_dir, filename), "r", encoding="utf-8") as f:
                    products.append(json.load(f))
        return products

    # ------------------------------------------------------------------
    # Count
    # ------------------------------------------------------------------

    def count(self) -> int:
        return len(self._load_all())

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query: str) -> List[dict]:
        query_lower = query.lower()
        results = []
        for product in self._load_all():
            text = self._searchable_text(product)
            if query_lower in text:
                results.append(product)
        return results

    def _searchable_text(self, product: dict) -> str:
        listing = product.get("listing", {})
        parts = [
            product.get("product_id", ""),
            product.get("name") or listing.get("title", ""),
            listing.get("description", ""),
            product.get("category") or listing.get("category", ""),
            listing.get("condition", ""),
            product.get("brand") or "",
            product.get("seller", {}).get("username", ""),
            product.get("seller", {}).get("display_name", ""),
        ]
        return " ".join(str(p) for p in parts).lower()

    # ------------------------------------------------------------------
    # Filter
    # ------------------------------------------------------------------

    def filter(
        self,
        category: Optional[str] = None,
        condition: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[dict]:
        results = []
        for product in self._load_all():
            listing = product.get("listing", {})
            price_obj = listing.get("price")

            category_value = product.get("category") or listing.get("category", "")
            brand_value = product.get("brand")

            if category and category_value.lower() != category.lower():
                continue
            if condition and listing.get("condition", "").lower() != condition.lower():
                continue
            if min_price is not None:
                amount = price_obj.get("amount", 0) if price_obj else 0
                if amount < min_price:
                    continue
            if max_price is not None:
                amount = price_obj.get("amount", 0) if price_obj else 0
                if amount > max_price:
                    continue
            if brand:
                if brand_value:
                    # Product Model field — exact match.
                    if brand.lower() != brand_value.lower():
                        continue
                else:
                    # Legacy record with no brand field: fall back to the
                    # old title-substring heuristic.
                    name_value = product.get("name") or listing.get("title", "")
                    if brand.lower() not in name_value.lower():
                        continue
            if status and product.get("status", "").lower() != status.lower():
                continue

            results.append(product)
        return results

    # ------------------------------------------------------------------
    # Sort
    # ------------------------------------------------------------------

    def sort(self, products: List[dict], by: str = "acquired_at", ascending: bool = False) -> List[dict]:
        def key(p):
            listing = p.get("listing", {})
            if by == "price":
                return listing.get("price", {}).get("amount", 0) or 0
            elif by == "acquired_at":
                return p.get("metadata", {}).get("acquired_at", "")
            elif by == "title":
                return (p.get("name") or listing.get("title", "")).lower()
            elif by == "product_id":
                return p.get("product_id", "")
            return ""
        return sorted(products, key=key, reverse=not ascending)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def statistics(self) -> Dict[str, Any]:
        products = self._load_all()
        total = len(products)
        if total == 0:
            return {
                "total_products": 0, "total_value": 0.0, "average_price": 0.0,
                "min_price": 0.0, "max_price": 0.0,
                "categories": {}, "brands": {}, "conditions": {}, "statuses": {},
            }

        prices = []
        categories = {}
        brands = {}
        conditions = {}
        statuses = {}

        for p in products:
            listing = p.get("listing", {})
            price = listing.get("price", {})
            amount = price.get("amount", 0) if price else 0
            prices.append(amount)

            cat = p.get("category") or listing.get("category", "uncategorized")
            categories[cat] = categories.get(cat, 0) + 1

            brand = p.get("brand")
            if brand:
                brands[brand] = brands.get(brand, 0) + 1

            cond = listing.get("condition", "Unknown")
            conditions[cond] = conditions.get(cond, 0) + 1

            status = p.get("status", "active")
            statuses[status] = statuses.get(status, 0) + 1

        return {
            "total_products": total,
            "total_value": round(sum(prices), 2),
            "average_price": round(sum(prices) / total, 2),
            "min_price": round(min(prices), 2),
            "max_price": round(max(prices), 2),
            "categories": categories,
            "brands": brands,
            "conditions": conditions,
            "statuses": statuses,
        }

    # ------------------------------------------------------------------
    # Newest Products
    # ------------------------------------------------------------------

    def newest(self, limit: int = 10) -> List[dict]:
        products = self._load_all()
        sorted_products = self.sort(products, by="acquired_at", ascending=False)
        return sorted_products[:limit]

    # ------------------------------------------------------------------
    # Duplicate Report
    # ------------------------------------------------------------------

    def duplicate_report(self) -> Dict[str, Any]:
        """Scan catalog and return duplicate analysis."""
        products = self._load_all()
        if len(products) < 2:
            return {"total_products": len(products), "duplicate_groups": [], "duplicate_count": 0}

        dup_engine = DuplicateEngine(data_dir=self.data_dir)
        groups = []
        checked = set()

        for i, a in enumerate(products):
            if i in checked:
                continue
            group = [a]
            for j, b in enumerate(products):
                if i >= j or j in checked:
                    continue
                result = dup_engine.check(b)
                if result.duplicate and result.matched_product:
                    if result.matched_product.get("product_id") == a.get("product_id"):
                        group.append(b)
                        checked.add(j)
            if len(group) > 1:
                checked.add(i)
                groups.append({
                    "products": [p["product_id"] for p in group],
                    "count": len(group),
                    "level": "EXACT",
                })

        return {
            "total_products": len(products),
            "duplicate_groups": groups,
            "duplicate_count": sum(g["count"] - 1 for g in groups),
        }

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export(self, products: Optional[List[dict]] = None, filepath: Optional[str] = None) -> str:
        if products is None:
            products = self._load_all()
        payload = {
            "exported_at": datetime.now().isoformat(),
            "count": len(products),
            "products": products,
        }
        json_str = json.dumps(payload, indent=2)
        if filepath:
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
        return json_str