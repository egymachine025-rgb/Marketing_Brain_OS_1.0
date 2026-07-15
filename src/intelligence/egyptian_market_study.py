from __future__ import annotations

from typing import Dict, List, Any


class EgyptianMarketStudy:
    """Market study data and audience segmentation for Egypt."""

    DATA = {
        "population": 105_000_000,
        "internet_users": 75_000_000,
        "social_media_users": 55_000_000,
        "ecommerce_penetration": 0.35,
        "preferred_payment": {"COD": 0.75, "cards": 0.20, "wallets": 0.05},
    }

    CITY_INSIGHTS: Dict[str, Dict[str, Any]] = {
        "cairo": {
            "population": 22_000_000,
            "preference": "highest purchasing power",
            "channels": ["facebook", "instagram", "whatsapp"],
        },
        "alexandria": {
            "population": 5_000_000,
            "preference": "coastal lifestyle preference",
            "channels": ["facebook", "tiktok", "instagram"],
        },
        "delta": {
            "population": 15_000_000,
            "preference": "price sensitive, family-oriented",
            "channels": ["facebook", "whatsapp"],
        },
        "upper egypt": {
            "population": 20_000_000,
            "preference": "traditional, brand loyal",
            "channels": ["facebook", "whatsapp"],
        },
        "sinai": {
            "population": 2_000_000,
            "preference": "tourism focused, seasonal",
            "channels": ["instagram", "facebook"],
        },
        "red sea": {
            "population": 1_000_000,
            "preference": "tourism focused, seasonal",
            "channels": ["instagram", "facebook"],
        },
    }

    def get_market_insight(self, product_category: str, city: str) -> Dict[str, Any]:
        category = (product_category or "").lower()
        city_key = (city or "").strip().lower()
        insight = self.CITY_INSIGHTS.get(city_key, self.CITY_INSIGHTS.get("cairo"))

        demand = "medium"
        if category in ["tech", "fashion"]:
            demand = "high"
        if category in ["education", "health"]:
            demand = "medium"
        if category in ["real_estate"]:
            demand = "low"

        price_sensitivity = 0.4
        if city_key in ["delta", "upper egypt", "sinai", "red sea"]:
            price_sensitivity = 0.8
        elif city_key == "cairo":
            price_sensitivity = 0.3

        return {
            "demand_level": demand,
            "price_sensitivity": round(price_sensitivity, 2),
            "preferred_channels": insight["channels"],
            "cultural_considerations": ["ramadan_timing", "family_approval"],
            "logistics_challenges": ["delivery_to_rural", "COD_collection"],
        }

    def segment_audience(self, product: Dict[str, Any], price: float) -> List[Dict[str, Any]]:
        category = (product.get("category") or product.get("listing", {}).get("category", "") or "general").lower()
        segments = []

        segments.append({
            "segment_name": "Young Professionals",
            "age_range": "25-35",
            "income_estimate": "15K-30K",
            "platforms": ["facebook", "instagram"],
            "messaging_style": "modern_bilingual",
            "pain_points": ["quality_vs_price", "brand_authenticity"],
        })

        if price and price < 1000:
            segments.append({
                "segment_name": "Budget Shoppers",
                "age_range": "18-28",
                "income_estimate": "5K-15K",
                "platforms": ["tiktok", "whatsapp"],
                "messaging_style": "casual_local",
                "pain_points": ["price_sensitivity", "fast_delivery"],
            })
        else:
            segments.append({
                "segment_name": "Value Seekers",
                "age_range": "30-45",
                "income_estimate": "25K-40K",
                "platforms": ["facebook", "whatsapp"],
                "messaging_style": "trustworthy_family",
                "pain_points": ["trust", "warranty"],
            })

        return segments
