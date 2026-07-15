#!/usr/bin/env python3
"""
Marketing Brain OS — Telegram Pipeline Bot (Fixed Direct Client)
================================================================
Real Telegram Bot that receives messages and feeds them into the Pipeline.

This version initializes Telethon client directly to avoid dependency issues.

Place this file in: src/bot/telegram_bot.py
Run with: python src/bot/telegram_bot.py

Target Channels:
    - @cjfhjch4764gd36e
    - @EgyStore005
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# ── Load .env file ──────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from dotenv import load_dotenv
    env_path = os.path.join(PROJECT_ROOT, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded .env from: {env_path}")
except ImportError:
    pass

# ── Telethon imports ────────────────────────────────────────────────
try:
    from telethon import TelegramClient
    from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument
    from telethon.errors import SessionPasswordNeededError, FloodWaitError
    TELETHON_OK = True
except ImportError:
    TELETHON_OK = False
    print("ERROR: Telethon not installed. Run: pip install telethon")
    sys.exit(1)

# ── Existing Marketing Brain OS imports ─────────────────────────────
from marketing_brain_os.duplicate_engine import DuplicateEngine
from marketing_brain_os.fingerprint_engine import FingerprintEngine
from marketing_brain_os.dashboard_service import DashboardService
from marketing_brain_os.dashboard_repository import DashboardRepository

# ── Logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("MarketingBrainOS.TelegramBot")

# ── Configuration ───────────────────────────────────────────────────
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "products")
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "telegram")
EXPORT_DIR = os.path.join(PROJECT_ROOT, "data", "exports")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "data", "reports")

for d in [DATA_DIR, RAW_DIR, EXPORT_DIR, REPORTS_DIR]:
    os.makedirs(d, exist_ok=True)


class TelegramPipelineBot:
    """Telegram Bot that bridges Telegram messages → Pipeline → Dashboard."""

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        phone: str = "",
        channels: List[str] = None,
        data_path: str = "data",
        auto_pipeline: bool = True,
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.channels = channels or []
        self.auto_pipeline = auto_pipeline
        self.data_path = data_path

        # Direct Telethon client
        session_path = os.path.join(PROJECT_ROOT, "telegram_bot_session")
        self.client = TelegramClient(session_path, api_id, api_hash)

        # Dashboard Setup (Correct initialization order)
        self.dashboard_repo = DashboardRepository(data_dir=DATA_DIR)
        self.dashboard_service = DashboardService(repo=self.dashboard_repo)

        # Stats
        self.stats = {
            "messages_received": 0,
            "products_created": 0,
            "duplicates_found": 0,
            "errors": 0,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

    async def connect(self) -> bool:
        """Connect to Telegram with interactive login."""
        logger.info("=" * 60)
        logger.info("TELEGRAM PIPELINE BOT — CONNECTING")
        logger.info("=" * 60)

        try:
            await self.client.connect()

            if not await self.client.is_user_authorized():
                logger.info("Authorization required")
                if self.phone:
                    await self.client.send_code_request(self.phone)
                    logger.info(f"Login code sent to {self.phone}")

                    # Interactive login
                    code = input("Enter login code from Telegram: ").strip()
                    try:
                        await self.client.sign_in(self.phone, code)
                    except SessionPasswordNeededError:
                        password = input("Enter 2FA password: ").strip()
                        await self.client.sign_in(password=password)
                    logger.info("Authorization successful!")
                else:
                    logger.error("Phone number required for authorization")
                    return False

            me = await self.client.get_me()
            logger.info(f"Connected as: {me.first_name} (@{me.username})")
            logger.info("=" * 60)
            return True

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False

    async def disconnect(self):
        """Disconnect from Telegram."""
        if self.client:
            await self.client.disconnect()
        logger.info("Disconnected from Telegram")

    def _save_raw_message(self, raw_message: Dict[str, Any]):
        """Save raw message in format expected by run_pipeline.py."""
        channel = raw_message.get("channel", "unknown")
        msg_id = raw_message.get("message_id", 0)

        channel_dir = os.path.join(RAW_DIR, channel.replace("@", ""))
        os.makedirs(channel_dir, exist_ok=True)

        filepath = os.path.join(channel_dir, f"{msg_id:06d}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(raw_message, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"  Saved: {filepath}")

    async def scan_channel(self, channel: str):
        """Scan a single channel."""
        logger.info(f"Scanning channel: {channel}")

        try:
            entity = await self.client.get_entity(channel)
            logger.info(f"  Entity resolved: {entity.title if hasattr(entity, 'title') else channel}")

            message_count = 0
            async for message in self.client.iter_messages(entity, limit=100):
                if not message.text:
                    continue

                self.stats["messages_received"] += 1
                message_count += 1

                raw = {
                    "message_id": message.id,
                    "channel": channel,
                    "date": message.date.isoformat() if message.date else datetime.now(timezone.utc).isoformat(),
                    "text": message.text or "",
                    "views": getattr(message, 'views', None),
                    "forwards": getattr(message, 'forwards', None),
                }

                self._save_raw_message(raw)

                # Rate limiting
                await asyncio.sleep(0.5)

            logger.info(f"  Messages downloaded: {message_count}")

        except Exception as e:
            logger.error(f"  Error scanning {channel}: {e}")
            self.stats["errors"] += 1

    def run_pipeline(self):
        """Run the existing pipeline script."""
        logger.info("Running pipeline...")
        try:
            pipeline_script = os.path.join(PROJECT_ROOT, "scripts", "run_pipeline.py")
            if os.path.exists(pipeline_script):
                result = subprocess.run(
                    [sys.executable, pipeline_script],
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT,
                )
                if result.returncode == 0:
                    logger.info("Pipeline completed successfully")
                    # Print pipeline output
                    print(result.stdout)
                else:
                    logger.error(f"Pipeline failed: {result.stderr}")
            else:
                logger.warning(f"Pipeline script not found: {pipeline_script}")
        except Exception as e:
            logger.error(f"Error running pipeline: {e}")

    async def scan(self) -> Dict[str, Any]:
        """Run a single scan cycle on all configured channels."""
        if not self.channels:
            logger.error("No channels configured")
            return {"error": "No channels configured"}

        logger.info(f"Starting scan on {len(self.channels)} channels...")
        for ch in self.channels:
            logger.info(f"  - {ch}")

        for channel in self.channels:
            await self.scan_channel(channel)
            await asyncio.sleep(2)  # Pause between channels

        # Run pipeline after scan
        if self.auto_pipeline:
            self.run_pipeline()

        # Generate report
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stats": self.stats,
        }

        report_path = os.path.join(REPORTS_DIR, "telegram_bot_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info("=" * 60)
        logger.info("SCAN COMPLETE")
        logger.info(f"  Messages: {self.stats['messages_received']}")
        logger.info(f"  Products: {self.stats['products_created']}")
        logger.info(f"  Duplicates: {self.stats['duplicates_found']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info("=" * 60)

        return report

    async def run_continuous(self, interval_seconds: int = 300):
        """Run continuous polling loop."""
        logger.info(f"Starting continuous polling (interval: {interval_seconds}s)")
        try:
            while True:
                await self.scan()
                logger.info(f"Sleeping {interval_seconds}s before next scan...")
                await asyncio.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Stopped by user")


# ── CLI Entry Point ────────────────────────────────────────────────
async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Telegram Pipeline Bot")
    parser.add_argument("--api-id", type=int, default=int(os.getenv("TELEGRAM_API_ID", 0)))
    parser.add_argument("--api-hash", default=os.getenv("TELEGRAM_API_HASH", ""))
    parser.add_argument("--phone", default=os.getenv("TELEGRAM_PHONE", ""))
    parser.add_argument("--channels", default=os.getenv("CHANNELS", ""))
    parser.add_argument("--data-path", default=os.getenv("DATA_PATH", "data"))
    parser.add_argument("--auto-pipeline", type=lambda x: x.lower() == "true",
                        default=os.getenv("PIPELINE_AUTO_RUN", "true").lower() == "true")
    parser.add_argument("--continuous", action="store_true", help="Run continuous polling")
    parser.add_argument("--interval", type=int, default=300, help="Polling interval in seconds")
    args = parser.parse_args()

    if not args.api_id or not args.api_hash:
        print("=" * 60)
        print("ERROR: TELEGRAM_API_ID and TELEGRAM_API_HASH required")
        print("=" * 60)
        print("\nSet in .env file:")
        print("  TELEGRAM_API_ID=your_id")
        print("  TELEGRAM_API_HASH=your_hash")
        print("  TELEGRAM_PHONE=+1234567890")
        print("  CHANNELS=@channel1,@channel2")
        print("=" * 60)
        sys.exit(1)

    channels = [c.strip() for c in args.channels.split(",") if c.strip()] if args.channels else []
    if not channels:
        print("ERROR: No channels specified")
        sys.exit(1)

    print("=" * 60)
    print("TELEGRAM PIPELINE BOT")
    print("=" * 60)
    print(f"API ID:     {args.api_id}")
    print(f"Phone:      {args.phone or 'Not set'}")
    print(f"Channels:   {len(channels)}")
    for ch in channels:
        print(f"  - {ch}")
    print(f"Mode:       {'CONTINUOUS' if args.continuous else 'SINGLE SCAN'}")
    print("=" * 60)

    bot = TelegramPipelineBot(
        api_id=args.api_id,
        api_hash=args.api_hash,
        phone=args.phone,
        channels=channels,
        data_path=args.data_path,
        auto_pipeline=args.auto_pipeline,
    )

    connected = await bot.connect()
    if not connected:
        sys.exit(1)

    try:
        if args.continuous:
            await bot.run_continuous(interval_seconds=args.interval)
        else:
            report = await bot.scan()
            print("\n" + "=" * 60)
            print("FINAL REPORT")
            print("=" * 60)
            print(json.dumps(report, indent=2, default=str))
    finally:
        await bot.disconnect()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())