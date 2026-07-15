from __future__ import annotations

from typing import Iterable


def score_roi(expected_revenue: float, investment: float) -> float:
    """
    Convert revenue and investment into an ROI score as a ratio.

    The score is calculated as (revenue - investment) / investment and can exceed 1.0
    for high-return opportunities.
    """
    if investment <= 0:
        return 0.0
    return round(max(0.0, (expected_revenue - investment) / investment), 4)


def score_risk(risk_list: Iterable[str], market_stability: float) -> float:
    """
    Lower score for more risks and lower market stability.
    """
    if market_stability < 0:
        market_stability = 0.0
    risk_factor = len(list(risk_list)) * 0.1
    return round(max(0.0, min(1.0, market_stability - risk_factor)), 4)


def score_timing(seasonality: float, competition_timing: float) -> float:
    """
    Combine seasonality and competition timing into a decision timing score.
    """
    return round(max(0.0, min(1.0, (seasonality + (1.0 - competition_timing)) / 2.0)), 4)
