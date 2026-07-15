"""
Mission Validator Module
==========================
Validates that a Mission object is complete and does not violate the
Mission Contract (e.g. it must never contain research output,
AI-generated recommendations, or marketing plans — those belong to
later layers).

No AI. Pure Python.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from contracts.mission_contract import REQUIRED_FIELDS, FORBIDDEN_FIELDS


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid


class MissionValidator:
    """Validates Mission dicts against MISSION_CONTRACT.md."""

    def validate(self, mission: dict[str, Any]) -> ValidationResult:
        errors: list[str] = []

        errors.extend(self._check_required_fields(mission))
        errors.extend(self._check_forbidden_fields(mission))
        errors.extend(self._check_field_values(mission))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def _check_required_fields(self, mission: dict[str, Any]) -> list[str]:
        errors = []
        for required in REQUIRED_FIELDS:
            if required not in mission:
                errors.append(f"Missing required field: '{required}'")
            elif mission[required] in (None, "", [], {}):
                # budget=0 is valid (zero-funding start). success_metrics/timeline
                # are allowed to start empty — they're often filled in later,
                # not necessarily known at onboarding time.
                if required in ("budget", "success_metrics", "timeline"):
                    continue
                errors.append(f"Required field '{required}' is empty")
        return errors

    def _check_forbidden_fields(self, mission: dict[str, Any]) -> list[str]:
        errors = []
        for forbidden in FORBIDDEN_FIELDS:
            if forbidden in mission:
                errors.append(
                    f"Forbidden field '{forbidden}' found in Mission — "
                    f"this belongs to a later layer (Research/Strategy), not Mission."
                )
        return errors

    def _check_field_values(self, mission: dict[str, Any]) -> list[str]:
        errors = []

        budget = mission.get("budget")
        if budget is not None and not isinstance(budget, (int, float)):
            errors.append("Field 'budget' must be numeric.")
        if isinstance(budget, (int, float)) and budget < 0:
            errors.append("Field 'budget' cannot be negative.")

        resources = mission.get("resources", {})
        if not isinstance(resources, dict) or "sources" not in resources:
            errors.append("Field 'resources' must be a dict containing 'sources'.")

        return errors
