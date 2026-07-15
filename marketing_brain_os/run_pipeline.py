from __future__ import annotations
import logging
import sys
import os
from typing import Any, Dict, Optional

# استيراد المكونات الفرعية والمطورة
from marketing_brain_os.parser_manager import ParserManager
from marketing_brain_os.product_builder import ProductBuilder
from marketing_brain_os.normalizer import ProductNormalizer
from marketing_brain_os.fingerprint_engine import FingerprintEngine
from marketing_brain_os.duplicate_engine import DuplicateEngine

# استيراد مستودعات البيانات المحدثة المتزامنة
from marketing_brain_os.product_repository import ProductRepository
from marketing_brain_os.dashboard_repository import DashboardRepository
from marketing_brain_os.raw_repository import RawRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("PipelineEngine")


class IngestionPipeline:
    """
    خط معالجة متزامن (Synchronous) بالكامل يربط بين المكونات بدون async/await وبدون Mocks.
    """

    def __init__(
        self, 
        product_repo: ProductRepository, 
        dashboard_repo: DashboardRepository
    ) -> None:
        self.parser_manager = ParserManager()
        self.product_builder = ProductBuilder()
        self.normalizer = ProductNormalizer()
        self.fingerprint_engine = FingerprintEngine()
        self.duplicate_engine = DuplicateEngine()
        
        self.product_repo = product_repo
        self.dashboard_repo = dashboard_repo

    def process_telegram_message(
        self, 
        raw_message_text: str, 
        telegram_channel: str, 
        telegram_message_id: int
    ) -> Optional[Dict[str, Any]]:
        logger.info(f"Processing message {telegram_message_id} from {telegram_channel}")

        try:
            # 1. ParserManager
            parse_result = self.parser_manager.parse_raw_content(raw_message_text)

            # 2. ProductBuilder
            product = self.product_builder.build_from_parse_result(
                parse_result=parse_result,
                telegram_channel=telegram_channel,
                telegram_message_id=telegram_message_id
            )

            # 3. ProductNormalizer
            normalized_product = self.normalizer.normalize_product(product)

            # 4. FingerprintEngine
            fingerprint = self.fingerprint_engine.generate(normalized_product)
            normalized_product.fingerprint = fingerprint

            # 5. DuplicateEngine
            dup_result = self.duplicate_engine.check(normalized_product)
            if dup_result.duplicate:
                logger.warning(f"Duplicate product blocked. Fingerprint: {fingerprint}")
                return None

            # 6. ProductRepository
            saved_product = self.product_repo.save(normalized_product)

            # 7. DashboardRepository
            self.dashboard_repo.save(saved_product.to_dict())
            logger.info(f"Successfully ingested and saved product ID: {saved_product.id}")

            return saved_product.to_dict()

        except Exception as e:
            logger.error(f"Error executing ingestion flow for message {telegram_message_id}: {e}", exc_info=True)
            return None


if __name__ == "__main__":
    print("=" * 70)
    print("RUNNING PIPELINE AGAINST REAL TELEGRAM DATA STORAGE")
    print("=" * 70)

    # تهيئة المستودعات الحقيقية المتزامنة بالكامل بالمسار الافتراضي الصحيح
    raw_repo = RawRepository()  # يستخدم المسار الافتراضي الصحيح: "data/raw" تلقائياً
    product_repo = ProductRepository()
    dashboard_repo = DashboardRepository()

    pipeline = IngestionPipeline(
        product_repo=product_repo,
        dashboard_repo=dashboard_repo
    )

    channels = raw_repo.get_all_channels()
    if not channels:
        print("[-] No active channels detected in raw storage. Create E2E directories to perform tests.")
    else:
        for channel in channels:
            print(f"\n[*] Auditing channel: {channel}")
            message_ids = raw_repo.list_messages(channel)
            print(f"[*] Found {len(message_ids)} stored messages to process.")
            
            for message_id in message_ids:
                raw_message = raw_repo.load(channel, message_id)
                if raw_message is None:
                    continue
                
                pipeline.process_telegram_message(
                    raw_message_text=raw_message.get("text", ""),
                    telegram_channel=channel,
                    telegram_message_id=message_id,
                )
    print("\n" + "=" * 70)
    print("INGESTION PROCESSING CYCLE COMPLETED")
    print("=" * 70)