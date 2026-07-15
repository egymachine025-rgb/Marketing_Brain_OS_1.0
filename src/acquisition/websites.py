from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from src.acquisition.base import BaseAcquisitionRepository

@dataclass(frozen=True)
class WebsiteRawScrape:
    target_url: str
    domain: str
    http_status_code: int
    raw_html_body: str
    headers_captured: dict[str, str]
    scraped_at: datetime

class WebsitesAcquisitionRepository(BaseAcquisitionRepository[WebsiteRawScrape], Protocol):
    """
    Interface establishing systemic behaviors for targeted crawling, public blog reads, and general tracking.
    """
    async def register_target_url(self, url: str) -> bool: ...
    async def execute_immediate_scrape(self, url: str) -> WebsiteRawScrape: ...
    async def fetch_pending_crawl_queue(self, batch_size: int = 10) -> list[str]: ...