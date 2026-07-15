from __future__ import annotations

from typing import Dict, List, Any


class MarketingPsychologyEngine:
    """Generate sales psychology content for the Egyptian market."""

    SALES_TRIGGERS = [
        "عرض محدود",
        "خصم 50%",
        "الأكثر مبيعاً",
        "ضمان سنة",
        "توصيل مجاني",
        "الدفع عند الاستلام",
        "تقييم 5 نجوم",
    ]

    def generate_sales_hooks(self, product: Dict[str, Any], audience_segment: str) -> List[str]:
        name = product.get("name") or product.get("listing", {}).get("title", "المنتج")
        segment = audience_segment.replace("_", " ")
        hooks = [
            f"{self.SALES_TRIGGERS[0]} على {name} لفترة محدودة!",
            f"{self.SALES_TRIGGERS[1]} عند الشراء الآن لعملاء {segment}.",
            f"{self.SALES_TRIGGERS[4]} مع {self.SALES_TRIGGERS[5]} لحجز سريع.",
        ]
        return hooks

    def predict_conversion_rate(self, content_type: str, audience: str, price_range: float) -> float:
        score = 0.3
        if content_type == "promotional":
            score += 0.3
        if any(key in audience.lower() for key in ["upper", "upper_middle"]):
            score += 0.2
        if price_range and price_range < 1000:
            score += 0.15
        return round(min(1.0, max(0.0, score)), 2)

    def recommend_pricing_strategy(self, product: Dict[str, Any], segment: str) -> Dict[str, Any]:
        category = (product.get("category") or product.get("listing", {}).get("category", "")).lower()
        price = float(product.get("listing", {}).get("price", {}).get("amount", 0) or 0)
        strategy = "competitive"
        psychological_price = 999
        if price > 5000:
            strategy = "premium"
            psychological_price = int(price) - 1 if int(price) > 1 else 999
        elif price < 500:
            strategy = "penetration"
            psychological_price = int(price * 0.95)
        bundle = "buy 2 get 1"
        urgency = ["limited_time", "stock_remaining"]

        if segment == "lower":
            strategy = "competitive"
            psychological_price = max(99, int(price * 0.98))
            urgency = ["limited_time"]

        return {
            "price_point": strategy,
            "psychological_price": psychological_price,
            "bundle_suggestion": bundle,
            "urgency_tactics": urgency,
        }
