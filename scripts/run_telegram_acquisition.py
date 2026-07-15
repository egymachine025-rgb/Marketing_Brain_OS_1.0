import asyncio
import logging
import sys

# Update this line to use the correct directory namespace (marketing_brain_os)
# and import the class name you actually use below:
from marketing_brain_os.telegram_acquisition import TelegramAcquisition

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("AcquisitionRunner")

async def main() -> None:
    logger.info("Initializing Telegram acquisition pipeline...")
    engine = TelegramAcquisition()  # This now matches the imported class!
    try:
        await engine.start()
    except KeyboardInterrupt:
        logger.info("Acquisition sequence interrupted by user.")
    except Exception as e:
        logger.error(f"Acquisition sequence failed with runtime error: {e}")
    finally:
        await engine.stop()

if __name__ == "__main__":
    async def run_main():
        await main()
    asyncio.run(run_main())