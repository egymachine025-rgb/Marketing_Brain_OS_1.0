"""
Tests for Telegram Acquisition Layer
=====================================
No AI. Pure Python.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from datetime import datetime

# Handle imports - works both as module and standalone
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from marketing_brain_os.raw_repository import RawRepository
from marketing_brain_os.media_repository import MediaRepository
from marketing_brain_os.telegram_acquisition import TelegramAcquisition, AcquisitionConfig, ScanState


class TestRawRepository(unittest.TestCase):
    """Test RawRepository functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo = RawRepository(base_path=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load(self):
        """Test saving and loading a message."""
        msg = {
            "message_id": 42,
            "channel": "@test_channel",
            "date": "2024-01-15T10:30:00",
            "text": "Hello world",
            "views": 100,
            "forwards": 5,
        }
        path = self.repo.save(msg)
        self.assertTrue(os.path.exists(path))

        loaded = self.repo.load("@test_channel", 42)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["message_id"], 42)
        self.assertEqual(loaded["text"], "Hello world")

    def test_exists(self):
        """Test existence check."""
        self.assertFalse(self.repo.exists("@test", 1))
        self.repo.save({"message_id": 1, "channel": "@test", "text": "x"})
        self.assertTrue(self.repo.exists("@test", 1))
        self.assertFalse(self.repo.exists("@test", 2))

    def test_last_message(self):
        """Test last message tracking."""
        self.assertEqual(self.repo.last_message("@test"), 0)
        self.repo.save({"message_id": 10, "channel": "@test", "text": "a"})
        self.assertEqual(self.repo.last_message("@test"), 10)
        self.repo.save({"message_id": 25, "channel": "@test", "text": "b"})
        self.assertEqual(self.repo.last_message("@test"), 25)
        # Lower ID should not update
        self.repo.save({"message_id": 5, "channel": "@test", "text": "c"})
        self.assertEqual(self.repo.last_message("@test"), 25)

    def test_list_messages(self):
        """Test listing message IDs."""
        for i in [3, 1, 5, 2]:
            self.repo.save({"message_id": i, "channel": "@test", "text": str(i)})
        ids = self.repo.list_messages("@test")
        self.assertEqual(ids, [1, 2, 3, 5])

    def test_count(self):
        """Test message counting."""
        self.assertEqual(self.repo.count("@test"), 0)
        self.repo.save({"message_id": 1, "channel": "@test", "text": "a"})
        self.repo.save({"message_id": 2, "channel": "@test", "text": "b"})
        self.assertEqual(self.repo.count("@test"), 2)

    def test_get_all_channels(self):
        """Test listing all channels."""
        self.repo.save({"message_id": 1, "channel": "@ch1", "text": "a"})
        self.repo.save({"message_id": 1, "channel": "@ch2", "text": "b"})
        channels = self.repo.get_all_channels()
        self.assertIn("ch1", channels)
        self.assertIn("ch2", channels)

    def test_delete_channel(self):
        """Test channel deletion."""
        self.repo.save({"message_id": 1, "channel": "@test", "text": "a"})
        self.assertTrue(self.repo.exists("@test", 1))
        self.repo.delete_channel("@test")
        self.assertFalse(self.repo.exists("@test", 1))

    def test_channel_name_sanitization(self):
        """Test special characters in channel names."""
        self.repo.save({"message_id": 1, "channel": "@channel/name", "text": "a"})
        self.assertTrue(self.repo.exists("@channel/name", 1))


class TestMediaRepository(unittest.TestCase):
    """Test MediaRepository functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo = MediaRepository(base_path=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_temp_file(self, content: bytes = b"test content", ext: str = ".jpg") -> str:
        """Create a temporary file."""
        fd, path = tempfile.mkstemp(suffix=ext)
        os.write(fd, content)
        os.close(fd)
        return path

    def test_save_image(self):
        """Test saving an image file."""
        temp_file = self._create_temp_file(b"fake image data", ".jpg")
        result = self.repo.save(
            channel="@test",
            file_path=temp_file,
            media_type="image",
            message_id=42,
            original_filename="photo.jpg",
        )
        self.assertTrue(result["stored"])
        self.assertTrue(os.path.exists(result["file_path"]))
        self.assertEqual(result["media_type"], "image")
        os.unlink(temp_file)

    def test_deduplication(self):
        """Test duplicate file detection."""
        temp_file = self._create_temp_file(b"duplicate test", ".png")
        result1 = self.repo.save("@test", temp_file, "image", 1)
        self.assertTrue(result1["stored"])

        result2 = self.repo.save("@test", temp_file, "image", 2)
        self.assertFalse(result2["stored"])
        self.assertTrue(result2["duplicate"])
        os.unlink(temp_file)

    def test_exists_by_hash(self):
        """Test hash-based existence check."""
        temp_file = self._create_temp_file(b"hash test", ".pdf")
        result = self.repo.save("@test", temp_file, "document", 1)
        file_hash = result["hash"]
        self.assertTrue(self.repo.exists("@test", file_hash))
        self.assertFalse(self.repo.exists("@test", "nonexistenthash123"))
        os.unlink(temp_file)

    def test_list_media(self):
        """Test listing media files."""
        temp_file = self._create_temp_file(b"list test", ".mp4")
        self.repo.save("@test", temp_file, "video", 1, "video.mp4")
        media = self.repo.list_media("@test")
        self.assertEqual(len(media), 1)
        self.assertEqual(media[0]["media_type"], "video")
        os.unlink(temp_file)

    def test_detect_type(self):
        """Test media type detection from extension."""
        self.assertEqual(self.repo._detect_type("jpg"), "image")
        self.assertEqual(self.repo._detect_type("mp4"), "video")
        self.assertEqual(self.repo._detect_type("pdf"), "document")
        self.assertEqual(self.repo._detect_type("mp3"), "audio")
        self.assertEqual(self.repo._detect_type("unknown"), "document")

    def test_count(self):
        """Test media counting."""
        self.assertEqual(self.repo.count("@test"), 0)
        temp_file = self._create_temp_file(b"count test", ".jpg")
        self.repo.save("@test", temp_file, "image", 1)
        self.assertEqual(self.repo.count("@test"), 1)
        os.unlink(temp_file)

    def test_path(self):
        """Test path resolution."""
        path = self.repo.path("@test", "image", "001_abc.jpg")
        self.assertIn("images", path)
        self.assertIn("test", path)


class TestTelegramAcquisition(unittest.TestCase):
    """Test TelegramAcquisition engine."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = AcquisitionConfig(
            base_data_path=self.temp_dir,
            log_path=os.path.join(self.temp_dir, "telegram.log"),
        )
        self.engine = TelegramAcquisition(self.config)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine.raw_repo)
        self.assertIsNotNone(self.engine.media_repo)
        self.assertEqual(self.engine.config.max_retries, 3)

    def test_scan_state_dataclass(self):
        """Test ScanState dataclass."""
        state = ScanState(channel="@test", last_message_id=10)
        d = state.to_dict()
        self.assertEqual(d["channel"], "@test")
        self.assertEqual(d["last_message_id"], 10)

    def test_ingest_mock_message(self):
        """Test mock message ingestion."""
        msg = {
            "message_id": 100,
            "text": "Mock message",
            "date": datetime.now().isoformat(),
        }
        path = self.engine.ingest_mock_message("@test_channel", msg)
        self.assertTrue(os.path.exists(path))

        loaded = self.engine.raw_repo.load("@test_channel", 100)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["text"], "Mock message")

    def test_ingest_mock_media(self):
        """Test mock media ingestion."""
        fd, temp_file = tempfile.mkstemp(suffix=".jpg")
        os.write(fd, b"fake image data")
        os.close(fd)

        result = self.engine.ingest_mock_media("@test", temp_file, "image", 42)
        self.assertTrue(result["stored"])
        os.unlink(temp_file)

    def test_get_stats_empty(self):
        """Test stats with no scans."""
        stats = self.engine.get_stats()
        self.assertEqual(stats["channels_scanned"], 0)
        self.assertEqual(stats["total_messages"], 0)

    def test_logger_created(self):
        """Test log file creation."""
        self.assertTrue(os.path.exists(self.config.log_path))

    def test_config_defaults(self):
        """Test default configuration."""
        cfg = AcquisitionConfig()
        self.assertEqual(cfg.max_retries, 3)
        self.assertEqual(cfg.retry_delay, 2.0)
        self.assertEqual(cfg.chunk_size, 100)
        self.assertTrue(cfg.download_media)
        self.assertIn("image", cfg.media_types)

    def test_message_to_dict_structure(self):
        """Test message serialization structure."""
        class MockMessage:
            id = 1
            date = datetime.now()
            text = "Test"
            raw_text = "Test"
            views = 100
            forwards = 5
            edit_date = None
            pinned = False
            from_scheduled = False
            silent = False
            post = True
            via_bot_id = None
            grouped_id = None
            media = None
            entities = None
            reply_to = None
            fwd_from = None
            reactions = None

            def to_dict(self):
                return {"id": self.id, "text": self.text}

        msg = MockMessage()
        result = self.engine._message_to_dict(msg, "@test")

        self.assertEqual(result["message_id"], 1)
        self.assertEqual(result["channel"], "@test")
        self.assertEqual(result["text"], "Test")
        self.assertIn("raw_telegram_payload", result)
        self.assertIn("media", result)

    def test_incremental_scan_simulation(self):
        """Simulate incremental scanning behavior."""
        channel = "@incremental_test"

        # First batch: messages 1-5
        for i in range(1, 6):
            self.engine.ingest_mock_message(channel, {
                "message_id": i,
                "text": f"Message {i}",
                "date": datetime.now().isoformat(),
            })

        self.assertEqual(self.engine.raw_repo.last_message(channel), 5)
        self.assertEqual(self.engine.raw_repo.count(channel), 5)

        # Second batch: messages 3-8 (3-5 should be skipped)
        new_count = 0
        for i in range(3, 9):
            if not self.engine.raw_repo.exists(channel, i):
                self.engine.ingest_mock_message(channel, {
                    "message_id": i,
                    "text": f"Message {i}",
                    "date": datetime.now().isoformat(),
                })
                new_count += 1

        self.assertEqual(new_count, 3)  # Only 6, 7, 8 are new
        self.assertEqual(self.engine.raw_repo.count(channel), 8)
        self.assertEqual(self.engine.raw_repo.last_message(channel), 8)


class TestIntegration(unittest.TestCase):
    """Integration tests across all components."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = AcquisitionConfig(
            base_data_path=self.temp_dir,
            log_path=os.path.join(self.temp_dir, "telegram.log"),
        )
        self.engine = TelegramAcquisition(self.config)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_pipeline_mock(self):
        """Test full pipeline with mock data."""
        channel = "@integration_test"

        # Step 1: Ingest messages
        for i in range(1, 4):
            self.engine.ingest_mock_message(channel, {
                "message_id": i,
                "text": f"Post {i}",
                "date": datetime.now().isoformat(),
                "views": i * 10,
                "forwards": i,
            })

        # Step 2: Ingest media
        for i in range(1, 3):
            fd, temp = tempfile.mkstemp(suffix=".jpg")
            os.write(fd, f"image {i}".encode())
            os.close(fd)
            self.engine.ingest_mock_media(channel, temp, "image", i)
            os.unlink(temp)

        # Step 3: Verify raw storage
        self.assertEqual(self.engine.raw_repo.count(channel), 3)
        self.assertEqual(self.engine.raw_repo.last_message(channel), 3)

        # Step 4: Verify media storage
        media = self.engine.media_repo.list_media(channel)
        self.assertEqual(len(media), 2)

        # Step 5: Verify stats
        stats = self.engine.get_stats()
        self.assertEqual(stats["total_messages"], 3)
        self.assertEqual(stats["total_media"], 2)

        # Step 6: Verify log exists
        self.assertTrue(os.path.exists(self.config.log_path))

    def test_directory_structure(self):
        """Verify expected directory structure."""
        channel = "@struct_test"
        self.engine.ingest_mock_message(channel, {
            "message_id": 1,
            "text": "Test",
            "date": datetime.now().isoformat(),
        })

        # Check raw structure
        raw_channel = os.path.join(self.temp_dir, "raw", "struct_test")
        self.assertTrue(os.path.exists(raw_channel))
        self.assertTrue(os.path.exists(os.path.join(raw_channel, "000001.json")))
        self.assertTrue(os.path.exists(os.path.join(raw_channel, "_state.json")))

        # Check media structure
        media_channel = os.path.join(self.temp_dir, "media", "struct_test")
        self.assertTrue(os.path.exists(media_channel))


if __name__ == "__main__":
    unittest.main(verbosity=2)