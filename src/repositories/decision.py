from __future__ import annotations
import uuid
from typing import Protocol
from src.models.decision import Decision
from src.models.base import DecisionStatus
from src.repositories.base import BaseRepository

class DecisionRepository(BaseRepository[Decision], Protocol):
    """
    Persistence contract monitoring execution summaries, statuses, and links to upstream analyses.
    """
    async def fetch_by_status(self, status: DecisionStatus) -> list[Decision]: ...
    async def get_decisions_linked_to_analysis(self, analysis_id: uuid.UUID) -> list[Decision]: ...