from __future__ import annotations

from typing import Any


STRATEGY_TEMPLATES: dict[str, dict[str, Any]] = {
    "market_penetration": {
        "description": "Low price, high volume expansion within existing markets.",
        "phases": [
            {"name": "Launch", "focus": "pricing_and_distribution", "kpi_weight": 0.3},
            {"name": "Scale", "focus": "customer_acquisition", "kpi_weight": 0.4},
            {"name": "Optimize", "focus": "margin_improvement", "kpi_weight": 0.3},
        ],
    },
    "market_development": {
        "description": "Enter new markets with existing products.",
        "phases": [
            {"name": "Market Research", "focus": "localization", "kpi_weight": 0.25},
            {"name": "Entry", "focus": "distribution_and_partnerships", "kpi_weight": 0.45},
            {"name": "Growth", "focus": "brand_awareness", "kpi_weight": 0.3},
        ],
    },
    "product_development": {
        "description": "Launch new products within proven markets.",
        "phases": [
            {"name": "Design", "focus": "product_innovation", "kpi_weight": 0.25},
            {"name": "Pilot", "focus": "market_testing", "kpi_weight": 0.35},
            {"name": "Launch", "focus": "go_to_market", "kpi_weight": 0.4},
        ],
    },
    "diversification": {
        "description": "Enter a new product category in a new market.",
        "phases": [
            {"name": "Discovery", "focus": "opportunity_assessment", "kpi_weight": 0.2},
            {"name": "Launch", "focus": "cross_sell_and_positioning", "kpi_weight": 0.4},
            {"name": "Expand", "focus": "portfolio_buildout", "kpi_weight": 0.4},
        ],
    },
}


def get_template(template_name: str) -> dict[str, Any]:
    """Return the requested strategy template or a default template."""
    return STRATEGY_TEMPLATES.get(template_name, STRATEGY_TEMPLATES["market_development"])
