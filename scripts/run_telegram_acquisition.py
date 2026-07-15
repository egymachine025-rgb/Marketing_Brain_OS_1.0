import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from marketing_brain_os.telegram_acquisition import AcquisitionConfig, TelegramAcquisition

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("AcquisitionRunner")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def load_env() -> None:
    env_path = os.path.join(PROJECT_ROOT, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"Loaded .env from: {env_path}")
    else:
        logger.warning(f"No .env file found at: {env_path}")


async def main() -> None:
    load_env()

    api_id = int(os.getenv("TELEGRAM_API_ID", "0") or 0)
    api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
    phone = os.getenv("TELEGRAM_PHONE", "").strip()
    channels = [c.strip() for c in os.getenv("CHANNELS", "").split(",") if c.strip()]
    download_media = os.getenv("DOWNLOAD_MEDIA", "true").lower() != "false"

    logger.info("Initializing Telegram acquisition pipeline...")

    if not api_id or not api_hash:
        logger.error("Missing TELEGRAM_API_ID or TELEGRAM_API_HASH in .env")
        logger.error("Add entries like:")
        logger.error("  TELEGRAM_API_ID=your_id")
        logger.error("  TELEGRAM_API_HASH=your_hash")
        return

    if not channels:
        logger.error("No CHANNELS configured in .env")
        logger.error("Add an entry like:")
        logger.error("  CHANNELS=@channel1,@channel2")
        return

    config = AcquisitionConfig(
        api_id=api_id,
        api_hash=api_hash,
        phone=phone,
        base_data_path=os.path.join(PROJECT_ROOT, "data"),
        download_media=download_media,
    )

    engine = TelegramAcquisition(config=config)

    try:
        if not await engine.connect():
            logger.error("Telegram connection failed")
            return

        await engine.scan_channels(channels)
    except KeyboardInterrupt:
        logger.info("Acquisition sequence interrupted by user.")
    except Exception as e:
        logger.error(f"Acquisition sequence failed with runtime error: {e}")
    finally:
        await engine.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
