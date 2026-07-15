from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Optional
from marketing_brain_os.product import Product
from marketing_brain_os.parse_result import ParseResult


class ProductBuilder:
    """
    Responsible for constructing fully populated, typed Product entities 
    from parsed payload metadata and raw source telemetry.
    """

    def __init__(self) -> None:
        pass

    def build_from_parse_result(
        self, 
        parse_result: ParseResult, 
        telegram_channel: Optional[str] = None,
        telegram_message_id: Optional[int] = None
    ) -> Product:
        """
        Takes a ParseResult instance and optional social-feed telemetry 
        and manufactures a valid domain Product model instance.
        """
        # Ensure mandatory defaults for fallback tracking
        product_name = parse_result.name.strip() if parse_result.name else "Unnamed Product"
        product_brand = parse_result.brand.strip() if parse_result.brand else "Unknown"
        product_category = parse_result.category.strip() if parse_result.category else "Other"
        
        # Instantiate and populate the Product Domain model
        product = Product(
            id=uuid.uuid4(),
            name=product_name,
            brand=product_brand,
            category=product_category,
            language=parse_result.language,
            price=parse_result.price,
            offer=parse_result.offer,
            colors=list(parse_result.colors),
            features=list(parse_result.features),
            keywords=list(parse_result.keywords),
            description=parse_result.description,
            created_at=datetime.utcnow(),
            telegram_channel=telegram_channel,
            telegram_message_id=telegram_message_id
        )

        return product