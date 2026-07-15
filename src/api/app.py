#!/usr/bin/env python3
"""
Marketing Brain OS — Flask API
==============================
Integrated REST API serving Dashboard, Pipeline, and Telegram Bot.

Place this file in: src/api/app.py
Run with: python src/api/app.py

Endpoints:
    GET  /api/health                  → Health check
    GET  /api/products                → List all products
    GET  /api/products/<id>           → Get single product
    GET  /api/products/search         → Search products
    GET  /api/products/filter         → Filter products
    GET  /api/products/newest         → Newest products
    GET  /api/statistics              → Dashboard statistics
    GET  /api/duplicates              → Duplicate report
    POST /api/pipeline/run            → Run pipeline on raw messages
    POST /api/telegram/scan           → Trigger Telegram scan
    GET  /api/telegram/status         → Telegram scan status
    POST /api/export                  → Export products to JSON
    GET  /api/telegram-sources        → Real-time sources manager data (Custom Added)
"""

import os
import sys
import json
import glob
import asyncio
import threading
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, jsonify, request, Response, render_template
from flask_cors import CORS

# ── Project root resolution ─────────────────────────────────────────
# This works whether run from project root or src/api/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── Existing Marketing Brain OS imports ─────────────────────────────
from marketing_brain_os.dashboard_service import DashboardService
from marketing_brain_os.dashboard_repository import DashboardRepository
from marketing_brain_os.duplicate_engine import DuplicateEngine, DuplicateResult
from marketing_brain_os.fingerprint_engine import FingerprintEngine

# ── Telegram imports (from marketing_brain_os package) ──────────────
from marketing_brain_os.telegram_acquisition import TelegramAcquisition, AcquisitionConfig

# ── Configuration ───────────────────────────────────────────────────
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "products")
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "telegram")
EXPORT_DIR = os.path.join(PROJECT_ROOT, "data", "exports")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "data", "reports")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ── Flask App ───────────────────────────────────────────────────────
app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static"),
)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── Global Service Instances ────────────────────────────────────────
dashboard_repo = DashboardRepository(data_dir=DATA_DIR)
dashboard_service = DashboardService(repo=dashboard_repo)
dup_engine = DuplicateEngine(data_dir=DATA_DIR)

# Telegram engine (initialized on demand)
telegram_engine: Optional[TelegramAcquisition] = None

# ── Helpers ─────────────────────────────────────────────────────────
def _json_response(data: Any, status: int = 200) -> Response:
    """Return a JSON response with proper headers."""
    return Response(
        json.dumps(data, indent=2, default=str, ensure_ascii=False),
        status=status,
        mimetype="application/json; charset=utf-8"
    )

def _error(message: str, status: int = 400) -> Response:
    return _json_response({"success": False, "error": message}, status)

def _success(data: Any, message: str = "OK") -> Response:
    return _json_response({"success": True, "message": message, "data": data})

# ════════════════════════════════════════════════════════════════════
# HTML DASHBOARD (Widget served as template)
# ════════════════════════════════════════════════════════════════════

@app.route("/", methods=["GET"])
def index():
    """Serve the main dashboard widget."""
    return render_template("dashboard.html")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Alias for the main dashboard."""
    return render_template("dashboard.html")

# ════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ════════════════════════════════════════════════════════════════════

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return _success({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "services": {
            "dashboard": True,
            "pipeline": True,
            "telegram": telegram_engine is not None,
        }
    })

# ── Products ────────────────────────────────────────────────────────
@app.route("/api/products", methods=["GET"])
def get_products():
    """Get all products with optional pagination."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    per_page = min(per_page, 200)

    products = dashboard_service.get_all_products()
    total = len(products)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = products[start:end]

    return _success({
        "products": paginated,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        }
    })

@app.route("/api/products/<product_id>", methods=["GET"])
def get_product(product_id: str):
    """Get a single product by ID."""
    product = dashboard_service.get_product_by_id(product_id)
    if product is None:
        return _error(f"Product '{product_id}' not found", 404)
    return _success(product)

# ── Search ──────────────────────────────────────────────────────────
@app.route("/api/products/search", methods=["GET"])
def search_products():
    """Search products by query string."""
    query = request.args.get("q", "").strip()
    if not query:
        return _error("Query parameter 'q' is required")

    results = dashboard_service.search(query)
    return _success({
        "query": query,
        "count": len(results),
        "products": results,
    })

# ── Filter ──────────────────────────────────────────────────────────
@app.route("/api/products/filter", methods=["GET"])
def filter_products():
    """Filter products by multiple criteria."""
    category = request.args.get("category")
    condition = request.args.get("condition")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    brand = request.args.get("brand")
    status = request.args.get("status")
    sort_by = request.args.get("sort_by", "acquired_at")
    ascending = request.args.get("ascending", "false").lower() == "true"

    filtered = dashboard_service.filter_products(
        category=category,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
        brand=brand,
        status=status,
    )
    sorted_products = dashboard_service.sort_products(filtered, sort_by=sort_by, ascending=ascending)

    return _success({
        "filters": {
            "category": category,
            "condition": condition,
            "min_price": min_price,
            "max_price": max_price,
            "brand": brand,
            "status": status,
        },
        "count": len(sorted_products),
        "products": sorted_products,
    })

# ── Newest ──────────────────────────────────────────────────────────
@app.route("/api/products/newest", methods=["GET"])
def newest_products():
    """Get the most recently acquired products."""
    limit = request.args.get("limit", 10, type=int)
    limit = min(limit, 100)
    products = dashboard_service.get_newest_products(limit=limit)
    return _success({
        "limit": limit,
        "products": products,
    })

# ── Statistics ──────────────────────────────────────────────────────
@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    """Get dashboard statistics."""
    stats = dashboard_service.get_statistics()
    return _success(stats)

# ── Duplicates ──────────────────────────────────────────────────────
@app.route("/api/duplicates", methods=["GET"])
def get_duplicates():
    """Get duplicate products report."""
    report = dashboard_service.duplicate_report()
    return _success(report)

# ── Pipeline ────────────────────────────────────────────────────────
@app.route("/api/pipeline/run", methods=["POST"])
def run_pipeline():
    """
    Run the full pipeline on raw Telegram messages.
    Body (optional JSON):
        { "clean": false, "telegram_dir": "data/raw/telegram" }
    """
    body = request.get_json(silent=True) or {}
    clean = body.get("clean", False)
    telegram_dir = body.get("telegram_dir", "data/raw/telegram")

    try:
        from scripts.run_pipeline import run_pipeline as _run_pipeline
        report = _run_pipeline(
            telegram_dir=telegram_dir,
            products_dir="data/products",
            clean=clean,
        )
        return _success(report, "Pipeline completed successfully")
    except Exception as e:
        import traceback
        return _error(f"Pipeline failed: {str(e)}\n{traceback.format_exc()}", 500)

# ── Export ──────────────────────────────────────────────────────────
@app.route("/api/export", methods=["POST"])
def export_products():
    """Export products to JSON file."""
    body = request.get_json(silent=True) or {}
    filename = body.get("filename")

    if filename:
        filepath = os.path.join(EXPORT_DIR, filename)
    else:
        filepath = os.path.join(
            EXPORT_DIR,
            f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    try:
        json_str = dashboard_service.export_json(filepath=filepath)
        return _success({
            "filepath": filepath,
            "count": json.loads(json_str)["count"],
        }, f"Exported to {filepath}")
    except Exception as e:
        return _error(f"Export failed: {str(e)}", 500)

# ── Telegram ────────────────────────────────────────────────────────
@app.route("/api/telegram/scan", methods=["POST"])
def telegram_scan():
    """
    Trigger a Telegram channel scan.
    Body (JSON):
        {
            "api_id": 12345,
            "api_hash": "abcdef...",
            "phone": "+1234567890",
            "channels": ["@channel1", "@channel2"],
            "download_media": true
        }
    """
    global telegram_engine
    body = request.get_json(silent=True) or {}

    api_id = body.get("api_id")
    api_hash = body.get("api_hash")
    phone = body.get("phone")
    channels = body.get("channels", [])
    download_media = body.get("download_media", True)

    if not api_id or not api_hash:
        return _error("api_id and api_hash are required", 400)
    if not channels:
        return _error("channels list is required", 400)

    config = AcquisitionConfig(
        api_id=int(api_id),
        api_hash=str(api_hash),
        phone=str(phone) if phone else "",
        base_data_path=os.path.join(PROJECT_ROOT, "data"),
        download_media=bool(download_media),
    )

    telegram_engine = TelegramAcquisition(config)

    def _scan():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(telegram_engine.connect())
            loop.run_until_complete(telegram_engine.scan_channels(channels))
        finally:
            loop.run_until_complete(telegram_engine.disconnect())
            loop.close()

    thread = threading.Thread(target=_scan, daemon=True)
    thread.start()

    return _success({
        "status": "scanning",
        "channels": channels,
        "message": "Scan started in background. Check /api/telegram/status for progress.",
    })

@app.route("/api/telegram/status", methods=["GET"])
def telegram_status():
    """Get Telegram scan status."""
    if telegram_engine is None:
        return _success({
            "status": "idle",
            "message": "No active Telegram engine. Use /api/telegram/scan to start.",
        })

    states = telegram_engine.get_all_scan_states()
    stats = telegram_engine.get_stats()

    return _success({
        "status": "active" if states else "idle",
        "scan_states": {k: v.to_dict() for k, v in states.items()},
        "stats": stats,
    })

# ── Telegram Channels ───────────────────────────────────────────────
@app.route("/api/telegram/channels", methods=["GET"])
def get_telegram_channels():
    """Get list of scanned Telegram channels and their stats."""
    channels = []
    
    if not os.path.exists(RAW_DIR):
        return _success({"channels": [], "total_messages": 0})
    
    for channel_name in sorted(os.listdir(RAW_DIR)):
        channel_path = os.path.join(RAW_DIR, channel_name)
        if not os.path.isdir(channel_path):
            continue
            
        # Count JSON message files
        msg_count = 0
        latest_msg = None
        
        for filename in os.listdir(channel_path):
            if filename.endswith(".json"):
                msg_count += 1
                filepath = os.path.join(channel_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        msg = json.load(f)
                        msg_date = msg.get("date") or msg.get("timestamp")
                        if msg_date and (latest_msg is None or msg_date > latest_msg):
                            latest_msg = msg_date
                except:
                    pass
        
        channels.append({
            "name": channel_name,
            "display_name": channel_name.replace("_", " ").title(),
            "message_count": msg_count,
            "latest_message": latest_msg,
            "path": channel_path
        })
    
    return _success({
        "channels": channels,
        "total_channels": len(channels),
        "total_messages": sum(c["message_count"] for c in channels)
    })

# ── Dynamic Telegram Sources Endpoint (New) ────────────────────────
@app.route("/api/telegram-sources", methods=["GET"])
def get_telegram_sources():
    """Retrieve actual sources configuration and statuses directly from local files."""
    sources = []
    
    if not os.path.exists(RAW_DIR):
        return jsonify([])
        
    for channel_name in os.listdir(RAW_DIR):
        channel_path = os.path.join(RAW_DIR, channel_name)
        if os.path.isdir(channel_path):
            # Calculate actual JSON messages
            json_files = glob.glob(os.path.join(channel_path, "*.json"))
            total_messages = len(json_files)
            
            # Count actual products extracted from this channel
            products_count = 0
            if os.path.exists(DATA_DIR):
                processed_products = glob.glob(os.path.join(DATA_DIR, "*.json"))
                for p_file in processed_products:
                    try:
                        with open(p_file, "r", encoding="utf-8") as f:
                            p_data = json.load(f)
                            # Match product to channel (source.update_id is usually parsed from the filename/source metadata)
                            source_meta = p_data.get("source", {})
                            if p_data.get("source_channel") == channel_name or channel_name in str(source_meta):
                                products_count += 1
                    except:
                        pass

            # Detect last dynamic scan time
            last_scan = "N/A"
            if json_files:
                latest_file = max(json_files, key=os.path.getmtime)
                mtime = os.path.getmtime(latest_file)
                last_scan = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %I:%M %p")
            
            # Determine active status dynamically
            status = "Active" if total_messages > 0 else "Pending"
            
            # Formulate Clean UI-Friendly Name
            display_channel = f"@{channel_name}" if not channel_name.startswith("@") else channel_name
            
            sources.append({
                "channel_name": display_channel,
                "status": status,
                "messages": total_messages,
                "products": products_count,
                "last_scan": last_scan
            })
            
    return jsonify(sources)

# ── Error Handlers ──────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return _error("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(e):
    return _error("Internal server error", 500)

# ── Main ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    cli = argparse.ArgumentParser()
    cli.add_argument("--host", default="0.0.0.0", help="Host to bind")
    cli.add_argument("--port", type=int, default=5000, help="Port to bind")
    cli.add_argument("--debug", action="store_true", help="Debug mode")
    args = cli.parse_args()

    print("=" * 60)
    print("  MARKETING BRAIN OS — FLASK API")
    print("=" * 60)
    print(f"  Project:  {PROJECT_ROOT}")
    print(f"  Data:      {DATA_DIR}")
    print(f"  Raw:      {RAW_DIR}")
    print(f"  Export:   {EXPORT_DIR}")
    print(f"  Endpoint: http://{args.host}:{args.port}/api/")
    print(f"  Dashboard: http://{args.host}:{args.port}/")
    print("=" * 60)

    app.run(host=args.host, port=args.port, debug=args.debug)