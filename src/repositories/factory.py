from __future__ import annotations
from typing import Protocol
from src.repositories.market import MarketRepository
from src.repositories.audience import AudienceRepository
from src.repositories.trend import TrendRepository
from src.repositories.analysis import AnalysisRepository
from src.repositories.decision import DecisionRepository
from src.repositories.knowledge import KnowledgeRepository

class RepositoryFactory(Protocol):
    """
    Dependency Injection interface managing transaction safety and 
    centralized structural creation of domain repository structures.
    """
    def create_market_repository(self) -> MarketRepository: ...
    def create_audience_repository(self) -> AudienceRepository: ...
    def create_trend_repository(self) -> TrendRepository: ...
    def create_analysis_repository(self) -> AnalysisRepository: ...
    def create_decision_repository(self) -> DecisionRepository: ...
    def create_knowledge_repository(self) -> KnowledgeRepository: ...