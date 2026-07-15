"""
Research Source Registry for Marketing Brain OS

This module defines available research sources for marketing intelligence gathering.
Each source includes metadata about availability, usage limits, and step-by-step instructions.
"""

RESEARCH_SOURCES = {
    "keywords": {
        "google_trends": {
            "name": "Google Trends",
            "url": "https://trends.google.com",
            "free": True,
            "steps": [
                "Go to URL",
                "Enter keyword",
                "Select Egypt",
                "Copy data"
            ]
        },
        "ubersuggest": {
            "name": "Ubersuggest",
            "url": "https://neilpatel.com/ubersuggest",
            "free": True,
            "limit": "3 searches/day"
        },
        "answer_the_public": {
            "name": "AnswerThePublic",
            "url": "https://answerthepublic.com",
            "free": True
        }
    },
    "social_media": {
        "facebook_insights": {
            "name": "Facebook Audience Insights",
            "url": "https://www.facebook.com/business/insights/tools/audience-insights",
            "free": True
        },
        "tiktok_creative": {
            "name": "TikTok Creative Center",
            "url": "https://ads.tiktok.com/business/creativecenter",
            "free": True
        }
    },
    "competitors": {
        "facebook_ad_library": {
            "name": "Facebook Ad Library",
            "url": "https://www.facebook.com/ads/library",
            "free": True
        },
        "similarweb": {
            "name": "SimilarWeb",
            "url": "https://www.similarweb.com",
            "free": True,
            "limit": "5 results"
        }
    },
    "market_research": {
        "capmas_egypt": {
            "name": "Capmas Egypt",
            "url": "https://www.capmas.gov.eg",
            "free": True,
            "language": "ar"
        },
        "google_consumer": {
            "name": "Google Consumer Barometer",
            "url": "https://www.thinkwithgoogle.com/consumer-barometer",
            "free": True
        }
    }
}

# Example task format for research suggestions
EXAMPLE_TASK = {
    "task": "Find keywords for Nike shoes in Egypt",
    "suggested_tools": ["google_trends", "ubersuggest"],
    "steps": [
        "Go to Google Trends",
        "Search 'nike shoes egypt'",
        "Note: Interest over time, related queries",
        "Go to Ubersuggest",
        "Search 'nike shoes'",
        "Note: Search volume, SEO difficulty, CPC"
    ],
    "expected_results": {
        "keywords": ["list of keywords"],
        "volumes": {"keyword": "monthly searches"},
        "difficulty": {"keyword": "score 0-100"},
        "trend": "up/down/stable"
    }
}


def get_source(category: str, source_id: str) -> dict:
    """
    Retrieve a specific research source by category and ID.
    
    Args:
        category: The category name (e.g., "keywords", "social_media")
        source_id: The source identifier (e.g., "google_trends")
    
    Returns:
        Dictionary containing source metadata, or None if not found
    """
    return RESEARCH_SOURCES.get(category, {}).get(source_id)


def get_category(category: str) -> dict:
    """
    Retrieve all sources in a specific category.
    
    Args:
        category: The category name
    
    Returns:
        Dictionary containing all sources in the category, or None if not found
    """
    return RESEARCH_SOURCES.get(category)


def get_free_sources() -> dict:
    """
    Retrieve all free research sources across all categories.
    
    Returns:
        Dictionary of free sources organized by category
    """
    free_sources = {}
    for category, sources in RESEARCH_SOURCES.items():
        free_sources[category] = {
            source_id: source_data
            for source_id, source_data in sources.items()
            if source_data.get("free", False)
        }
    return free_sources


def format_research_task(task: str, suggested_tools: list, steps: list, expected_results: dict) -> dict:
    """
    Format a research task suggestion with all required information.
    
    Args:
        task: Description of the research task
        suggested_tools: List of source IDs to use
        steps: Step-by-step instructions
        expected_results: Expected data structure for results
    
    Returns:
        Formatted task dictionary
    """
    return {
        "task": task,
        "suggested_tools": suggested_tools,
        "steps": steps,
        "expected_results": expected_results
    }
