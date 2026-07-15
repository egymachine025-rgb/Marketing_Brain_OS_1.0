from __future__ import annotations
from dataclasses import dataclass, field
from src.models.base import BaseModel

@dataclass
class DashboardStatistics(BaseModel):
    """
    Consolidated KPI calculations, tracking volumes, average price trends, 
    and ingest velocities across our raw content streams.
    """
    total_processed_items: int = 0
    total_active_campaigns: int = 0
    average_product_price: float = 0.0
    sentiment_index_ratio: float = 0.0  # Normalized score representing overall trend sentiment (-1.0 to 1.0)
    ingestion_rate_per_hour: float = 0.0
    channel_volume_distribution: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.total_processed_items < 0:
            raise ValueError("Total processed items volume cannot resolve as a negative integer.")
        if self.total_active_campaigns < 0:
            raise ValueError("Total active campaigns volume cannot resolve as a negative integer.")
        if self.average_product_price < 0.0:
            raise ValueError("Average product price metric must be a non-negative float value.")
        if not (-1.0 <= self.sentiment_index_ratio <= 1.0):
            raise ValueError("Sentiment index ratio must remain bound between -1.0 and 1.0.")