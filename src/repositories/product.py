from __future__ import annotations
from typing import Protocol
from marketing_brain_os.product import Product
from src.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product], Protocol):
    """
    Persistence contract governing standardized storage and querying of products.
    """
    async def get_by_fingerprint(self, fingerprint: str) -> Product | None: ...