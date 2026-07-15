from __future__ import annotations


def rule_competitive_threat(shared_categories: int, total_categories: int) -> str:
    """
    Determine a competitive threat level based on the share of categories
    a competitor occupies relative to the target brand.
    """
    if total_categories == 0:
        return "unknown"
    ratio = shared_categories / total_categories
    if ratio >= 0.75:
        return "critical"
    if ratio >= 0.5:
        return "high"
    if ratio >= 0.25:
        return "medium"
    return "low"


def rule_market_opportunity(competitor_count: int, category_demand: float) -> float:
    """
    Score a market opportunity using competitor density and category demand.
    """
    if category_demand < 0:
        category_demand = 0.0
    base = max(0.0, 1.0 - min(1.0, competitor_count / 5.0))
    return round(min(1.0, base * category_demand), 4)


def rule_price_tier(avg_price: float, market_median: float) -> str:
    """
    Classify a price positioning tier relative to the market median.
    """
    if market_median <= 0:
        return "unknown"
    ratio = avg_price / market_median
    if ratio >= 1.25:
        return "high"
    if ratio >= 0.9:
        return "mid"
    return "low"
