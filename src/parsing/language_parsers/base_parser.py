from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Tuple


class BaseParser(ABC):
    """Abstract base class for language-specific parsing strategies."""

    @abstractmethod
    def extract_price(self, text: str) -> tuple[float | None, str | None, float]:
        ...

    @abstractmethod
    def extract_brand(self, text: str) -> tuple[str | None, float]:
        ...

    @abstractmethod
    def extract_category(self, text: str) -> tuple[str | None, float]:
        ...

    @abstractmethod
    def extract_condition(self, text: str) -> tuple[str | None, float]:
        ...

    @abstractmethod
    def extract_features(self, text: str) -> list[tuple[str, float]]:
        ...

    def _is_not_empty(self, value: str | None) -> bool:
        return bool(value and value.strip())

    def _normalize_confidence(self, score: float) -> float:
        return min(1.0, max(0.0, score))
