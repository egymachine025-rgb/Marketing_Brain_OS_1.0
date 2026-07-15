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

from src.intelligence import (
    ContentAnalyzer,
    KeywordResearchEngine,
    MarketingPsychologyEngine,
    EgyptianMarketStudy,
    SocialMediaKnowledgeBase,
    EgyptianMarketSegments,
)

# ── Telegram imports (from marketing_brain_os package) ──────────────
from marketing_brain_os.telegram_acquisition import TelegramAcquisition, AcquisitionConfig

# ── Research imports ─────────────────────────────────────────────────
from src.research.research_tasks import ResearchTaskManager, TaskStatus, TaskPriority
from src.research.research_results import ResearchResultManager

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
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static"),
)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── Global Service Instances ────────────────────────────────────────
dashboard_repo = DashboardRepository(data_dir=DATA_DIR)
dashboard_service = DashboardService(repo=dashboard_repo)
dup_engine = DuplicateEngine(data_dir=DATA_DIR)

# Telegram engine (initialized on demand)
telegram_engine: Optional[TelegramAcquisition] = None

# Research managers
research_task_manager = ResearchTaskManager()
research_result_manager = ResearchResultManager()

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

@app.route("/profile", methods=["GET"])
def profile():
    """Serve the WhatsApp-style dashboard profile."""
    return render_template("dashboard_profile.html", now=datetime.now().strftime("%Y-%m-%d %I:%M %p"))

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

# ── Intelligence ───────────────────────────────────────────────────

def _build_intelligence_for_product(product: dict) -> dict:
    analyzer = ContentAnalyzer()
    keyword_engine = KeywordResearchEngine()
    psychology = MarketingPsychologyEngine()
    market_study = EgyptianMarketStudy()

    title = product.get("name") or product.get("listing", {}).get("title", "")
    description = product.get("listing", {}).get("description", "")
    content_text = f"{title} {description}".strip()

    content_analysis = analyzer.analyze_content_type(content_text)
    page_category = analyzer.categorize_page([content_text])
    keyword_data = analyzer.extract_keywords(content_text)
    keyword_suggestions = keyword_engine.find_low_competition_keywords(product.get("category", ""))
    competitor_data = keyword_engine.analyze_competitor_keywords([content_text])

    target_segment = content_analysis.get("target_audience", ["middle"])[0]
    price = float(product.get("listing", {}).get("price", {}).get("amount", 0) or 0)
    pricing = psychology.recommend_pricing_strategy(product, target_segment)
    conversion_rate = psychology.predict_conversion_rate(content_analysis.get("type", "product_showcase"), target_segment, price)
    sales_hooks = psychology.generate_sales_hooks(product, target_segment)
    market_insights = market_study.get_market_insight(product.get("category", ""), "Cairo")
    audience_segments = market_study.segment_audience(product, price)
    social_behaviors = SocialMediaKnowledgeBase.get_behaviors(target_segment)

    return {
        "product_id": product.get("product_id"),
        "title": title,
        "content_analysis": content_analysis,
        "page_category": page_category,
        "keyword_data": keyword_data,
        "keyword_suggestions": keyword_suggestions,
        "competitor_analysis": competitor_data,
        "pricing": pricing,
        "conversion_rate": conversion_rate,
        "sales_hooks": sales_hooks,
        "market_insights": market_insights,
        "audience_segments": audience_segments,
        "social_media_behaviors": social_behaviors,
    }

@app.route("/api/intelligence/product/<product_id>", methods=["GET"])
def get_product_intelligence(product_id: str):
    """Get intelligence insights for a specific product."""
    product = dashboard_service.get_product_by_id(product_id)
    if not product:
        return _error(f"Product '{product_id}' not found", 404)
    return _success(_build_intelligence_for_product(product))

@app.route("/api/intelligence/products/newest", methods=["GET"])
def get_newest_products_intelligence():
    """Get intelligence insights for the newest acquired products."""
    limit = request.args.get("limit", 10, type=int)
    limit = min(limit, 20)
    products = dashboard_service.get_newest_products(limit=limit)
    insights = [_build_intelligence_for_product(product) for product in products]
    return _success({"products": insights})

@app.route("/api/intelligence/market-segments", methods=["GET"])
def get_market_segments():
    """Get Egyptian market segments with income levels and demographics."""
    market_study = EgyptianMarketStudy()
    market_segments = EgyptianMarketSegments()
    
    segments = []
    for segment in market_segments.get_all_segments():
        segments.append({
            "segment_name": segment.name,
            "income_range": segment.income_range,
            "income_min": segment.income_min,
            "income_max": segment.income_max,
            "population_percentage": segment.population_percentage,
            "areas": segment.areas,
            "age_range": segment.age_range,
            "education_level": segment.education_level,
            "social_media_platforms": segment.social_media_platforms,
            "content_preferences": segment.content_preferences,
            "purchasing_behavior": segment.purchasing_behavior,
            "price_sensitivity": segment.price_sensitivity,
            "brand_loyalty": segment.brand_loyalty,
            "preferred_payment_methods": segment.preferred_payment_methods,
            "peak_activity_hours": segment.peak_activity_hours,
            "language_preference": segment.language_preference
        })
    
    # Add overall market data
    market_data = {
        "total_population": market_study.DATA["population"],
        "internet_users": market_study.DATA["internet_users"],
        "social_media_users": market_study.DATA["social_media_users"],
        "ecommerce_penetration": market_study.DATA["ecommerce_penetration"],
        "preferred_payment": market_study.DATA["preferred_payment"]
    }
    
    # Add platform insights
    platform_insights = {}
    for platform_name in ["facebook", "instagram", "tiktok", "whatsapp"]:
        platform_insights[platform_name] = market_segments.get_platform_insights(platform_name)
    
    # Add regional insights
    regional_insights = {}
    for region_name in ["cairo", "alexandria", "delta", "upper_egypt", "sinai_red_sea"]:
        regional_insights[region_name] = market_segments.get_regional_insights(region_name)
    
    return _success({
        "market_data": market_data,
        "segments": segments,
        "platform_insights": platform_insights,
        "regional_insights": regional_insights
    })

def _get_segment_percentage(segment_name: str) -> float:
    """Estimate population percentage for a segment."""
    percentages = {
        "upper": 0.05,
        "upper_middle": 0.15,
        "middle": 0.35,
        "lower_middle": 0.30,
        "lower": 0.15
    }
    return percentages.get(segment_name, 0.0)

@app.route("/api/intelligence/content-strategy", methods=["GET"])
def get_content_strategy():
    """Get content strategy recommendations for a specific product."""
    product_id = request.args.get("product_id")
    if not product_id:
        return _error("product_id parameter is required")
    
    product = dashboard_service.get_product_by_id(product_id)
    if not product:
        return _error(f"Product '{product_id}' not found", 404)
    
    analyzer = ContentAnalyzer()
    market_study = EgyptianMarketStudy()
    market_segments = EgyptianMarketSegments()
    
    title = product.get("name") or product.get("listing", {}).get("title", "")
    description = product.get("listing", {}).get("description", "")
    content_text = f"{title} {description}".strip()
    category = product.get("category", "")
    price = float(product.get("listing", {}).get("price", {}).get("amount", 0) or 0)
    
    # Analyze content
    content_analysis = analyzer.analyze_content_type(content_text)
    
    # Determine market segment based on price
    segment_name = market_segments.get_segment_by_income(price * 30)  # Convert USD to EGP roughly
    segment = market_segments.get_segment(segment_name)
    
    # Get market insights for Cairo (default)
    market_insights = market_study.get_market_insight(category, "Cairo")
    
    # Get detailed platform recommendations
    platform_recommendations = _get_detailed_platform_recommendations(category, segment_name)
    
    # Get best posting times
    posting_times = _get_best_posting_times(platform_recommendations)
    
    # Get content type recommendations
    content_type = _get_content_type_recommendation(category, segment_name)
    
    # Get caption style
    caption_style = _get_caption_style_recommendation(segment_name, content_analysis)
    
    # Generate hashtags
    hashtags = _generate_hashtags(category, content_text, segment_name)
    
    # Generate content suggestions
    content_suggestions = _generate_content_suggestions(content_analysis, category)
    
    return _success({
        "product_id": product_id,
        "category": category,
        "price": price,
        "target_segment": segment_name,
        "content_analysis": content_analysis,
        "market_insights": market_insights,
        "platform_recommendations": platform_recommendations,
        "best_posting_times": posting_times,
        "content_type": content_type,
        "caption_style": caption_style,
        "hashtags": hashtags,
        "content_suggestions": content_suggestions
    })

def _get_detailed_platform_recommendations(category: str, segment_name: str) -> dict:
    """Get detailed platform recommendations based on category and segment."""
    category_lower = category.lower()
    market_segments = EgyptianMarketSegments()
    segment = market_segments.get_segment(segment_name)
    
    # Base platform recommendations by category
    if "fashion" in category_lower or "clothing" in category_lower or "dress" in category_lower:
        primary = ["instagram", "tiktok"]
        secondary = ["facebook"]
        reasoning = "Visual platforms work best for fashion products"
    elif "electronics" in category_lower or "phone" in category_lower or "tech" in category_lower:
        primary = ["facebook", "whatsapp"]
        secondary = ["instagram"]
        reasoning = "Detailed specs and trust important for electronics"
    else:
        primary = ["facebook", "instagram"]
        secondary = ["whatsapp"]
        reasoning = "Broad reach across Egyptian market"
    
    # Refine based on segment preferences
    segment_platforms = segment.social_media_platforms
    
    return {
        "primary": [p for p in primary if p in segment_platforms],
        "secondary": [p for p in secondary if p in segment_platforms],
        "reasoning": reasoning,
        "segment_alignment": segment_platforms
    }

def _get_best_posting_times(platforms: dict) -> dict:
    """Get best posting times for recommended platforms."""
    all_platforms = platforms.get("primary", []) + platforms.get("secondary", [])
    
    times = {
        "facebook": {"peak": "12:00-15:00", "secondary": "19:00-21:00"},
        "instagram": {"peak": "19:00-22:00", "secondary": "12:00-14:00"},
        "tiktok": {"peak": "18:00-21:00", "secondary": "12:00-15:00"},
        "whatsapp": {"peak": "10:00-12:00", "secondary": "16:00-18:00"}
    }
    
    return {platform: times[platform] for platform in all_platforms if platform in times}

def _get_content_type_recommendation(category: str, segment_name: str) -> dict:
    """Get content type recommendations based on category and segment."""
    category_lower = category.lower()
    market_segments = EgyptianMarketSegments()
    segment = market_segments.get_segment(segment_name)
    
    if "fashion" in category_lower or "clothing" in category_lower:
        return {
            "primary": "video",
            "secondary": ["carousel", "image"],
            "story": "highly_recommended",
            "reels": "highly_recommended",
            "reasoning": "Fashion products benefit from showing movement and multiple angles"
        }
    elif "electronics" in category_lower or "phone" in category_lower:
        return {
            "primary": "carousel",
            "secondary": ["video", "image"],
            "story": "recommended",
            "reels": "recommended",
            "reasoning": "Electronics need detailed specs shown in carousel format"
        }
    else:
        return {
            "primary": "image",
            "secondary": ["video", "carousel"],
            "story": "recommended",
            "reels": "optional",
            "reasoning": "Standard product images work well for general products"
        }

def _get_caption_style_recommendation(segment_name: str, content_analysis: dict) -> dict:
    """Get caption style recommendations based on segment and content."""
    market_segments = EgyptianMarketSegments()
    segment = market_segments.get_segment(segment_name)
    
    if segment_name in ["upper", "upper_middle"]:
        return {
            "tone": "professional",
            "language": segment.language_preference,
            "length": "medium",
            "emojis": "minimal",
            "structure": "problem-solution",
            "call_to_action": "professional",
            "example": "Discover premium quality with our latest collection. Order now for exclusive delivery."
        }
    elif segment_name == "middle":
        return {
            "tone": "friendly",
            "language": segment.language_preference,
            "length": "medium",
            "emojis": "moderate",
            "structure": "benefit-focused",
            "call_to_action": "direct",
            "example": "Great quality at amazing prices! 🌟 Order now via WhatsApp for fast delivery."
        }
    else:
        return {
            "tone": "casual",
            "language": segment.language_preference,
            "length": "short",
            "emojis": "heavy",
            "structure": "attention-grabbing",
            "call_to_action": "urgent",
            "example": "🔥 عروض جنونية! سعر خاص لفترة محدودة. اطلب الآن ووصل خلال 24 ساعة! 🚚"
        }

def _generate_hashtags(category: str, content_text: str, segment_name: str) -> dict:
    """Generate relevant hashtags based on category, content, and segment."""
    category_lower = category.lower()
    market_segments = EgyptianMarketSegments()
    segment = market_segments.get_segment(segment_name)
    
    # Base hashtags
    base_hashtags = ["#Egypt", "#Cairo", "#ShoppingEgypt", "#Deals"]
    
    # Category-specific hashtags
    if "fashion" in category_lower or "clothing" in category_lower:
        category_hashtags = ["#FashionEgypt", "#StyleEgypt", "#ClothingEgypt", "#FashionCairo", "#ملابس", "#موديلات"]
    elif "electronics" in category_lower or "phone" in category_lower:
        category_hashtags = ["#TechEgypt", "#ElectronicsEgypt", "#MobileEgypt", "#ايفون", "#سامسونج"]
    else:
        category_hashtags = [f"#{category.replace(' ', '')}", "#ProductsEgypt", "#ShoppingOnline"]
    
    # Segment-specific hashtags
    if segment_name in ["upper", "upper_middle"]:
        segment_hashtags = ["#PremiumEgypt", "#LuxuryEgypt", "#QualityFirst"]
    elif segment_name == "middle":
        segment_hashtags = ["#BestDeals", "#ValueForMoney", "#QualityAssurance"]
    else:
        segment_hashtags = ["#DiscountEgypt", "#SpecialOffer", "#LowPrice"]
    
    return {
        "primary": base_hashtags[:3],
        "category": category_hashtags[:5],
        "segment": segment_hashtags[:3],
        "all": base_hashtags + category_hashtags + segment_hashtags,
        "usage_tip": "Use 5-8 hashtags per post, mix from all categories"
    }

def _generate_content_suggestions(content_analysis: dict, category: str) -> dict:
    """Generate content suggestions based on analysis."""
    content_type = content_analysis.get("type", "general")
    tone = content_analysis.get("tone", "professional")
    
    suggestions = {
        "headlines": [
            f"Best {category} in Egypt - Limited Stock",
            f"Premium {category} - Free Delivery",
            f"Special Offer on {category} - Don't Miss Out"
        ],
        "call_to_action": [
            "Order Now via WhatsApp",
            "Limited Stock - Contact Us Today",
            "Free Delivery in Cairo"
        ],
        "hashtag_suggestions": [
            f"#{category.replace(' ', '_')}",
            "#Egypt",
            "#Cairo",
            "#ShoppingEgypt",
            "#Deals"
        ],
        "content_tips": [
            "Use high-quality images showing product details",
            "Include price and delivery information",
            "Add customer testimonials when available",
            "Use Egyptian Arabic for local appeal"
        ]
    }
    
    return suggestions

@app.route("/api/intelligence/keywords", methods=["GET"])
def get_keywords():
    """Get keyword suggestions with competition analysis for a category."""
    category = request.args.get("category", "")
    
    keyword_engine = KeywordResearchEngine()
    
    # Get low competition keywords
    low_competition = keyword_engine.find_low_competition_keywords(category)
    
    # Get competitor analysis
    competitor_keywords = keyword_engine.analyze_competitor_keywords([category])
    
    # Generate keyword suggestions with competition levels
    all_keywords = _generate_keyword_suggestions(category)
    
    return _success({
        "category": category,
        "low_competition_keywords": low_competition,
        "competitor_analysis": competitor_keywords,
        "keyword_suggestions": all_keywords
    })

def _generate_keyword_suggestions(category: str) -> list:
    """Generate keyword suggestions with competition analysis, search volume, and CPC estimates in EGP."""
    category_lower = category.lower()
    
    # Base keywords by category with enhanced data
    if "fashion" in category_lower or "clothing" in category_lower:
        base_keywords = [
            {"keyword": "ملابس", "competition": "high", "search_volume": 45000, "cpc_egp": 8.50, "difficulty": 85},
            {"keyword": "لونج دريس", "competition": "medium", "search_volume": 12000, "cpc_egp": 4.20, "difficulty": 55},
            {"keyword": "ستايل كاجوال", "competition": "low", "search_volume": 3500, "cpc_egp": 1.80, "difficulty": 25},
            {"keyword": "فستان", "competition": "high", "search_volume": 38000, "cpc_egp": 7.80, "difficulty": 80},
            {"keyword": "موديل 2024", "competition": "low", "search_volume": 5600, "cpc_egp": 2.50, "difficulty": 30},
            {"keyword": "سعر خاص", "competition": "medium", "search_volume": 18000, "cpc_egp": 3.90, "difficulty": 45},
            {"keyword": "ملابس حريمي", "competition": "high", "search_volume": 32000, "cpc_egp": 6.70, "difficulty": 75},
            {"keyword": "احدث موديلات", "competition": "low", "search_volume": 4200, "cpc_egp": 2.10, "difficulty": 28}
        ]
    elif "electronics" in category_lower or "phone" in category_lower:
        base_keywords = [
            {"keyword": "ايفون", "competition": "high", "search_volume": 68000, "cpc_egp": 15.50, "difficulty": 92},
            {"keyword": "سامسونج", "competition": "high", "search_volume": 54000, "cpc_egp": 12.80, "difficulty": 88},
            {"keyword": "موبايل", "competition": "medium", "search_volume": 42000, "cpc_egp": 6.90, "difficulty": 65},
            {"keyword": "سنيكرز", "competition": "low", "search_volume": 2800, "cpc_egp": 1.50, "difficulty": 22},
            {"keyword": "اكسسوارات", "competition": "medium", "search_volume": 15000, "cpc_egp": 4.50, "difficulty": 48},
            {"keyword": "عرض خاص", "competition": "low", "search_volume": 8500, "cpc_egp": 2.80, "difficulty": 32},
            {"keyword": "شاحن سريع", "competition": "medium", "search_volume": 11000, "cpc_egp": 3.70, "difficulty": 42},
            {"keyword": "سماعات بلوتوث", "competition": "medium", "search_volume": 13500, "cpc_egp": 4.20, "difficulty": 50}
        ]
    else:
        base_keywords = [
            {"keyword": "منتجات", "competition": "high", "search_volume": 52000, "cpc_egp": 7.20, "difficulty": 78},
            {"keyword": "تخفيضات", "competition": "medium", "search_volume": 28000, "cpc_egp": 5.10, "difficulty": 58},
            {"keyword": "عروض", "competition": "medium", "search_volume": 35000, "cpc_egp": 5.80, "difficulty": 62},
            {"keyword": "سعر مناسب", "competition": "low", "search_volume": 9500, "cpc_egp": 2.30, "difficulty": 35},
            {"keyword": "جودة عالية", "competition": "low", "search_volume": 4800, "cpc_egp": 1.90, "difficulty": 28},
            {"keyword": "توصيل مجاني", "competition": "medium", "search_volume": 16500, "cpc_egp": 3.60, "difficulty": 45},
            {"keyword": "تسوق اونلاين", "competition": "high", "search_volume": 41000, "cpc_egp": 6.50, "difficulty": 72},
            {"keyword": "افضل سعر", "competition": "low", "search_volume": 7200, "cpc_egp": 2.70, "difficulty": 38}
        ]
    
    return base_keywords

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

# ── Research Tasks ───────────────────────────────────────────────────
@app.route("/api/research/tasks", methods=["GET"])
def get_research_tasks():
    """Get all research tasks with optional filtering."""
    status = request.args.get("status")
    category = request.args.get("category")
    priority = request.args.get("priority")
    brand = request.args.get("brand")
    product_id = request.args.get("product_id")
    tags = request.args.getlist("tags")
    
    tasks = research_task_manager.list_tasks(
        status=status,
        category=category,
        priority=priority,
        brand=brand,
        product_id=product_id,
        tags=tags if tags else None
    )
    
    return _success({
        "tasks": [task.to_dict() for task in tasks],
        "count": len(tasks)
    })

@app.route("/api/research/tasks", methods=["POST"])
def create_research_task():
    """Create a new research task."""
    body = request.get_json(silent=True) or {}
    
    title = body.get("title")
    description = body.get("description")
    category = body.get("category")
    suggested_tools = body.get("suggested_tools", [])
    steps = body.get("steps", [])
    expected_results = body.get("expected_results", {})
    priority = body.get("priority", TaskPriority.MEDIUM.value)
    assigned_to = body.get("assigned_to")
    tags = body.get("tags", [])
    brand = body.get("brand")
    product_id = body.get("product_id")
    notes = body.get("notes")
    
    if not title or not description or not category:
        return _error("title, description, and category are required")
    
    try:
        task = research_task_manager.create_task(
            title=title,
            description=description,
            category=category,
            suggested_tools=suggested_tools,
            steps=steps,
            expected_results=expected_results,
            priority=priority,
            assigned_to=assigned_to,
            tags=tags,
            brand=brand,
            product_id=product_id,
            notes=notes
        )
        return _success(task.to_dict(), "Task created successfully")
    except Exception as e:
        return _error(f"Failed to create task: {str(e)}", 500)

@app.route("/api/research/tasks/<task_id>", methods=["GET"])
def get_research_task(task_id: str):
    """Get a specific research task by ID."""
    task = research_task_manager.get_task(task_id)
    if not task:
        return _error(f"Task '{task_id}' not found", 404)
    return _success(task.to_dict())

@app.route("/api/research/tasks/<task_id>", methods=["PUT"])
def update_research_task(task_id: str):
    """Update a research task."""
    body = request.get_json(silent=True) or {}
    
    task = research_task_manager.update_task(
        task_id=task_id,
        title=body.get("title"),
        description=body.get("description"),
        status=body.get("status"),
        priority=body.get("priority"),
        assigned_to=body.get("assigned_to"),
        notes=body.get("notes"),
        tags=body.get("tags")
    )
    
    if not task:
        return _error(f"Task '{task_id}' not found", 404)
    
    return _success(task.to_dict(), "Task updated successfully")

@app.route("/api/research/tasks/<task_id>/complete", methods=["POST"])
def complete_research_task(task_id: str):
    """Mark a research task as completed."""
    body = request.get_json(silent=True) or {}
    notes = body.get("notes")
    
    task = research_task_manager.complete_task(task_id, notes=notes)
    
    if not task:
        return _error(f"Task '{task_id}' not found", 404)
    
    return _success(task.to_dict(), "Task completed successfully")

@app.route("/api/research/tasks/<task_id>", methods=["DELETE"])
def delete_research_task(task_id: str):
    """Delete a research task."""
    success = research_task_manager.delete_task(task_id)
    
    if not success:
        return _error(f"Task '{task_id}' not found", 404)
    
    return _success({"task_id": task_id}, "Task deleted successfully")

@app.route("/api/research/tasks/statistics", methods=["GET"])
def get_research_task_statistics():
    """Get research task statistics."""
    stats = research_task_manager.get_statistics()
    return _success(stats)

# ── Research Results ──────────────────────────────────────────────────
@app.route("/api/research/results", methods=["GET"])
def get_research_results():
    """Get all research results with optional filtering."""
    category = request.args.get("category")
    brand = request.args.get("brand")
    channel = request.args.get("channel")
    product_id = request.args.get("product_id")
    tags = request.args.getlist("tags")
    limit = request.args.get("limit", type=int)
    
    results = research_result_manager.list_results(
        category=category,
        brand=brand,
        channel=channel,
        product_id=product_id,
        tags=tags if tags else None,
        limit=limit
    )
    
    return _success({
        "results": [result.to_dict() for result in results],
        "count": len(results)
    })

@app.route("/api/research/results/<result_id>", methods=["GET"])
def get_research_result(result_id: str):
    """Get a specific research result by ID."""
    result = research_result_manager.get_result(result_id)
    if not result:
        return _error(f"Result '{result_id}' not found", 404)
    return _success(result.to_dict())

@app.route("/api/research/results", methods=["POST"])
def save_research_result():
    """Save a new research result."""
    body = request.get_json(silent=True) or {}
    
    title = body.get("title")
    category = body.get("category")
    data = body.get("data")
    source = body.get("source")
    tags = body.get("tags", [])
    task_id = body.get("task_id")
    brand = body.get("brand")
    channel = body.get("channel")
    product_id = body.get("product_id")
    notes = body.get("notes")
    confidence_score = body.get("confidence_score")
    
    if not title or not category or not data or not source:
        return _error("title, category, data, and source are required")
    
    try:
        result = research_result_manager.save_result(
            title=title,
            category=category,
            data=data,
            source=source,
            tags=tags,
            task_id=task_id,
            brand=brand,
            channel=channel,
            product_id=product_id,
            notes=notes,
            confidence_score=confidence_score
        )
        return _success(result.to_dict(), "Result saved successfully")
    except Exception as e:
        return _error(f"Failed to save result: {str(e)}", 500)

@app.route("/api/research/results/<result_id>", methods=["PUT"])
def update_research_result(result_id: str):
    """Update a research result."""
    body = request.get_json(silent=True) or {}
    
    result = research_result_manager.update_result(
        result_id=result_id,
        title=body.get("title"),
        data=body.get("data"),
        notes=body.get("notes"),
        tags=body.get("tags"),
        confidence_score=body.get("confidence_score")
    )
    
    if not result:
        return _error(f"Result '{result_id}' not found", 404)
    
    return _success(result.to_dict(), "Result updated successfully")

@app.route("/api/research/results/<result_id>", methods=["DELETE"])
def delete_research_result(result_id: str):
    """Delete a research result."""
    success = research_result_manager.delete_result(result_id)
    
    if not success:
        return _error(f"Result '{result_id}' not found", 404)
    
    return _success({"result_id": result_id}, "Result deleted successfully")

@app.route("/api/research/results/statistics", methods=["GET"])
def get_research_result_statistics():
    """Get research result statistics."""
    stats = research_result_manager.get_statistics()
    return _success(stats)

# ── Research Auto-Suggest ─────────────────────────────────────────────
@app.route("/api/research/suggest", methods=["GET"])
def suggest_research():
    """
    Auto-suggest next research tasks based on current data gaps.
    
    Logic:
    - If brand has < 3 keywords → suggest keyword research
    - If product has no price data → suggest pricing research
    - If category is new → suggest market research
    - If competitor unknown → suggest competitor analysis
    """
    suggestions = []
    
    # Get all products
    products = dashboard_service.get_all_products()
    
    # Analyze brands for keyword gaps
    brand_keyword_counts = {}
    for product in products:
        brand = product.get("brand")
        if brand:
            brand_keyword_counts[brand] = brand_keyword_counts.get(brand, 0) + 1
    
    for brand, count in brand_keyword_counts.items():
        # Check if we have keyword research for this brand
        keyword_results = research_result_manager.search_by_brand(brand)
        keyword_results = [r for r in keyword_results if r.category == "keywords"]
        
        if len(keyword_results) < 3:
            suggestions.append({
                "type": "keyword_research",
                "priority": "high" if len(keyword_results) == 0 else "medium",
                "reason": f"Brand '{brand}' has only {len(keyword_results)} keyword research results",
                "suggested_task": {
                    "title": f"Keyword Research for {brand}",
                    "description": f"Research keywords for brand {brand} in the Egyptian market",
                    "category": "keywords",
                    "suggested_tools": ["google_trends", "ubersuggest"],
                    "steps": [
                        f"Go to Google Trends",
                        f"Search '{brand} egypt'",
                        "Note: Interest over time, related queries",
                        f"Go to Ubersuggest",
                        f"Search '{brand}'",
                        "Note: Search volume, SEO difficulty, CPC"
                    ],
                    "expected_results": {
                        "keywords": ["list of keywords"],
                        "volumes": {"keyword": "monthly searches"},
                        "difficulty": {"keyword": "score 0-100"},
                        "trend": "up/down/stable"
                    },
                    "brand": brand
                }
            })
    
    # Analyze products for price data gaps
    for product in products[:10]:  # Check first 10 products
        product_id = product.get("product_id")
        price_data = product.get("listing", {}).get("price")
        
        if not price_data or not price_data.get("amount"):
            suggestions.append({
                "type": "pricing_research",
                "priority": "medium",
                "reason": f"Product '{product.get('name', 'Unknown')}' has no price data",
                "suggested_task": {
                    "title": f"Pricing Research for {product.get('name', 'Unknown')}",
                    "description": "Research market pricing for this product category",
                    "category": "market_research",
                    "suggested_tools": ["facebook_ad_library", "similarweb"],
                    "steps": [
                        "Go to Facebook Ad Library",
                        "Search for similar products",
                        "Note: Price ranges from competitors",
                        "Go to SimilarWeb",
                        "Analyze competitor pricing strategies"
                    ],
                    "expected_results": {
                        "price_range": {"min": 0, "max": 0},
                        "competitor_prices": [{"competitor": "price"}],
                        "market_average": 0
                    },
                    "product_id": product_id
                }
            })
    
    # Analyze categories for market research gaps
    category_counts = {}
    for product in products:
        category = product.get("category")
        if category:
            category_counts[category] = category_counts.get(category, 0) + 1
    
    for category, count in category_counts.items():
        # Check if we have market research for this category
        market_results = research_result_manager.search_by_category("market_research")
        category_researched = any(category.lower() in r.title.lower() for r in market_results)
        
        if not category_researched and count > 2:
            suggestions.append({
                "type": "market_research",
                "priority": "high",
                "reason": f"Category '{category}' has {count} products but no market research",
                "suggested_task": {
                    "title": f"Market Research for {category}",
                    "description": f"Research the Egyptian market for {category}",
                    "category": "market_research",
                    "suggested_tools": ["capmas_egypt", "google_consumer"],
                    "steps": [
                        "Go to Capmas Egypt",
                        f"Search for {category} market data",
                        "Note: Market size, demographics",
                        "Go to Google Consumer Barometer",
                        "Analyze consumer behavior for this category"
                    ],
                    "expected_results": {
                        "market_size": 0,
                        "target_demographics": [],
                        "consumer_behavior": {},
                        "growth_trend": "up/down/stable"
                    },
                    "tags": [category, "market_research"]
                }
            })
    
    # Analyze for competitor analysis gaps
    for product in products[:5]:  # Check first 5 products
        brand = product.get("brand")
        if brand:
            competitor_results = research_result_manager.search_by_brand(brand)
            competitor_results = [r for r in competitor_results if r.category == "competitors"]
            
            if len(competitor_results) == 0:
                suggestions.append({
                    "type": "competitor_analysis",
                    "priority": "medium",
                    "reason": f"Brand '{brand}' has no competitor analysis",
                    "suggested_task": {
                        "title": f"Competitor Analysis for {brand}",
                        "description": f"Analyze competitors for brand {brand}",
                        "category": "competitors",
                        "suggested_tools": ["facebook_ad_library", "similarweb"],
                        "steps": [
                            "Go to Facebook Ad Library",
                            f"Search for {brand} competitors",
                            "Note: Ad strategies, creatives, targeting",
                            "Go to SimilarWeb",
                            "Analyze competitor traffic sources"
                        ],
                        "expected_results": {
                            "competitors": ["list of competitors"],
                            "ad_strategies": {},
                            "traffic_sources": {},
                            "market_position": "leader/challenger/niche"
                        },
                        "brand": brand
                    }
                })
    
    # Sort suggestions by priority
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    suggestions.sort(key=lambda x: priority_order.get(x["priority"], 4))
    
    return _success({
        "suggestions": suggestions,
        "count": len(suggestions)
    })

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