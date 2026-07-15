"""
Marketing Brain OS — API Package
================================
Flask REST API for Dashboard, Pipeline, and Telegram integration.

Usage:
    from src.api import app
    app.run(host="0.0.0.0", port=5000)
"""
from .app import app

__all__ = ["app"]
