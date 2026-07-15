"""
duplicate_engine.py

Duplicate Detection Engine.
No AI. Pure Python.

Input:  Product (dict)
Output: DuplicateResult

Duplicate Levels:
    EXACT   → fingerprint hash exact match
    HIGH    → confidence >= 0.90
    MEDIUM  → confidence >= 0.75
    LOW     → confidence >= 0.60
    NONE    → confidence < 0.60 (New Product)
"""

import os
import json
from typing import Optional

from .fingerprint_engine import FingerprintEngine, compute_similarity


class DuplicateResult:
    """
    Result object for duplicate detection.

    Attributes:
        duplicate (bool): Whether the incoming product is a duplicate.
        level (str): One of "EXACT", "HIGH", "MEDIUM", "LOW", "NONE".
        confidence (float): Similarity score between 0.0 and 1.0.
        matched_product (dict | None): The matching catalog product, if any.
        reason (str): Human-readable explanation of the decision.
    """

    def __init__(
        self,
        duplicate: bool,
        level: str,
        confidence: float,
        matched_product: Optional[dict],
        reason: str,
    ):
        self.duplicate = duplicate
        self.level = level
        self.confidence = confidence
        self.matched_product = matched_product
        self.reason = reason

    def to_dict(self) -> dict:
        """Return a JSON-serializable dict representation."""
        return {
            "duplicate": self.duplicate,
            "level": self.level,
            "confidence": round(self.confidence, 4),
            "matched_product": self.matched_product,
            "reason": self.reason,
        }


class DuplicateEngine:
    """
    Scans a directory of product JSON files and compares incoming
    products against the catalog to detect duplicates.
    """

    THRESHOLDS = {
        "EXACT": 1.0,
        "HIGH": 0.90,
        "MEDIUM": 0.75,
        "LOW": 0.60,
    }

    def __init__(self, data_dir: str = "data/products"):
        """
        Initialize the engine and load the existing product catalog.

        Args:
            data_dir: Path to directory containing product JSON files.
        """
        self.data_dir = data_dir
        self.fingerprint_engine = FingerprintEngine()
        self.catalog = self._load_catalog()

    def check(self, incoming_product: dict) -> DuplicateResult:
        """
        Check if an incoming product is a duplicate of any product
        in the catalog.

        Args:
            incoming_product: Product dict with at least "product_id",
                "listing" (with "title", "price", "category"), and "seller".

        Returns:
            DuplicateResult with duplicate flag, level, confidence,
            matched product (if any), and reason.
        """
        incoming_fp = self.fingerprint_engine.generate(incoming_product)
        incoming_components = self.fingerprint_engine.generate_components(incoming_product)

        best_similarity = 0.0
        best_match_product = None

        for existing in self.catalog:
            existing_fp = self.fingerprint_engine.generate(existing)

            # EXACT: fingerprint hash match
            if incoming_fp == existing_fp:
                return DuplicateResult(
                    duplicate=True,
                    level="EXACT",
                    confidence=1.0,
                    matched_product=existing,
                    reason="Fingerprint hash exact match.",
                )

            # Similarity-based comparison
            existing_components = self.fingerprint_engine.generate_components(existing)
            similarity = compute_similarity(incoming_components, existing_components)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match_product = existing

        level = self._level_from_similarity(best_similarity)

        if level == "NONE":
            return DuplicateResult(
                duplicate=False,
                level="NONE",
                confidence=best_similarity,
                matched_product=None,
                reason=f"Best similarity {best_similarity:.2%} below LOW threshold. New product.",
            )
        else:
            return DuplicateResult(
                duplicate=True,
                level=level,
                confidence=best_similarity,
                matched_product=best_match_product,
                reason=f"Best similarity {best_similarity:.2%} → {level} duplicate.",
            )

    def add_to_catalog(self, product: dict) -> None:
        """
        Add a new product to the catalog and persist it to disk.

        Args:
            product: Product dict. Must contain "product_id".

        Raises:
            ValueError: If product does not have a "product_id".
        """
        product_id = product.get("product_id")
        if not product_id:
            raise ValueError("Product must have a product_id.")

        filepath = os.path.join(self.data_dir, f"{product_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(product, f, indent=2)

        self.catalog.append(product)

    def _load_catalog(self) -> list:
        """Load all product JSON files from data_dir into memory."""
        catalog = []
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
            return catalog

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    catalog.append(json.load(f))
        return catalog

    def _level_from_similarity(self, similarity: float) -> str:
        """Map a similarity score to a duplicate level."""
        if similarity >= self.THRESHOLDS["EXACT"]:
            return "EXACT"
        elif similarity >= self.THRESHOLDS["HIGH"]:
            return "HIGH"
        elif similarity >= self.THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        elif similarity >= self.THRESHOLDS["LOW"]:
            return "LOW"
        else:
            return "NONE"