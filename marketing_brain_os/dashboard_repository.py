"""
dashboard_repository.py

Data access layer for the dashboard.
Loads products from JSON files. No UI. Pure Backend.
"""

import os
import json
from typing import List, Optional


class DashboardRepository:
    """
    Repository for loading and persisting product data.
    Reads all .json files from a data directory.
    """

    def __init__(self, data_dir: str = "data/products"):
        self.data_dir = data_dir

    def load_all(self) -> List[dict]:
        """Load all product JSON files from data_dir."""
        products = []
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
            return products

        for filename in sorted(os.listdir(self.data_dir)):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    products.append(json.load(f))
        return products

    def load_by_id(self, product_id: str) -> Optional[dict]:
        """Load a single product by its product_id."""
        filepath = os.path.join(self.data_dir, f"{product_id}.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def save(self, product: dict) -> None:
        """Save or overwrite a product JSON file."""
        product_id = product.get("product_id")
        if not product_id:
            raise ValueError("Product must have a product_id.")

        filepath = os.path.join(self.data_dir, f"{product_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(product, f, indent=2)

    def delete(self, product_id: str) -> bool:
        """Delete a product JSON file by product_id. Returns True if deleted."""
        filepath = os.path.join(self.data_dir, f"{product_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def count(self) -> int:
        """Return the number of product JSON files in data_dir."""
        if not os.path.exists(self.data_dir):
            return 0
        return sum(1 for f in os.listdir(self.data_dir) if f.endswith(".json"))

    # ✅ ADD THIS METHOD HERE — INDENTED 4 SPACES (inside the class)
    def get_current_statistics(self):
        """
        Returns raw statistics data.
        Used by the async DashboardService.fetch_current_view()
        """
        products = self.load_all()
        
        prices = [p.get("price", 0) for p in products if p.get("price") is not None]
        avg_price = round(sum(prices) / len(prices), 2) if prices else 0.0
        
        channel_dist = {}
        for p in products:
            channel = p.get("source_channel", p.get("channel", "unknown"))
            channel_dist[channel] = channel_dist.get(channel, 0) + 1
        
        return {
            "total_processed_items": len(products),
            "average_product_price": avg_price,
            "channel_volume_distribution": channel_dist
        }