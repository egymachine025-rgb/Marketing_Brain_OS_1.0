from __future__ import annotations

from typing import Dict, List, Any


class KeywordResearchEngine:
    """Search and competitor keyword intelligence for Egyptian markets."""

    CATEGORY_KEYWORDS: Dict[str, List[Dict[str, Any]]] = {
        "fashion": [
            {
                "keyword": "شوز رياضي رجالي",
                "search_volume_estimate": "high",
                "competition_level": "low",
                "cpc_estimate_egp": 2.5,
                "difficulty_score": 0.3,
                "related_keywords": ["شوز رياضي نسائي", "شوز كاجوال"],
                "suggested_content": "product comparison",
            },
            {
                "keyword": "اوتفيت خروج كاجوال",
                "search_volume_estimate": "medium",
                "competition_level": "low",
                "cpc_estimate_egp": 1.8,
                "difficulty_score": 0.25,
                "related_keywords": ["ملابس كاجوال", "لوك شبابي"],
                "suggested_content": "review",
            },
        ],
        "tech": [
            {
                "keyword": "ايفون 15 برو للبيع",
                "search_volume_estimate": "high",
                "competition_level": "low",
                "cpc_estimate_egp": 3.5,
                "difficulty_score": 0.28,
                "related_keywords": ["سعر ايفون 15", "مراجعة ايفون 15"],
                "suggested_content": "buying guide",
            }
        ],
        "food": [
            {
                "keyword": "مطاعم في القاهرة",
                "search_volume_estimate": "high",
                "competition_level": "low",
                "cpc_estimate_egp": 2.0,
                "difficulty_score": 0.35,
                "related_keywords": ["افضل مطاعم", "مطاعم عائلية"],
                "suggested_content": "review",
            }
        ],
    }

    def find_low_competition_keywords(self, category: str, market: str = "egypt") -> List[Dict[str, Any]]:
        if not category:
            category = "fashion"
        category_key = category.strip().lower().replace(" ", "_")
        return self.CATEGORY_KEYWORDS.get(category_key, self.CATEGORY_KEYWORDS.get("fashion", []))

    def analyze_competitor_keywords(self, competitor_content: List[str]) -> Dict[str, Any]:
        combined = " ".join(competitor_content).lower()
        found = []
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for item in keywords:
                if item["keyword"] in combined:
                    found.append(item["keyword"])
        found = sorted(set(found))

        gaps = []
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for item in keywords:
                if item["keyword"] not in combined and len(gaps) < 5:
                    gaps.append(item["keyword"])

        opportunities = [
            f"Create {item['suggested_content']} for {item['keyword']}"
            for category in self.CATEGORY_KEYWORDS.values()
            for item in category[:3]
        ]

        return {
            "keywords_they_rank_for": found,
            "gaps_we_can_target": gaps,
            "content_opportunities": sorted(set(opportunities))[:5],
        }

    def seasonal_trends(self, category: str) -> Dict[str, List[str]]:
        return {
            "ramadan": ["modest fashion", "family gifts"],
            "summer": ["swimwear", "air conditioners"],
            "back_to_school": ["stationery", "laptops"],
            "black_friday": ["electronics", "appliances"],
        }
