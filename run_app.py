#!/usr/bin/env python3
"""
Marketing Brain OS — Run Script
================================
Usage:
    python run_app.py                    # Start server
    python run_app.py --init             # Init data + start
    python run_app.py --pipeline         # Run pipeline + start
    python run_app.py --scan             # Scan Telegram channels then start dashboard
    python run_app.py --scan-only        # Scan Telegram channels and exit
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# ── PATH SETUP ──────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

TEMPLATE_CANDIDATES = [
    PROJECT_ROOT / "templates",
    PROJECT_ROOT / "src" / "api" / "templates",
    PROJECT_ROOT / "src" / "templates",
    PROJECT_ROOT / "marketing_brain_os" / "templates",
]

# ── COLORS ──────────────────────────────────────────────────────────
class C:
    G = "\033[92m"; B = "\033[94m"; Y = "\033[93m"
    R = "\033[91m"; C = "\033[96m"; X = "\033[1m"; N = "\033[0m"

def log(m, c=C.B): t = datetime.now().strftime("%H:%M:%S"); print(f"{c}[{t}] {m}{C.N}")
def ok(m): log(m, C.G)
def warn(m): log(m, C.Y)
def err(m): log(m, C.R)
def info(m): log(m, C.C)

# ── TEMPLATE DETECTION ─────────────────────────────────────────────────
def detect_templates_root() -> Path:
    info(f"PROJECT_ROOT = {PROJECT_ROOT}")

    # Try direct discovery by locating the known template file.
    for path in PROJECT_ROOT.rglob("dashboard_profile.html"):
        if path.is_file():
            info(f"Detected dashboard_profile.html at: {path}")
            info(f"Using templates folder: {path.parent}")
            return path.parent

    # Fall back to standard candidate locations.
    for candidate in TEMPLATE_CANDIDATES:
        info(f"Checking candidate templates folder: {candidate}")
        if candidate.is_dir():
            info(f"Found templates folder: {candidate}")
            return candidate

    warn("No templates folder found in standard locations.")
    return PROJECT_ROOT / "templates"

# ── TELEGRAM CONFIGURATION ───────────────────────────────────────────
def load_env_file():
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists() and load_dotenv:
        load_dotenv(dotenv_path=str(env_path))
        info(f"Loaded .env from: {env_path}")
    elif env_path.exists():
        warn(f"Found .env at {env_path} but python-dotenv is not installed")
    else:
        warn(f"No .env file found at {env_path}")


def get_telegram_config_from_env():
    load_env_file()
    api_id = int(os.getenv("TELEGRAM_API_ID", "0") or 0)
    api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
    phone = os.getenv("TELEGRAM_PHONE", "").strip()
    channels = [c.strip() for c in os.getenv("CHANNELS", "").split(",") if c.strip()]
    download_media = os.getenv("DOWNLOAD_MEDIA", "true").lower() != "false"
    return api_id, api_hash, phone, channels, download_media


from marketing_brain_os.telegram_acquisition import AcquisitionConfig, TelegramAcquisition


def scan_telegram(api_id=None, api_hash=None, phone=None, channels=None, download_media=None) -> bool:
    env_api_id, env_api_hash, env_phone, env_channels, env_download_media = get_telegram_config_from_env()
    api_id = api_id or env_api_id
    api_hash = api_hash or env_api_hash
    phone = phone or env_phone
    channels = channels if channels is not None else env_channels
    download_media = download_media if download_media is not None else env_download_media

    info(f"Telegram scan config: api_id={api_id}, api_hash={'set' if api_hash else 'missing'}, phone={'set' if phone else 'unset'}, channels={channels}, download_media={download_media}")

    if not api_id or not api_hash:
        err("❌ Missing Telegram credentials")
        err("Set TELEGRAM_API_ID and TELEGRAM_API_HASH in .env or environment variables")
        err("Expected .env entries:")
        err("  TELEGRAM_API_ID=your_id")
        err("  TELEGRAM_API_HASH=your_hash")
        return False

    if not channels:
        err("❌ No Telegram channels configured")
        err("Set CHANNELS=@channel1,@channel2 in .env or pass --channels")
        return False

    config = AcquisitionConfig(
        api_id=int(api_id),
        api_hash=str(api_hash),
        phone=str(phone) if phone else "",
        base_data_path=str(PROJECT_ROOT / "data"),
        download_media=bool(download_media),
    )

    engine = TelegramAcquisition(config=config)

    async def _run_scan():
        ok("✅ Connecting to Telegram...")
        if not await engine.connect():
            err("❌ Telegram connection failed")
            return False

        ok("✅ Connected. Starting channel scan...")
        await engine.scan_channels(channels)
        ok("✅ Telegram scan completed")
        return True

    try:
        return asyncio.run(_run_scan())
    except Exception as e:
        err(f"❌ Telegram scan error: {e}")
        return False


# ── INIT ────────────────────────────────────────────────────────────
def init_data():
    dirs = ["data/raw/telegram", "data/products", "data/knowledge", 
            "data/knowledge_graph", "data/exports", "data/reports"]
    for d in dirs:
        (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)
        info(f"📁 {d}")

    # Sample data
    ch = PROJECT_ROOT / "data/raw/telegram/EgyStore005"
    ch.mkdir(exist_ok=True)
    msgs = [
        {"message_id": "1", "date": datetime.now(timezone.utc).isoformat(),
         "text": "Nike Air Max\nPrice: 120 USD\nCondition: New\nFeatures: breathable mesh, lightweight"},
        {"message_id": "2", "date": datetime.now(timezone.utc).isoformat(),
         "text": "Apple iPhone 14 Pro\nPrice: 45000 EGP\nCondition: Like New"}
    ]
    for i, m in enumerate(msgs, 1):
        with open(ch / f"msg_{i}.json", "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=2)
    ok("✅ Sample data created")

# ── CHECK ───────────────────────────────────────────────────────────
def check():
    template_root = detect_templates_root()
    paths = {
        "PROJECT_ROOT": PROJECT_ROOT,
        "template_root": template_root,
        "app_py": PROJECT_ROOT / "src" / "api" / "app.py",
        "dashboard": template_root / "dashboard.html",
        "profile": template_root / "dashboard_profile.html",
    }

    info(f"PROJECT_ROOT = {paths['PROJECT_ROOT']}")
    info(f"template_root = {paths['template_root']}")
    info(f"Looking for app.py at: {paths['app_py']}")
    info(f"Looking for dashboard.html at: {paths['dashboard']}")
    info(f"Looking for dashboard_profile.html at: {paths['profile']}")

    missing = [name for name, path in paths.items() if name not in {"PROJECT_ROOT", "template_root"} and not path.exists()]
    if missing:
        err("❌ Missing files:")
        for name in missing:
            err(f"  - {name}: {paths[name]}")
        return False

    ok("✅ All files found")
    return True

# ── START ───────────────────────────────────────────────────────────
def start():
    info("🚀 Starting...")
    os.chdir(PROJECT_ROOT)
    try:
        from src.api.app import app
        ok("✅ Flask loaded")
        print(f"\n{C.G}{C.X}  🌐 http://localhost:5000/{C.N}")
        print(f"{C.G}{C.X}  🌐 http://localhost:5000/profile{C.N}\n")
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        err(f"❌ Failed: {e}"); sys.exit(1)

# ── MAIN ────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--init", action="store_true")
    p.add_argument("--pipeline", action="store_true")
    p.add_argument("--scan", action="store_true", help="Scan Telegram channels before launching the dashboard")
    p.add_argument("--scan-only", action="store_true", help="Scan Telegram channels and exit without starting the dashboard")
    p.add_argument("--channels", default="", help="Override CHANNELS from .env")
    p.add_argument("--api-id", type=int, default=None, help="Override TELEGRAM_API_ID")
    p.add_argument("--api-hash", default=None, help="Override TELEGRAM_API_HASH")
    p.add_argument("--phone", default=None, help="Override TELEGRAM_PHONE")
    p.add_argument("--download-media", default=None, help="Override DOWNLOAD_MEDIA from .env")
    args = p.parse_args()

    print(f"\n{C.C}{C.X}  💚 Marketing Brain OS v1.0{C.N}\n")

    if args.init:
        init_data()

    if args.scan or args.scan_only:
        channels = [c.strip() for c in args.channels.split(",") if c.strip()] if args.channels else None
        download_media = None
        if args.download_media is not None:
            download_media = args.download_media.lower() != "false"

        if not scan_telegram(
            api_id=args.api_id,
            api_hash=args.api_hash,
            phone=args.phone,
            channels=channels,
            download_media=download_media,
        ):
            sys.exit(1)

    if args.scan_only:
        return

    if not check():
        sys.exit(1)
    start()

if __name__ == "__main__": main()