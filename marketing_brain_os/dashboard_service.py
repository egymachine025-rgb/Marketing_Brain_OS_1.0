from __future__ import annotations
from typing import Any, Dict

# Task 2: Cleaned up duplicate imports, ensuring single source declarations
from src.models.dashboard_statistics import DashboardStatistics
from src.repositories.dashboard import DashboardRepository


class DashboardService:
    """
    Business orchestration facade representing dashboard interactions.
    """
    def __init__(self, repo: DashboardRepository) -> None:
        self.repo = repo

    def get_statistics(self) -> Dict[str, Any]:
        """
        Synchronous method called by Flask app.py.
        Computes statistics directly from repository data.
        """
        products = self.repo.load_all()
        
        total_items = len(products)
        
        # Calculate average price
        prices = [p.get("price", 0) for p in products if p.get("price") is not None]
        avg_price = round(sum(prices) / len(prices), 2) if prices else 0.0
        
        # Channel volume distribution
        channel_dist: Dict[str, int] = {}
        for p in products:
            channel = p.get("source_channel", p.get("channel", "unknown"))
            channel_dist[channel] = channel_dist.get(channel, 0) + 1
        
        return {
            "total_processed_items": total_items,
            "average_product_price": avg_price,
            "channel_volume_distribution": channel_dist
        }

    async def fetch_current_view(self) -> Dict[str, Any]:
        """
        Async method for fetching current dashboard view.
        """
        stats: DashboardStatistics = await self.repo.get_current_statistics()
        return {
            "total_processed_items": stats.total_processed_items,
            "average_product_price": stats.average_product_price,
            "channel_volume_distribution": stats.channel_volume_distribution
        }