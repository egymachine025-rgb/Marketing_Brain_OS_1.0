from __future__ import annotations
from typing import Protocol
from src.models.analysis import Analysis
from src.repositories.base import BaseRepository

class AnalysisRepository(BaseRepository[Analysis], Protocol):
    """
    Persistence contract storing structured analytical outputs, scoped findings, and core data run metrics.
    """
    async def find_by_scope_prefix(self, scope_query: str) -> list[Analysis]: ...
    async def get_analyses_with_metric_threshold(self, metric_key: str, min_value: float) -> list[Analysis]: ...