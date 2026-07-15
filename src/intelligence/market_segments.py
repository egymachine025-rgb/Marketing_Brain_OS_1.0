"""
Egyptian Market Segments Module
================================
Defines detailed market segments for Egypt with income levels, demographics,
and social media preferences for targeted marketing strategies.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class MarketSegment:
    """Represents a single market segment in Egypt."""
    name: str
    income_range: str
    income_min: int
    income_max: int
    population_percentage: float
    areas: List[str]
    age_range: str
    education_level: str
    social_media_platforms: List[str]
    content_preferences: List[str]
    purchasing_behavior: str
    price_sensitivity: str
    brand_loyalty: str
    preferred_payment_methods: List[str]
    peak_activity_hours: str
    language_preference: str


class EgyptianMarketSegments:
    """
    Comprehensive Egyptian market segmentation data.
    Based on demographic studies and consumer behavior patterns in Egypt.
    """

    SEGMENTS: Dict[str, MarketSegment] = {
        "upper": MarketSegment(
            name="Upper Class",
            income_range=">50,000 EGP",
            income_min=50000,
            income_max=999999,
            population_percentage=0.05,
            areas=[
                "New Cairo (5th Settlement, Maadi, Rehab)",
                "Zamalek",
                "Maadi",
                "Sheikh Zayed",
                "6th October (Gardenia, Beverly Hills)"
            ],
            age_range="30-55",
            education_level="University Graduate + Postgraduate",
            social_media_platforms=[
                "Instagram",
                "LinkedIn",
                "Premium Facebook Groups",
                "Twitter/X",
                "WhatsApp Business"
            ],
            content_preferences=[
                "Premium lifestyle content",
                "International brands",
                "Exclusive offers",
                "Quality-focused messaging",
                "English/Arabic bilingual"
            ],
            purchasing_behavior="Quality and brand conscious",
            price_sensitivity="Low",
            brand_loyalty="High (to premium brands)",
            preferred_payment_methods=["Credit Cards", "Digital Wallets", "Bank Transfer"],
            peak_activity_hours="19:00-22:00",
            language_preference="English/Arabic Bilingual"
        ),
        
        "upper_middle": MarketSegment(
            name="Upper Middle Class",
            income_range="25,000-50,000 EGP",
            income_min=25000,
            income_max=50000,
            population_percentage=0.15,
            areas=[
                "Nasr City",
                "Heliopolis",
                "6th October (main areas)",
                "New Giza",
                "Madinet Nasr"
            ],
            age_range="28-45",
            education_level="University Graduate",
            social_media_platforms=[
                "Facebook",
                "Instagram",
                "Twitter/X",
                "WhatsApp",
                "TikTok (growing)"
            ],
            content_preferences=[
                "Family-oriented content",
                "Value for quality",
                "Local and international brands",
                "Educational content",
                "Arabic with some English"
            ],
            purchasing_behavior="Balanced quality and price",
            price_sensitivity="Medium",
            brand_loyalty="Medium-High",
            preferred_payment_methods=["Credit Cards", "Digital Wallets", "COD (30%)"],
            peak_activity_hours="18:00-21:00",
            language_preference="Arabic Primary"
        ),
        
        "middle": MarketSegment(
            name="Middle Class",
            income_range="10,000-25,000 EGP",
            income_min=10000,
            income_max=25000,
            population_percentage=0.35,
            areas=[
                "Dokki",
                "Mohandessin",
                "Agouza",
                "Alexandria (Smouha, Miami)",
                "Mansoura",
                "Tanta"
            ],
            age_range="25-40",
            education_level="University/Technical Institute",
            social_media_platforms=[
                "Facebook",
                "TikTok",
                "WhatsApp Groups",
                "Instagram",
                "Facebook Lite"
            ],
            content_preferences=[
                "Practical content",
                "Discounts and deals",
                "Family values",
                "Local brands",
                "Egyptian Arabic"
            ],
            purchasing_behavior="Price-conscious but quality-aware",
            price_sensitivity="Medium-High",
            brand_loyalty="Medium",
            preferred_payment_methods=["COD (60%)", "Digital Wallets", "Installments"],
            peak_activity_hours="12:00-15:00, 19:00-22:00",
            language_preference="Egyptian Arabic"
        ),
        
        "lower_middle": MarketSegment(
            name="Lower Middle Class",
            income_range="5,000-10,000 EGP",
            income_min=5000,
            income_max=10000,
            population_percentage=0.30,
            areas=[
                "Shobra",
                "Imbaba",
                "Ain Shams",
                "Matariya",
                "Helwan",
                "Rural areas near cities"
            ],
            age_range="20-35",
            education_level="High School/Some University",
            social_media_platforms=[
                "TikTok",
                "Facebook",
                "WhatsApp",
                "Facebook Lite",
                "Instagram (limited)"
            ],
            content_preferences=[
                "Entertainment",
                "Viral trends",
                "Heavy discounts",
                "Casual content",
                "Egyptian Arabic slang"
            ],
            purchasing_behavior="Highly price-sensitive",
            price_sensitivity="High",
            brand_loyalty="Low-Medium",
            preferred_payment_methods=["COD (80%)", "Cash", "Installments"],
            peak_activity_hours="16:00-22:00",
            language_preference="Egyptian Arabic"
        ),
        
        "lower": MarketSegment(
            name="Lower Class",
            income_range="<5,000 EGP",
            income_min=0,
            income_max=5000,
            population_percentage=0.15,
            areas=[
                "Informal settlements (Ashwa'iyyat)",
                "Rural villages",
                "Upper Egypt rural areas",
                "Delta rural areas"
            ],
            age_range="18-45",
            education_level="Basic/Primary School",
            social_media_platforms=[
                "TikTok",
                "WhatsApp",
                "Facebook Lite",
                "Facebook"
            ],
            content_preferences=[
                "Simple entertainment",
                "Local deals",
                "Community-focused",
                "Egyptian Arabic (colloquial)"
            ],
            purchasing_behavior="Essential goods only",
            price_sensitivity="Very High",
            brand_loyalty="Low (price-driven)",
            preferred_payment_methods=["COD (95%)", "Cash"],
            peak_activity_hours="Variable",
            language_preference="Egyptian Arabic (Colloquial)"
        )
    }

    # Platform-specific insights
    PLATFORM_INSIGHTS: Dict[str, Dict[str, Any]] = {
        "facebook": {
            "user_base": "45 million",
            "primary_demographics": ["middle", "lower_middle", "upper_middle"],
            "best_content_types": ["Image posts", "Video content", "Carousel ads"],
            "peak_times": ["12:00-15:00", "19:00-21:00"],
            "ad_effectiveness": "High for all segments",
            "engagement_rate": "3-5%"
        },
        "instagram": {
            "user_base": "12 million",
            "primary_demographics": ["upper", "upper_middle", "middle"],
            "best_content_types": ["Stories", "Reels", "High-quality images"],
            "peak_times": ["19:00-22:00"],
            "ad_effectiveness": "High for upper/middle segments",
            "engagement_rate": "4-6%"
        },
        "tiktok": {
            "user_base": "18 million",
            "primary_demographics": ["lower_middle", "middle", "upper_middle"],
            "best_content_types": ["Short videos", "Trends", "Entertainment"],
            "peak_times": ["18:00-21:00"],
            "ad_effectiveness": "High for younger demographics",
            "engagement_rate": "8-12%"
        },
        "whatsapp": {
            "user_base": "35 million",
            "primary_demographics": ["all segments"],
            "best_content_types": ["Direct messages", "Status updates", "Catalog"],
            "peak_times": ["10:00-12:00", "16:00-18:00"],
            "ad_effectiveness": "High for business communication",
            "engagement_rate": "High (direct communication)"
        }
    }

    # Regional insights
    REGIONAL_INSIGHTS: Dict[str, Dict[str, Any]] = {
        "cairo": {
            "population": 22_000_000,
            "dominant_segments": ["upper_middle", "middle", "upper"],
            "purchasing_power": "Highest in Egypt",
            "preferred_channels": ["Facebook", "Instagram", "WhatsApp"],
            "market_characteristics": "Diverse, trend-setting, competitive"
        },
        "alexandria": {
            "population": 5_000_000,
            "dominant_segments": ["middle", "upper_middle"],
            "purchasing_power": "High",
            "preferred_channels": ["Facebook", "TikTok", "Instagram"],
            "market_characteristics": "Coastal lifestyle, tourism-influenced"
        },
        "delta": {
            "population": 15_000_000,
            "dominant_segments": ["middle", "lower_middle"],
            "purchasing_power": "Medium",
            "preferred_channels": ["Facebook", "WhatsApp"],
            "market_characteristics": "Price-sensitive, family-oriented"
        },
        "upper_egypt": {
            "population": 20_000_000,
            "dominant_segments": ["middle", "lower_middle"],
            "purchasing_power": "Medium-Low",
            "preferred_channels": ["Facebook", "WhatsApp"],
            "market_characteristics": "Traditional, brand-loyal, conservative"
        },
        "sinai_red_sea": {
            "population": 3_000_000,
            "dominant_segments": ["middle", "upper_middle"],
            "purchasing_power": "Medium-High (seasonal)",
            "preferred_channels": ["Instagram", "Facebook"],
            "market_characteristics": "Tourism-focused, seasonal demand"
        }
    }

    @classmethod
    def get_segment_by_income(cls, income_egp: float) -> str:
        """Determine market segment based on monthly income."""
        if income_egp is None:
            return "middle"  # Default assumption
        
        if income_egp > 50000:
            return "upper"
        elif income_egp > 25000:
            return "upper_middle"
        elif income_egp > 10000:
            return "middle"
        elif income_egp > 5000:
            return "lower_middle"
        else:
            return "lower"

    @classmethod
    def get_segment_by_area(cls, area: str) -> str:
        """Determine likely market segment based on residential area."""
        if not area:
            return "middle"
        
        area_lower = area.strip().lower()
        
        # Upper class areas
        upper_areas = ["new cairo", "zamalek", "maadi", "sheikh zayed", "gardenia", "beverly"]
        if any(ua in area_lower for ua in upper_areas):
            return "upper"
        
        # Upper middle class areas
        upper_middle_areas = ["nasr city", "heliopolis", "6th october", "new giza", "madinet nasr"]
        if any(uma in area_lower for uma in upper_middle_areas):
            return "upper_middle"
        
        # Middle class areas
        middle_areas = ["dokki", "mohandessin", "agouza", "smouha", "miami", "mansoura", "tanta"]
        if any(ma in area_lower for ma in middle_areas):
            return "middle"
        
        # Lower middle class areas
        lower_middle_areas = ["shobra", "imbaba", "ain shams", "matariya", "helwan"]
        if any(lma in area_lower for lma in lower_middle_areas):
            return "lower_middle"
        
        return "middle"  # Default

    @classmethod
    def get_segment(cls, segment_name: str) -> MarketSegment:
        """Get segment data by name."""
        return cls.SEGMENTS.get(segment_name, cls.SEGMENTS["middle"])

    @classmethod
    def get_all_segments(cls) -> List[MarketSegment]:
        """Get all market segments."""
        return list(cls.SEGMENTS.values())

    @classmethod
    def get_platform_insights(cls, platform: str) -> Dict[str, Any]:
        """Get insights for a specific social media platform."""
        return cls.PLATFORM_INSIGHTS.get(platform.lower(), {})

    @classmethod
    def get_regional_insights(cls, region: str) -> Dict[str, Any]:
        """Get insights for a specific region."""
        return cls.REGIONAL_INSIGHTS.get(region.lower(), {})

    @classmethod
    def recommend_platforms_for_segment(cls, segment_name: str) -> List[str]:
        """Get recommended platforms for a specific segment."""
        segment = cls.get_segment(segment_name)
        return segment.social_media_platforms

    @classmethod
    def get_content_strategy(cls, segment_name: str) -> Dict[str, Any]:
        """Get content strategy recommendations for a segment."""
        segment = cls.get_segment(segment_name)
        
        return {
            "tone": "Professional" if segment_name in ["upper", "upper_middle"] else "Casual",
            "language": segment.language_preference,
            "content_types": segment.content_preferences,
            "posting_times": segment.peak_activity_hours,
            "key_messages": cls._get_key_messages(segment_name),
            "visual_style": cls._get_visual_style(segment_name)
        }

    @classmethod
    def _get_key_messages(cls, segment_name: str) -> List[str]:
        """Get key marketing messages for a segment."""
        messages = {
            "upper": ["Quality & Exclusivity", "Premium Experience", "Brand Heritage"],
            "upper_middle": ["Value for Money", "Family Values", "Trust & Reliability"],
            "middle": ["Best Deals", "Quality Assurance", "Local Availability"],
            "lower_middle": ["Big Discounts", "Limited Offers", "Easy Payment"],
            "lower": ["Lowest Prices", "Essential Needs", "Immediate Availability"]
        }
        return messages.get(segment_name, ["Quality & Value"])

    @classmethod
    def _get_visual_style(cls, segment_name: str) -> str:
        """Get recommended visual style for a segment."""
        styles = {
            "upper": "Minimalist, premium, high-end aesthetics",
            "upper_middle": "Clean, professional, family-friendly",
            "middle": "Colorful, engaging, practical",
            "lower_middle": "Bold, attention-grabbing, dynamic",
            "lower": "Simple, clear, direct"
        }
        return styles.get(segment_name, "Clean and professional")
