from __future__ import annotations
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from marketing_brain_os.dashboard_repository import DashboardRepository
from marketing_brain_os.duplicate_engine import DuplicateEngine
from src.models.dashboard_statistics import DashboardStatistics


class DashboardService:
    """Business orchestration facade representing dashboard interactions."""

    def __init__(self, repo: Optional[DashboardRepository] = None, data_dir: Optional[str] = None) -> None:
        if repo is not None:
            self.repo = repo
        elif data_dir is not None:
            self.repo = DashboardRepository(data_dir=data_dir)
        else:
            raise ValueError("DashboardService requires either repo or data_dir")

    def get_all_products(self) -> List[dict]:
        return self.repo.load_all()

    def get_product_by_id(self, product_id: str) -> Optional[dict]:
        return self.repo.load_by_id(product_id)

    def _searchable_text(self, product: dict) -> str:
        listing = product.get("listing", {})
        fields = [
            product.get("product_id", ""),
            product.get("name") or listing.get("title", ""),
            listing.get("description", ""),
            listing.get("category", ""),
            listing.get("condition", ""),
            product.get("brand", ""),
            product.get("seller", {}).get("username", ""),
            product.get("seller", {}).get("display_name", ""),
        ]
        return " ".join(str(field) for field in fields if field).lower()

    def search(self, query: str) -> List[dict]:
        query_lower = query.lower()
        return [product for product in self.get_all_products() if query_lower in self._searchable_text(product)]

    def filter_products(
        self,
        category: Optional[str] = None,
        condition: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[dict]:
        results: List[dict] = []
        for product in self.get_all_products():
            listing = product.get("listing", {})
            price_data = listing.get("price") or {}
            amount = price_data.get("amount", 0) or 0

            category_value = product.get("category") or listing.get("category", "")
            brand_value = product.get("brand")
            status_value = product.get("status", "")

            if category and category_value.lower() != category.lower():
                continue
            if condition and listing.get("condition", "").lower() != condition.lower():
                continue
            if min_price is not None and amount < min_price:
                continue
            if max_price is not None and amount > max_price:
                continue
            if brand:
                if brand_value:
                    if brand.lower() != brand_value.lower():
                        continue
                else:
                    title_value = product.get("name") or listing.get("title", "")
                    if brand.lower() not in title_value.lower():
                        continue
            if status and status_value.lower() != status.lower():
                continue

            results.append(product)
        return results

    def sort_products(self, products: List[dict], sort_by: str = "acquired_at", ascending: bool = False) -> List[dict]:
        def key(product: dict):
            listing = product.get("listing", {})
            if sort_by == "price":
                return listing.get("price", {}).get("amount", 0) or 0
            if sort_by == "title":
                return (product.get("name") or listing.get("title", "")).lower()
            if sort_by == "product_id":
                return product.get("product_id", "")
            return product.get("metadata", {}).get("acquired_at", "")

        return sorted(products, key=key, reverse=not ascending)

    def get_newest_products(self, limit: int = 10) -> List[dict]:
        return self.sort_products(self.get_all_products(), sort_by="acquired_at", ascending=False)[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        products = self.get_all_products()
        total = len(products)

        prices = [
            product.get("listing", {}).get("price", {}).get("amount", 0)
            for product in products
            if isinstance(product.get("listing", {}).get("price", {}), dict)
        ]

        categories: Dict[str, int] = {}
        brands: Dict[str, int] = {}
        conditions: Dict[str, int] = {}
        statuses: Dict[str, int] = {}

        for product in products:
            listing = product.get("listing", {})
            price_data = listing.get("price") or {}
            amount = price_data.get("amount", 0) or 0
            category_value = product.get("category") or listing.get("category") or "uncategorized"
            brand_value = product.get("brand")
            condition_value = listing.get("condition", "Unknown")
            status_value = product.get("status", "active")

            categories[category_value] = categories.get(category_value, 0) + 1
            if brand_value:
                brands[brand_value] = brands.get(brand_value, 0) + 1
            conditions[condition_value] = conditions.get(condition_value, 0) + 1
            statuses[status_value] = statuses.get(status_value, 0) + 1

        return {
            "total_products": total,
            "total_value": round(sum(prices), 2),
            "average_price": round(sum(prices) / total, 2) if total and prices else 0.0,
            "min_price": round(min(prices), 2) if prices else 0.0,
            "max_price": round(max(prices), 2) if prices else 0.0,
            "categories": categories,
            "brands": brands,
            "conditions": conditions,
            "statuses": statuses,
        }

    def duplicate_report(self) -> Dict[str, Any]:
        products = self.get_all_products()
        if len(products) < 2:
            return {"total_products": len(products), "duplicate_groups": [], "duplicate_count": 0}

        engine = DuplicateEngine(data_dir=getattr(self.repo, "data_dir", "data/products"))
        groups: List[dict] = []
        checked = set()

        for i, current in enumerate(products):
            if i in checked:
                continue
            group = [current]
            for j, candidate in enumerate(products):
                if i >= j or j in checked:
                    continue
                result = engine.check(candidate)
                if result.duplicate and result.matched_product and result.matched_product.get("product_id") == current.get("product_id"):
                    group.append(candidate)
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

    def export_json(self, products: Optional[List[dict]] = None, filepath: Optional[str] = None) -> str:
        if products is None:
            products = self.get_all_products()

        payload = {
            "exported_at": datetime.now().isoformat(),
            "count": len(products),
            "products": products,
        }
        json_str = json.dumps(payload, indent=2)
        if filepath:
            directory = os.path.dirname(filepath) or "."
            os.makedirs(directory, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
        return json_str

    async def fetch_current_view(self) -> Dict[str, Any]:
        stats: DashboardStatistics = await self.repo.get_current_statistics()
        return {
            "total_processed_items": stats.total_processed_items,
            "average_product_price": stats.average_product_price,
            "channel_volume_distribution": stats.channel_volume_distribution,
        }
