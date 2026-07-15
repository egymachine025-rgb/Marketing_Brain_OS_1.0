"""
Research Results Management for Marketing Brain OS

This module manages research results including storage, retrieval, and search.
Results are stored in data/research/results.json
"""

import os
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any


@dataclass
class ResearchResult:
    """Dataclass representing a research result."""
    result_id: str
    task_id: Optional[str]  # Associated task ID if any
    title: str
    category: str  # keywords, social_media, competitors, market_research
    data: Dict[str, Any]  # The actual research data
    source: str  # Which tool/source was used
    tags: List[str]
    brand: Optional[str] = None
    channel: Optional[str] = None
    product_id: Optional[str] = None
    created_at: str = None
    notes: Optional[str] = None
    confidence_score: Optional[float] = None  # 0-1 score for data quality

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchResult':
        """Create from dictionary."""
        return cls(**data)


class ResearchResultManager:
    """Manager for research results storage and operations."""

    def __init__(self, data_dir: str = None):
        """
        Initialize the result manager.
        
        Args:
            data_dir: Directory for storing results. Defaults to data/research
        """
        if data_dir is None:
            # Default to project root/data/research
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            data_dir = os.path.join(project_root, "data", "research")
        
        self.data_dir = data_dir
        self.results_file = os.path.join(data_dir, "results.json")
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing results
        self._results: Dict[str, ResearchResult] = {}
        self._load_results()

    def _load_results(self):
        """Load results from JSON file."""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for result_id, result_data in data.items():
                        self._results[result_id] = ResearchResult.from_dict(result_data)
            except Exception as e:
                print(f"Error loading results: {e}")
                self._results = {}

    def _save_results(self):
        """Save results to JSON file."""
        try:
            data = {result_id: result.to_dict() for result_id, result in self._results.items()}
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Error saving results: {e}")

    def save_result(
        self,
        title: str,
        category: str,
        data: Dict[str, Any],
        source: str,
        tags: List[str] = None,
        task_id: Optional[str] = None,
        brand: Optional[str] = None,
        channel: Optional[str] = None,
        product_id: Optional[str] = None,
        notes: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> ResearchResult:
        """
        Save a new research result.
        
        Args:
            title: Result title
            category: Research category (keywords, social_media, competitors, market_research)
            data: The actual research data
            source: Which tool/source was used
            tags: List of tags for filtering
            task_id: Associated task ID if any
            brand: Associated brand (if any)
            channel: Associated channel (if any)
            product_id: Associated product ID (if any)
            notes: Additional notes
            confidence_score: Data quality score (0-1)
            
        Returns:
            Created ResearchResult
        """
        result_id = str(uuid.uuid4())
        
        result = ResearchResult(
            result_id=result_id,
            task_id=task_id,
            title=title,
            category=category,
            data=data,
            source=source,
            tags=tags or [],
            brand=brand,
            channel=channel,
            product_id=product_id,
            notes=notes,
            confidence_score=confidence_score
        )
        
        self._results[result_id] = result
        self._save_results()
        return result

    def get_result(self, result_id: str) -> Optional[ResearchResult]:
        """
        Get a result by ID.
        
        Args:
            result_id: Result ID
            
        Returns:
            ResearchResult or None if not found
        """
        return self._results.get(result_id)

    def search_by_tag(self, tag: str) -> List[ResearchResult]:
        """
        Search results by tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of matching ResearchResult objects
        """
        results = [r for r in self._results.values() if tag in r.tags]
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results

    def search_by_brand(self, brand: str) -> List[ResearchResult]:
        """
        Search results by brand.
        
        Args:
            brand: Brand to search for
            
        Returns:
            List of matching ResearchResult objects
        """
        results = [r for r in self._results.values() if r.brand == brand]
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results

    def search_by_channel(self, channel: str) -> List[ResearchResult]:
        """
        Search results by channel.
        
        Args:
            channel: Channel to search for
            
        Returns:
            List of matching ResearchResult objects
        """
        results = [r for r in self._results.values() if r.channel == channel]
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results

    def search_by_category(self, category: str) -> List[ResearchResult]:
        """
        Search results by category.
        
        Args:
            category: Category to search for
            
        Returns:
            List of matching ResearchResult objects
        """
        results = [r for r in self._results.values() if r.category == category]
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results

    def search_by_product(self, product_id: str) -> List[ResearchResult]:
        """
        Search results by product ID.
        
        Args:
            product_id: Product ID to search for
            
        Returns:
            List of matching ResearchResult objects
        """
        results = [r for r in self._results.values() if r.product_id == product_id]
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results

    def list_results(
        self,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        channel: Optional[str] = None,
        product_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[ResearchResult]:
        """
        List results with optional filtering.
        
        Args:
            category: Filter by category
            brand: Filter by brand
            channel: Filter by channel
            product_id: Filter by product ID
            tags: Filter by tags (must match all)
            limit: Maximum number of results to return
            
        Returns:
            List of filtered ResearchResult objects
        """
        results = list(self._results.values())
        
        if category:
            results = [r for r in results if r.category == category]
        if brand:
            results = [r for r in results if r.brand == brand]
        if channel:
            results = [r for r in results if r.channel == channel]
        if product_id:
            results = [r for r in results if r.product_id == product_id]
        if tags:
            results = [r for r in results if all(tag in r.tags for tag in tags)]
        
        # Sort by created_at (newest first)
        results.sort(key=lambda r: r.created_at, reverse=True)
        
        if limit:
            results = results[:limit]
        
        return results

    def update_result(
        self,
        result_id: str,
        title: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        confidence_score: Optional[float] = None
    ) -> Optional[ResearchResult]:
        """
        Update an existing result.
        
        Args:
            result_id: Result ID
            title: New title
            data: New data
            notes: New notes
            tags: New tags
            confidence_score: New confidence score
            
        Returns:
            Updated ResearchResult or None if not found
        """
        result = self._results.get(result_id)
        if not result:
            return None
        
        if title is not None:
            result.title = title
        if data is not None:
            result.data = data
        if notes is not None:
            result.notes = notes
        if tags is not None:
            result.tags = tags
        if confidence_score is not None:
            result.confidence_score = confidence_score
        
        self._save_results()
        return result

    def delete_result(self, result_id: str) -> bool:
        """
        Delete a result.
        
        Args:
            result_id: Result ID
            
        Returns:
            True if deleted, False if not found
        """
        if result_id in self._results:
            del self._results[result_id]
            self._save_results()
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get result statistics.
        
        Returns:
            Dictionary with result statistics
        """
        total = len(self._results)
        by_category = {}
        by_source = {}
        by_brand = {}
        by_channel = {}
        
        for result in self._results.values():
            by_category[result.category] = by_category.get(result.category, 0) + 1
            by_source[result.source] = by_source.get(result.source, 0) + 1
            if result.brand:
                by_brand[result.brand] = by_brand.get(result.brand, 0) + 1
            if result.channel:
                by_channel[result.channel] = by_channel.get(result.channel, 0) + 1
        
        return {
            "total": total,
            "by_category": by_category,
            "by_source": by_source,
            "by_brand": by_brand,
            "by_channel": by_channel
        }
