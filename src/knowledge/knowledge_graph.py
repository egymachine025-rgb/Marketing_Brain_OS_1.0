from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from contracts.knowledge_graph_contract import KnowledgeGraphContract


class KnowledgeGraph(KnowledgeGraphContract):
    """
    JSON-backed knowledge graph that stores directed semantic relationships
    between knowledge object entities.
    """

    SUPPORTED_RELATION_TYPES = {
        "has_category",
        "has_audience",
        "has_competitor",
        "has_market",
        "has_tier",
        "has_feature",
        "similar_to",
    }

    def __init__(self, data_dir: str = "data/knowledge_graph") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.data_dir / "relationships.json"
        self.data = self._load_file()

    def add_relationship(
        self,
        from_id: str | uuid.UUID,
        to_id: str | uuid.UUID,
        relation_type: str,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        metadata = dict(metadata or {})
        relation_type = str(relation_type)

        if relation_type not in self.SUPPORTED_RELATION_TYPES:
            raise ValueError(f"Unsupported relation type: {relation_type}")

        from_id_str = str(from_id)
        to_id_str = str(to_id)

        existing = self._find_relationship(from_id_str, to_id_str, relation_type)
        if existing is not None:
            existing["weight"] = round((float(existing["weight"]) + float(weight)) / 2, 4)
            merged_metadata = dict(existing.get("metadata", {}))
            merged_metadata.update(metadata)
            existing["metadata"] = merged_metadata
            self._save_file()
            return dict(existing)

        relationship = {
            "from_id": from_id_str,
            "to_id": to_id_str,
            "relation_type": relation_type,
            "weight": round(float(weight), 4),
            "metadata": metadata,
            "created_at": self._now_iso(),
        }
        self.data["relationships"].append(relationship)
        self._save_file()
        return dict(relationship)

    def get_relationships(
        self, from_id: str | uuid.UUID, relation_type: str | None = None
    ) -> list[dict[str, Any]]:
        from_id_str = str(from_id)
        return [
            dict(record)
            for record in self.data["relationships"]
            if record["from_id"] == from_id_str
            and (relation_type is None or record["relation_type"] == relation_type)
        ]

    def get_related(
        self, to_id: str | uuid.UUID, relation_type: str | None = None
    ) -> list[dict[str, Any]]:
        to_id_str = str(to_id)
        return [
            dict(record)
            for record in self.data["relationships"]
            if record["to_id"] == to_id_str
            and (relation_type is None or record["relation_type"] == relation_type)
        ]

    def find_path(
        self,
        from_id: str | uuid.UUID,
        to_id: str | uuid.UUID,
        max_depth: int = 3,
    ) -> list[list[str]]:
        from_id_str = str(from_id)
        to_id_str = str(to_id)

        if from_id_str == to_id_str:
            return [[from_id_str]]

        adjacency: dict[str, list[str]] = {}
        for record in self.data["relationships"]:
            adjacency.setdefault(record["from_id"], []).append(record["to_id"])

        paths: list[list[str]] = []
        queue: list[list[str]] = [[from_id_str]]

        while queue:
            path = queue.pop(0)
            if len(path) - 1 >= max_depth:
                continue
            last_node = path[-1]
            for neighbor in adjacency.get(last_node, []):
                if neighbor in path:
                    continue
                next_path = path + [neighbor]
                if neighbor == to_id_str:
                    paths.append(next_path)
                else:
                    queue.append(next_path)

        return paths

    def get_neighbors(self, entity_id: str | uuid.UUID) -> dict[str, list[dict[str, Any]]]:
        entity_id_str = str(entity_id)
        neighbors: dict[str, list[dict[str, Any]]] = {}

        for record in self.data["relationships"]:
            if record["from_id"] == entity_id_str or record["to_id"] == entity_id_str:
                neighbors.setdefault(record["relation_type"], []).append(dict(record))

        return neighbors

    def delete_relationship(
        self,
        from_id: str | uuid.UUID,
        to_id: str | uuid.UUID,
        relation_type: str,
    ) -> bool:
        from_id_str = str(from_id)
        to_id_str = str(to_id)
        relation_type = str(relation_type)

        before_count = len(self.data["relationships"])
        self.data["relationships"] = [
            record
            for record in self.data["relationships"]
            if not (
                record["from_id"] == from_id_str
                and record["to_id"] == to_id_str
                and record["relation_type"] == relation_type
            )
        ]
        deleted = len(self.data["relationships"]) != before_count
        if deleted:
            self._save_file()
        return deleted

    def get_graph_statistics(self) -> dict[str, Any]:
        total_relationships = len(self.data["relationships"])
        by_type: dict[str, int] = {}
        entities: set[str] = set()

        for record in self.data["relationships"]:
            relation_type = record["relation_type"]
            by_type[relation_type] = by_type.get(relation_type, 0) + 1
            entities.add(record["from_id"])
            entities.add(record["to_id"])

        return {
            "total_relationships": total_relationships,
            "relationships_by_type": by_type,
            "unique_entities": len(entities),
            "supported_relation_types": sorted(self.SUPPORTED_RELATION_TYPES),
        }

    def _find_relationship(
        self, from_id: str, to_id: str, relation_type: str
    ) -> dict[str, Any] | None:
        for record in self.data["relationships"]:
            if (
                record["from_id"] == from_id
                and record["to_id"] == to_id
                and record["relation_type"] == relation_type
            ):
                return record
        return None

    def _load_file(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"relationships": []}

        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict) or "relationships" not in data:
                raise ValueError("Invalid graph format")
            return {"relationships": list(data.get("relationships", []))}
        except (json.JSONDecodeError, ValueError):
            backup = self.path.with_name(f"{self.path.stem}.corrupt.{int(time.time())}.bak{self.path.suffix}")
            self.path.replace(backup)
            return {"relationships": []}

    def _save_file(self) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=2, ensure_ascii=False)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()
