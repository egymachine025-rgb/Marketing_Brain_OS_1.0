"""
Mission Builder Module
=======================
Constructs a Mission object from raw onboarding answers.

This is the FIRST thing Marketing Brain OS runs for any user, per
governance rule NR-002 (Mission Before Product). No other layer
(Acquisition, Research, Strategy...) may run before a valid Mission
exists.

No AI. Pure Python. No external dependencies.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any

from contracts.mission_contract import (
    VALID_GOALS,
    VALID_EXPERIENCE_LEVELS,
    VALID_SOURCE_TYPES,
    VALID_SALES_TOOLS,
)


class MissionBuilder:
    """Builds a well-formed Mission dict from raw answers collected during onboarding."""

    def build(self, answers: dict[str, Any]) -> dict[str, Any]:
        """
        Build a Mission object.

        Args:
            answers: raw dict collected from the onboarding flow. Expected keys:
                - goal: str (one of VALID_GOALS)
                - experience_level: str (one of VALID_EXPERIENCE_LEVELS)
                - sources: list[dict] each like {"type": str, "identifier": str}
                - sales_tools: list[str] (subset of VALID_SALES_TOOLS)
                - budget: float (0 is valid — zero-funding start is a first-class case)
                - business_description: str (free text, e.g. "قناة تيليجرام ملابس حريمي")

        Returns:
            A Mission dict matching the fields required by MISSION_CONTRACT.
        """
        goal = self._normalize_goal(answers.get("goal", ""))
        experience_level = self._normalize_experience(answers.get("experience_level", ""))
        sources = self._normalize_sources(answers.get("sources", []))
        sales_tools = self._normalize_sales_tools(answers.get("sales_tools", []))
        budget = float(answers.get("budget", 0) or 0)

        mission: dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "goal": goal,
            "user": {
                "experience_level": experience_level,
            },
            "business": {
                "description": answers.get("business_description", "").strip(),
            },
            "resources": {
                "sources": sources,
            },
            "constraints": {
                "zero_funding": budget == 0,
            },
            "budget": budget,
            "timeline": answers.get("timeline", "unspecified"),
            "current_stage": "onboarding_complete",
            "success_metrics": answers.get("success_metrics", []),
            "sales_tools": sales_tools,
        }
        return mission

    # -- normalization helpers -------------------------------------------------

    def _normalize_goal(self, raw: str) -> str:
        raw = (raw or "").strip().lower()
        if raw not in VALID_GOALS:
            raise ValueError(
                f"Invalid goal '{raw}'. Must be one of: {', '.join(VALID_GOALS)}"
            )
        return raw

    def _normalize_experience(self, raw: str) -> str:
        raw = (raw or "").strip().lower()
        if raw not in VALID_EXPERIENCE_LEVELS:
            raise ValueError(
                f"Invalid experience_level '{raw}'. Must be one of: {', '.join(VALID_EXPERIENCE_LEVELS)}"
            )
        return raw

    def _normalize_sources(self, raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for item in raw:
            source_type = (item.get("type") or "").strip().lower()
            if source_type not in VALID_SOURCE_TYPES:
                raise ValueError(
                    f"Invalid source type '{source_type}'. Must be one of: {', '.join(VALID_SOURCE_TYPES)}"
                )
            normalized.append({
                "type": source_type,
                "identifier": (item.get("identifier") or "").strip(),
            })
        if not normalized:
            normalized.append({"type": "none_yet", "identifier": ""})
        return normalized

    def _normalize_sales_tools(self, raw: list[str]) -> list[str]:
        normalized: list[str] = []
        for item in raw:
            tool = (item or "").strip().lower()
            if tool not in VALID_SALES_TOOLS:
                raise ValueError(
                    f"Invalid sales tool '{tool}'. Must be one of: {', '.join(VALID_SALES_TOOLS)}"
                )
            normalized.append(tool)
        if not normalized:
            normalized.append("none_yet")
        return normalized
