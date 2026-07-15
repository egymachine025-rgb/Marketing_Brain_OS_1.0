from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from marketing_brain_os.product import Product

@dataclass(frozen=True)
class PipelineResult:
    """
    Immutable representation of the execution result of the MVP ingestion run.
    """
    success: bool
    status_message: str
    processed_at: datetime = field(default_factory=datetime.utcnow)
    product_state: Product | None = None
    is_duplicate: bool = False