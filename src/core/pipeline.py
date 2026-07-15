from __future__ import annotations
import logging
from typing import Any
from marketing_brain_os.parser_manager import ParserManager
from marketing_brain_os.product_builder import ProductBuilder
from marketing_brain_os.normalizer import ProductNormalizer

logger = logging.getLogger("MarketingBrainOS.Pipeline")


class PipelineResult:
    """
    Data transfer object capturing the terminal status of an ingestion run.
    """
    def __init__(
        self, 
        success: bool, 
        status_message: str, 
        product_state: Any = None, 
        is_duplicate: bool = False
    ) -> None:
        self.success = success
        self.status_message = status_message
        self.product_state = product_state
        self.is_duplicate = is_duplicate


class MVPPipeline:
    """
    Orchestration pipeline coordinating state transformations from raw messages
    into persistent normalized domain models and visual metric updates.
    """
    def __init__(
        self,
        product_repository: Any,
        dashboard_repository: Any
    ) -> None:
        self.product_repo = product_repository
        self.dashboard_repo = dashboard_repository
        
        # Instantiate stateless workers
        self.parser_manager = ParserManager()
        self.product_builder = ProductBuilder()
        self.normalizer = ProductNormalizer()

    async def process(self, raw_message: Any) -> PipelineResult:
        try:
            # 1. Extraction of Raw Message Content
            raw_text = getattr(raw_message, "content_text", "") or ""
            parse_result = self.parser_manager.parse_raw_content(raw_text)

            # 2. Schema Object Construction
            product = self.product_builder.build_from_telegram(raw_message, parse_result)
            if not product:
                return PipelineResult(
                    success=False,
                    status_message="Pipeline execution aborted: Product building failed."
                )

            # 3. Canonical Transformation & Standardization
            normalized_product = self.normalizer.normalize_product(product)

            # 4. Identification via Unique SHA-256 Fingerprint
            fingerprint = getattr(normalized_product, "fingerprint", None)

            # 5. Conflict Resolution & Duplication Detection
            existing_product = await self.product_repo.get_by_fingerprint(fingerprint)
            if existing_product is not None:
                return PipelineResult(
                    success=True,
                    status_message="Ingestion bypassed: Structural duplicate matches an existing entry.",
                    product_state=existing_product,
                    is_duplicate=True
                )

            # 6. Atomic Persistence Execution
            saved_product = await self.product_repo.save(normalized_product)

            # 7. Relational Metric Aggregations Updates
            stats = await self.dashboard_repo.get_current_statistics()
            
            stats.total_processed_items += 1
            if hasattr(saved_product, "price"):
                total = stats.total_processed_items
                old_avg = stats.average_product_price
                stats.average_product_price = round(((old_avg * (total - 1)) + saved_product.price) / total, 2)

            await self.dashboard_repo.update_statistics(stats)

            return PipelineResult(
                success=True,
                status_message="Ingestion process completed successfully.",
                product_state=saved_product,
                is_duplicate=False
            )

        except Exception as e:
            logger.error(f"Execution error encountered in MVP pipeline loop: {str(e)}")
            return PipelineResult(
                success=False,
                status_message=f"Pipeline processing failed: {str(e)}"
            )