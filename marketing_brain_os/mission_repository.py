"""
Mission Repository Module
============================
Stores and retrieves Mission objects. Pure storage — no business logic,
no validation (that's MissionValidator's job).

Uses a plain JSON file under data/memory/ so the system runs with zero
external dependencies (no database server required) — consistent with
the zero-funding starting constraint of this project.

No AI. Pure Python.
"""

from __future__ import annotations
import json
import os
from typing import Any


DEFAULT_STORAGE_PATH = os.path.join("data", "memory", "missions.json")


class MissionRepository:
    """JSON-file-backed repository for Mission objects."""

    def __init__(self, storage_path: str = DEFAULT_STORAGE_PATH):
        self.storage_path = storage_path
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        directory = os.path.dirname(self.storage_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read_all(self) -> list[dict[str, Any]]:
        with open(self.storage_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, missions: list[dict[str, Any]]) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(missions, f, ensure_ascii=False, indent=2)

    def save(self, mission: dict[str, Any]) -> dict[str, Any]:
        """Insert a new Mission, or update it in place if its id already exists."""
        missions = self._read_all()
        existing_index = next(
            (i for i, m in enumerate(missions) if m.get("id") == mission.get("id")),
            None,
        )
        if existing_index is not None:
            missions[existing_index] = mission
        else:
            missions.append(mission)
        self._write_all(missions)
        return mission

    def get_by_id(self, mission_id: str) -> dict[str, Any] | None:
        missions = self._read_all()
        return next((m for m in missions if m.get("id") == mission_id), None)

    def get_latest(self) -> dict[str, Any] | None:
        """Returns the most recently created Mission — this is what every
        other layer should read to know 'what is the current goal'."""
        missions = self._read_all()
        if not missions:
            return None
        return sorted(missions, key=lambda m: m.get("created_at", ""))[-1]

    def list_all(self) -> list[dict[str, Any]]:
        return self._read_all()
