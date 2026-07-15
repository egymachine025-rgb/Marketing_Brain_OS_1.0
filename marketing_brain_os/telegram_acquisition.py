"""
Telegram Acquisition Module
===========================
Reliably collects Telegram messages and media with incremental scanning.
No AI. Pure Python.
"""

import os
import sys
import json
import time
import logging
import traceback
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict

# Telegram client imports - these are optional dependencies
try:
    from telethon import TelegramClient
    from telethon.tl.types import (
        Message, MessageMediaPhoto, MessageMediaDocument,
        DocumentAttributeFilename, DocumentAttributeVideo,
        PeerChannel, Channel
    )
    from telethon.errors import (
        FloodWaitError, SessionPasswordNeededError,
        RPCError, NetworkMigrateError, PhoneMigrateError,
        TimeoutError as TGTimeoutError
    )
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    # Stub classes for type hints when telethon is not installed
    class TelegramClient:
        pass
    class Message:
        pass

# Handle imports - works both as package module and standalone
try:
    from .raw_repository import RawRepository
    from .media_repository import MediaRepository
except ImportError:
    from raw_repository import RawRepository
    from media_repository import MediaRepository


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class AcquisitionConfig:
    """Configuration for Telegram acquisition."""
    api_id: int = 0
    api_hash: str = ""
    session_name: str = "telegram_acquisition"
    phone: str = ""
    base_data_path: str = "data"
    log_path: str = "logs/telegram.log"
    max_retries: int = 3
    retry_delay: float = 2.0
    flood_wait_buffer: int = 30
    download_media: bool = True
    media_types: List[str] = None
    chunk_size: int = 100
    request_delay: float = 0.5
    timeout_seconds: int = 60

    def __post_init__(self):
        if self.media_types is None:
            self.media_types = ["image", "video", "document"]


# ---------------------------------------------------------------------------
# Logger Setup
# ---------------------------------------------------------------------------

def setup_logger(log_path: str) -> logging.Logger:
    """Configure acquisition logger."""
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)

    # Use a logger name unique to this log_path (not a single shared global
    # name). logging.getLogger() returns the SAME object for the same name
    # across the whole process, so a shared name meant a second
    # TelegramAcquisition instance pointing at a different log_path (e.g. a
    # different test's temp directory) would find handlers already attached
    # and skip creating its own file - silently never writing its log file.
    logger = logging.getLogger(f"telegram_acquisition.{os.path.abspath(log_path)}")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # File handler
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    file_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(file_fmt)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(levelname)s: %(message)s")
    ch.setFormatter(console_fmt)
    logger.addHandler(ch)

    return logger


# ---------------------------------------------------------------------------
# Scan State
# ---------------------------------------------------------------------------

@dataclass
class ScanState:
    """Tracks scan progress per channel."""
    channel: str = ""
    last_message_id: int = 0
    total_downloaded: int = 0
    media_downloaded: int = 0
    errors: int = 0
    started_at: str = ""
    finished_at: str = ""
    status: str = "idle"  # idle, running, completed, failed

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Telegram Acquisition Engine
# ---------------------------------------------------------------------------

class TelegramAcquisition:
    """
    Main acquisition engine for Telegram messages and media.

    Features:
        - Incremental scanning (never download twice)
        - Raw JSON storage
        - Media download with deduplication
        - Retry logic with exponential backoff
        - Comprehensive error handling
        - Detailed logging
    """

    def __init__(self, config: AcquisitionConfig = None):
        """
        Initialize acquisition engine.

        Args:
            config: AcquisitionConfig instance.
        """
        self.config = config or AcquisitionConfig()
        self.logger = setup_logger(self.config.log_path)
        self.raw_repo = RawRepository(os.path.join(self.config.base_data_path, "raw"))
        self.media_repo = MediaRepository(os.path.join(self.config.base_data_path, "media"))
        self.client: Optional[TelegramClient] = None
        self._scan_states: Dict[str, ScanState] = {}

        if not TELETHON_AVAILABLE:
            self.logger.warning("Telethon not installed. Install with: pip install telethon")

    # -----------------------------------------------------------------------
    # Connection
    # -----------------------------------------------------------------------

    async def connect(self) -> bool:
        """
        Connect to Telegram.

        Returns:
            True if connected successfully.
        """
        if not TELETHON_AVAILABLE:
            self.logger.error("Telethon library required. Install: pip install telethon")
            return False

        if not self.config.api_id or not self.config.api_hash:
            self.logger.error("API ID and API Hash required")
            return False

        self.logger.info("=" * 50)
        self.logger.info("CONNECTING TO TELEGRAM")
        self.logger.info(f"Session: {self.config.session_name}")

        try:
            self.client = TelegramClient(
                self.config.session_name,
                self.config.api_id,
                self.config.api_hash,
                timeout=self.config.timeout_seconds,
            )
            await self.client.connect()

            if not await self.client.is_user_authorized():
                self.logger.info("Authorization required")
                if self.config.phone:
                    await self.client.send_code_request(self.config.phone)
                    self.logger.info(f"Login code sent to {self.config.phone}")
                else:
                    self.logger.error("Phone number required for authorization")
                    return False

            me = await self.client.get_me()
            self.logger.info(f"Connected as: {me.first_name} (@{me.username})")
            self.logger.info("=" * 50)
            return True

        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            self.logger.debug(traceback.format_exc())
            return False

    async def disconnect(self):
        """Disconnect from Telegram."""
        if self.client:
            await self.client.disconnect()
            self.logger.info("Disconnected from Telegram")

    # -----------------------------------------------------------------------
    # Core Scanning
    # -----------------------------------------------------------------------

    async def scan_channel(self, channel: str,
                           message_handler: Callable = None,
                           media_handler: Callable = None) -> ScanState:
        """
        Scan a single channel incrementally.

        Args:
            channel: Channel username or ID (e.g., "@channelname").
            message_handler: Optional callback for each message.
            media_handler: Optional callback for each media file.

        Returns:
            ScanState with results.
        """
        state = ScanState(
            channel=channel,
            started_at=datetime.now().isoformat(),
            status="running",
        )
        self._scan_states[channel] = state

        self.logger.info("-" * 50)
        self.logger.info(f"SCAN STARTED: {channel}")

        # Get last known message ID
        last_id = self.raw_repo.last_message(channel)
        state.last_message_id = last_id
        self.logger.info(f"Resuming from message_id: {last_id}")

        if not self.client or not await self.client.is_user_authorized():
            self.logger.error("Not connected to Telegram")
            state.status = "failed"
            state.finished_at = datetime.now().isoformat()
            return state

        # Resolve channel entity
        entity = None
        for attempt in range(self.config.max_retries):
            try:
                entity = await self.client.get_entity(channel)
                break
            except Exception as e:
                self.logger.warning(f"Resolve attempt {attempt + 1}/{self.config.max_retries} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    await self._delay(self.config.retry_delay * (attempt + 1))
                else:
                    self.logger.error(f"Failed to resolve channel {channel}: {e}")
                    state.status = "failed"
                    state.finished_at = datetime.now().isoformat()
                    return state

        # Fetch messages incrementally
        messages_downloaded = 0
        media_downloaded = 0
        errors = 0

        try:
            # Iterate messages starting after last_message_id
            async for message in self.client.iter_messages(
                entity,
                min_id=last_id,
                reverse=True,  # Oldest first
                limit=None,
            ):
                try:
                    # Skip if already exists
                    if self.raw_repo.exists(channel, message.id):
                        self.logger.debug(f"Skipping existing message {message.id}")
                        continue

                    # Build raw payload
                    raw = self._message_to_dict(message, channel)

                    # Save raw message
                    saved_path = self.raw_repo.save(raw)
                    messages_downloaded += 1
                    state.total_downloaded = messages_downloaded

                    self.logger.info(
                        f"[{channel}] Message {message.id} saved | "
                        f"Total: {messages_downloaded}"
                    )

                    # Update last message ID
                    if message.id > state.last_message_id:
                        state.last_message_id = message.id

                    # Handle media
                    if self.config.download_media and message.media:
                        media_result = await self._download_media(
                            message, channel, media_handler
                        )
                        if media_result.get("stored"):
                            media_downloaded += 1
                            state.media_downloaded = media_downloaded

                    # Custom message handler
                    if message_handler:
                        try:
                            message_handler(raw)
                        except Exception as e:
                            self.logger.warning(f"Message handler error: {e}")

                    # Rate limiting
                    await self._delay(self.config.request_delay)

                except Exception as e:
                    errors += 1
                    state.errors = errors
                    self.logger.error(f"Error processing message {message.id}: {e}")
                    self.logger.debug(traceback.format_exc())
                    if errors > 50:
                        self.logger.error("Too many errors, stopping scan")
                        break

        except Exception as e:
            self.logger.error(f"Scan loop error: {e}")
            self.logger.debug(traceback.format_exc())
            state.status = "failed"

        state.finished_at = datetime.now().isoformat()
        state.status = "completed" if state.status != "failed" else "failed"

        self.logger.info(f"SCAN FINISHED: {channel}")
        self.logger.info(f"  Messages downloaded: {messages_downloaded}")
        self.logger.info(f"  Media downloaded: {media_downloaded}")
        self.logger.info(f"  Errors: {errors}")
        self.logger.info(f"  Last message ID: {state.last_message_id}")
        self.logger.info("-" * 50)

        return state

    async def scan_channels(self, channels: List[str]) -> Dict[str, ScanState]:
        """
        Scan multiple channels sequentially.

        Args:
            channels: List of channel names/IDs.

        Returns:
            Dict of channel -> ScanState.
        """
        self.logger.info("=" * 50)
        self.logger.info("MULTI-CHANNEL SCAN STARTED")
        self.logger.info(f"Channels: {len(channels)}")
        self.logger.info("=" * 50)

        results = {}
        for channel in channels:
            try:
                result = await self.scan_channel(channel)
                results[channel] = result
            except Exception as e:
                self.logger.error(f"Channel {channel} scan failed: {e}")
                results[channel] = ScanState(
                    channel=channel,
                    status="failed",
                    errors=1,
                    finished_at=datetime.now().isoformat(),
                )
            # Brief pause between channels
            await self._delay(2.0)

        self.logger.info("=" * 50)
        self.logger.info("MULTI-CHANNEL SCAN COMPLETED")
        total_msgs = sum(s.total_downloaded for s in results.values())
        total_media = sum(s.media_downloaded for s in results.values())
        total_errors = sum(s.errors for s in results.values())
        self.logger.info(f"Total messages: {total_msgs}")
        self.logger.info(f"Total media: {total_media}")
        self.logger.info(f"Total errors: {total_errors}")
        self.logger.info("=" * 50)

        return results

    # -----------------------------------------------------------------------
    # Media Download
    # -----------------------------------------------------------------------

    async def _download_media(self, message: Message, channel: str,
                              handler: Callable = None) -> Dict[str, Any]:
        """
        Download media from a message.

        Args:
            message: Telegram message object.
            channel: Channel name.
            handler: Optional callback.

        Returns:
            Result dict from MediaRepository.save().
        """
        if not message.media:
            return {"stored": False}

        # Determine media type
        media_type = self._detect_media_type(message)
        if media_type not in self.config.media_types:
            return {"stored": False, "reason": "type_filtered"}

        # Download to temp location
        temp_dir = os.path.join(self.config.base_data_path, ".temp")
        os.makedirs(temp_dir, exist_ok=True)

        for attempt in range(self.config.max_retries):
            try:
                temp_path = await self.client.download_media(
                    message.media,
                    file=os.path.join(temp_dir, f"{message.id}_"),
                )

                if not temp_path or not os.path.exists(temp_path):
                    return {"stored": False, "reason": "download_failed"}

                # Get original filename
                original_name = self._get_original_filename(message)

                # Save to repository
                result = self.media_repo.save(
                    channel=channel,
                    file_path=temp_path,
                    media_type=media_type,
                    message_id=message.id,
                    original_filename=original_name,
                )

                # Cleanup temp
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

                if result.get("stored"):
                    self.logger.info(
                        f"  Media saved: {result.get('relative_path')} "
                        f"({result.get('size_bytes', 0)} bytes)"
                    )

                # Custom handler
                if handler:
                    try:
                        handler(result)
                    except Exception as e:
                        self.logger.warning(f"Media handler error: {e}")

                return result

            except FloodWaitError as e:
                wait = e.seconds + self.config.flood_wait_buffer
                self.logger.warning(f"FloodWait: sleeping {wait}s")
                await self._delay(wait)
                if attempt == self.config.max_retries - 1:
                    return {"stored": False, "reason": "flood_wait_exceeded"}

            except Exception as e:
                self.logger.warning(f"Media download attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    await self._delay(self.config.retry_delay * (attempt + 1))
                else:
                    return {"stored": False, "reason": str(e)}

        return {"stored": False, "reason": "max_retries"}

    def _detect_media_type(self, message: Message) -> str:
        """Detect media type from message."""
        if hasattr(message, 'media'):
            media = message.media
            if hasattr(media, 'photo'):
                return "image"
            if hasattr(media, 'document'):
                doc = media.document
                mime = getattr(doc, 'mime_type', '')
                if mime.startswith('video/'):
                    return "video"
                if mime.startswith('audio/'):
                    return "audio"
                if mime.startswith('image/'):
                    return "image"
                return "document"
        return "document"

    def _get_original_filename(self, message: Message) -> Optional[str]:
        """Extract original filename from message."""
        if hasattr(message, 'media') and hasattr(message.media, 'document'):
            doc = message.media.document
            for attr in getattr(doc, 'attributes', []):
                if hasattr(attr, 'file_name'):
                    return attr.file_name
        return None

    # -----------------------------------------------------------------------
    # Message Serialization
    # -----------------------------------------------------------------------

    def _message_to_dict(self, message: Message, channel: str) -> Dict[str, Any]:
        """
        Convert Telegram message to serializable dict.

        Args:
            message: Telegram Message object.
            channel: Channel identifier.

        Returns:
            Dict with all message fields.
        """
        result = {
            "message_id": message.id,
            "channel": channel,
            "date": message.date.isoformat() if message.date else None,
            "text": message.text or "",
            "raw_text": message.raw_text or "",
            "views": getattr(message, 'views', None),
            "forwards": getattr(message, 'forwards', None),
            "edit_date": message.edit_date.isoformat() if getattr(message, 'edit_date', None) else None,
            "is_pinned": getattr(message, 'pinned', False),
            "is_scheduled": getattr(message, 'from_scheduled', False),
            "silent": getattr(message, 'silent', False),
            "post": getattr(message, 'post', False),
            "via_bot_id": getattr(message, 'via_bot_id', None),
            "grouped_id": getattr(message, 'grouped_id', None),
            "media": None,
            "entities": [],
            "reply_to": None,
            "forward": None,
            "reactions": None,
            "raw_telegram_payload": {},
        }

        # Entities (links, mentions, etc.)
        if hasattr(message, 'entities') and message.entities:
            result["entities"] = [
                {
                    "type": type(e).__name__,
                    "offset": e.offset,
                    "length": e.length,
                }
                for e in message.entities
            ]

        # Reply info
        if hasattr(message, 'reply_to') and message.reply_to:
            result["reply_to"] = {
                "reply_to_msg_id": getattr(message.reply_to, 'reply_to_msg_id', None),
                "reply_to_top_id": getattr(message.reply_to, 'reply_to_top_id', None),
            }

        # Forward info
        if hasattr(message, 'fwd_from') and message.fwd_from:
            fwd = message.fwd_from
            result["forward"] = {
                "from_id": str(getattr(fwd, 'from_id', '')),
                "from_name": getattr(fwd, 'from_name', None),
                "date": fwd.date.isoformat() if getattr(fwd, 'date', None) else None,
                "channel_post": getattr(fwd, 'channel_post', None),
            }

        # Reactions
        if hasattr(message, 'reactions') and message.reactions:
            result["reactions"] = [
                {
                    "emoticon": r.reaction.emoticon if hasattr(r.reaction, 'emoticon') else str(r.reaction),
                    "count": r.count,
                }
                for r in getattr(message.reactions, 'results', [])
            ]

        # Media info (without downloading)
        if message.media:
            media_info = {"has_media": True}
            if hasattr(message.media, 'photo'):
                media_info["type"] = "photo"
                photo = message.media.photo
                media_info["photo_id"] = getattr(photo, 'id', None)
                media_info["sizes"] = [
                    {"w": s.w, "h": s.h, "type": s.type}
                    for s in getattr(photo, 'sizes', [])
                    if hasattr(s, 'w')
                ]
            elif hasattr(message.media, 'document'):
                doc = message.media.document
                media_info["type"] = "document"
                media_info["document_id"] = getattr(doc, 'id', None)
                media_info["mime_type"] = getattr(doc, 'mime_type', None)
                media_info["size"] = getattr(doc, 'size', None)
                media_info["attributes"] = [
                    {"type": type(a).__name__, "data": str(a)}
                    for a in getattr(doc, 'attributes', [])
                ]
            elif hasattr(message.media, 'webpage'):
                media_info["type"] = "webpage"
                media_info["url"] = getattr(message.media.webpage, 'url', None)
                media_info["title"] = getattr(message.media.webpage, 'title', None)
            else:
                media_info["type"] = type(message.media).__name__
            result["media"] = media_info

        # Raw payload (for advanced use)
        try:
            result["raw_telegram_payload"] = message.to_dict()
        except Exception:
            result["raw_telegram_payload"] = {"serialization_error": True}

        return result

    # -----------------------------------------------------------------------
    # Utilities
    # -----------------------------------------------------------------------

    async def _delay(self, seconds: float):
        """Async delay helper."""
        await __import__('asyncio').sleep(seconds)

    def get_scan_state(self, channel: str) -> Optional[ScanState]:
        """Get scan state for a channel."""
        return self._scan_states.get(channel)

    def get_all_scan_states(self) -> Dict[str, ScanState]:
        """Get all scan states."""
        return dict(self._scan_states)

    def get_stats(self) -> Dict[str, Any]:
        """Get acquisition statistics.

        total_messages/total_media reflect actual persisted storage (raw_repo
        / media_repo), not just live scan sessions - scan_states only track
        messages seen during a real scan_channel() run, so relying on them
        alone reports 0 for data ingested via ingest_mock_message/
        ingest_mock_media (used in tests, and potentially other ingestion
        paths added later).
        """
        raw_stats = self.raw_repo.get_stats()
        total_media = sum(
            len(self.media_repo.list_media(ch))
            for ch in self.raw_repo.get_all_channels()
        )
        return {
            "channels_scanned": len(self._scan_states),
            "total_messages": raw_stats["total_messages"],
            "total_media": total_media,
            "total_errors": sum(s.errors for s in self._scan_states.values()),
            "raw_storage": raw_stats,
            "media_storage": {
                "channels": len(self.media_repo.list_media("")),
            },
        }

    # -----------------------------------------------------------------------
    # Standalone mode (without Telegram - for testing/import)
    # -----------------------------------------------------------------------

    def ingest_mock_message(self, channel: str, message: Dict[str, Any]) -> str:
        """
        Ingest a mock message (for testing without Telegram).

        Args:
            channel: Channel name.
            message: Message dict with at least 'message_id'.

        Returns:
            Path to saved file.
        """
        message["channel"] = channel
        # Ensure the media directory structure exists for this channel too,
        # even if no media arrives with this particular message.
        self.media_repo._channel_dir(channel)
        return self.raw_repo.save(message)

    def ingest_mock_media(self, channel: str, file_path: str,
                          media_type: str = "image",
                          message_id: int = 0) -> Dict[str, Any]:
        """
        Ingest a mock media file (for testing).

        Args:
            channel: Channel name.
            file_path: Path to file.
            media_type: Media type.
            message_id: Associated message ID.

        Returns:
            Result from MediaRepository.save().
        """
        return self.media_repo.save(
            channel=channel,
            file_path=file_path,
            media_type=media_type,
            message_id=message_id,
        )