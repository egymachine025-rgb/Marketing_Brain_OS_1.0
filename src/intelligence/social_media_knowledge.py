from __future__ import annotations

from typing import Dict, List, Optional


class SocialMediaKnowledgeBase:
    """Knowledge base for Egyptian social media segmentation and behavior."""

    SEGMENTS: Dict[str, Dict[str, object]] = {
        "upper": {
            "income_range": ">50K",
            "areas": ["New Cairo", "Zamalek", "Maadi"],
            "behaviors": ["instagram", "linkedin", "premium facebook groups"],
        },
        "upper_middle": {
            "income_range": "25K-50K",
            "areas": ["Nasr City", "Heliopolis", "6th October"],
            "behaviors": ["facebook", "instagram", "twitter/x"],
        },
        "middle": {
            "income_range": "10K-25K",
            "areas": ["Dokki", "Mohandessin", "Alexandria suburbs"],
            "behaviors": ["facebook", "tiktok", "whatsapp groups"],
        },
        "lower_middle": {
            "income_range": "5K-10K",
            "areas": ["Shobra", "Imbaba", "rural areas"],
            "behaviors": ["tiktok", "facebook", "whatsapp"],
        },
        "lower": {
            "income_range": "<5K",
            "areas": ["Informal settlements", "rural villages"],
            "behaviors": ["tiktok", "whatsapp", "facebook lite"],
        },
    }

    @classmethod
    def get_segment_by_income(cls, income_egp: float) -> Optional[str]:
        if income_egp is None:
            return None
        if income_egp > 50000:
            return "upper"
        if 25000 < income_egp <= 50000:
            return "upper_middle"
        if 10000 < income_egp <= 25000:
            return "middle"
        if 5000 < income_egp <= 10000:
            return "lower_middle"
        return "lower"

    @classmethod
    def get_segment_by_area(cls, area: str) -> Optional[str]:
        if not area:
            return None
        normalized = area.strip().lower()
        for segment, data in cls.SEGMENTS.items():
            for known_area in data["areas"]:
                if normalized == known_area.lower():
                    return segment
        return None

    @classmethod
    def get_behaviors(cls, segment_name: str) -> List[str]:
        return cls.SEGMENTS.get(segment_name, {}).get("behaviors", [])

    @classmethod
    def get_segment_info(cls, segment_name: str) -> Optional[Dict[str, object]]:
        return cls.SEGMENTS.get(segment_name)
