from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List


class ContentAnalyzer:
    """Analyze social media content and page signals."""

    CONTENT_TYPES = {
        "product_showcase": ["price", "offer", "sale", "buy", "deal"],
        "lifestyle": ["style", "living", "home", "travel", "lifestyle"],
        "educational": ["learn", "how to", "tips", "guide", "tutorial"],
        "entertainment": ["fun", "meme", "video", "challenge", "music"],
        "promotional": ["discount", "limited", "free", "sale", "promo"],
    }

    TONE_KEYWORDS = {
        "professional": ["official", "professional", "expert", "quality", "certified"],
        "casual": ["fun", "easy", "chill", "cool", "relax"],
        "aggressive": ["hurry", "now", "limited", "act fast", "only"],
        "friendly": ["welcome", "hi", "dear", "friend", "thanks"],
        "luxury": ["premium", "exclusive", "luxury", "designer", "limited edition"],
    }

    PLATFORM_SCORES = {
        "facebook": ["facebook", "fb"],
        "instagram": ["instagram", "insta", "reels"],
        "tiktok": ["tiktok", "tik tok", "video"],
        "whatsapp": ["whatsapp", "wa", "group"],
    }

    CATEGORY_KEYWORDS = {
        "fashion": ["dress", "shoes", "clothes", "apparel", "fashion", "outfit"],
        "tech": ["phone", "laptop", "tablet", "tech", "electronics", "gadget"],
        "food": ["restaurant", "food", "cafe", "eat", "drinks", "meal"],
        "real_estate": ["villa", "apartment", "flat", "house", "real estate", "property"],
        "education": ["course", "learn", "classes", "study", "training"],
        "health": ["health", "fitness", "wellness", "doctor", "clinic"],
    }

    def analyze_content_type(self, text: str, images: List[Any] = []) -> Dict[str, Any]:
        normalized = (text or "").lower()
        result: Dict[str, Any] = {
            "type": "product_showcase",
            "tone": "friendly",
            "engagement_predicted": 0.5,
            "best_platform": ["facebook"],
            "best_time_to_post": "18:00",
            "target_audience": ["middle"],
        }

        # Determine type.
        for content_type, keywords in self.CONTENT_TYPES.items():
            if any(keyword in normalized for keyword in keywords):
                result["type"] = content_type
                break

        # Determine tone.
        for tone, keywords in self.TONE_KEYWORDS.items():
            if any(keyword in normalized for keyword in keywords):
                result["tone"] = tone
                break

        # Engagement estimate.
        engagement = 0.3
        engagement += 0.2 if result["type"] in ["product_showcase", "promotional"] else 0.1
        engagement += 0.1 if len(images) > 0 else 0.0
        engagement += 0.1 if "#" in normalized else 0.0
        result["engagement_predicted"] = min(1.0, round(engagement, 2))

        # Platform scoring.
        platforms = []
        for platform, keywords in self.PLATFORM_SCORES.items():
            if any(keyword in normalized for keyword in keywords):
                platforms.append(platform)
        if not platforms:
            platforms = ["facebook", "tiktok"] if result["type"] in ["entertainment", "product_showcase"] else ["instagram"]
        result["best_platform"] = platforms

        # Time of day heuristics.
        if result["type"] in ["entertainment", "lifestyle"]:
            result["best_time_to_post"] = "20:00"
        elif result["type"] == "educational":
            result["best_time_to_post"] = "17:00"
        else:
            result["best_time_to_post"] = "18:30"

        # Target audience.
        if result["tone"] == "luxury":
            result["target_audience"] = ["upper", "upper_middle"]
        elif result["type"] in ["educational", "entertainment"]:
            result["target_audience"] = ["middle", "lower_middle"]
        else:
            result["target_audience"] = ["upper_middle", "middle"]

        return result

    def categorize_page(self, content_samples: List[str]) -> Dict[str, Any]:
        merged = " ".join(content_samples).lower()
        category = "fashion"
        for key, keywords in self.CATEGORY_KEYWORDS.items():
            if any(word in merged for word in keywords):
                category = key
                break

        sub_categories = []
        if "men" in merged or "male" in merged:
            sub_categories.append("men")
        if "women" in merged or "female" in merged:
            sub_categories.append("women")
        if "kids" in merged or "children" in merged:
            sub_categories.append("kids")
        if "luxury" in merged or "premium" in merged:
            sub_categories.append("luxury")
        if "budget" in merged or "economy" in merged:
            sub_categories.append("budget")

        if not sub_categories:
            sub_categories = ["products", "lifestyle"] if category in ["fashion", "real_estate"] else ["tips", "reviews"]

        brand_voice = "professional and informative"
        if "fun" in merged or "cool" in merged:
            brand_voice = "friendly and casual"
        if "premium" in merged or "exclusive" in merged:
            brand_voice = "luxury and aspirational"

        return {
            "primary_category": category,
            "sub_categories": sorted(set(sub_categories)),
            "content_pillars": ["tips", "products", "reviews", "lifestyle"],
            "brand_voice": brand_voice,
        }

    def extract_keywords(self, text: str) -> Dict[str, Any]:
        normalized = (text or "").lower()
        tokens = re.findall(r"[\w\u0600-\u06FF']+", normalized)
        keywords = [token for token in tokens if len(token) > 3]
        counts = Counter(keywords)
        primary = [kw for kw, _ in counts.most_common(5)][:3]

        hashtags = [tag for tag in re.findall(r"#\w+", normalized)]
        long_tail = []
        words = normalized.split()
        for i in range(len(words) - 2):
            phrase = " ".join(words[i : i + 3])
            if any(term in phrase for term in ["how to", "best", "for sale", "buy now"]):
                long_tail.append(phrase)
        long_tail = sorted(set(long_tail))[:3]

        trending_score = min(1.0, round((len(hashtags) * 0.1 + len(primary) * 0.05 + 0.2), 2))

        return {
            "primary_keywords": [kw for kw in primary if kw],
            "long_tail": long_tail,
            "hashtags": hashtags,
            "trending_score": trending_score,
        }
