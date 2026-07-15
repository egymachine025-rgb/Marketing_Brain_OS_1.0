from __future__ import annotations

import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from contracts.knowledge_repository_contract import KnowledgeRepositoryContract
from src.knowledge.knowledge_object import KnowledgeObject


class KnowledgeRepository(KnowledgeRepositoryContract):
    """
    JSON-backed repository for marketing knowledge objects.

    Each knowledge type is persisted in its own file under `data/knowledge/`.
    Deduplication is performed on the composite key (type, name, language).
    """

    def __init__(self, data_dir: str = "data/knowledge") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save(self, knowledge_object: KnowledgeObject) -> KnowledgeObject:
        path = self._path_for_type(knowledge_object.type)
        data = self._load_file(path)
        record = self._record_from_object(knowledge_object)

        existing = self._find_entity(
            data["entities"],
            knowledge_object.type,
            knowledge_object.name,
            knowledge_object.language,
        )

        if existing is not None:
            merged = self._merge_entity(existing, record)
            index = data["entities"].index(existing)
            data["entities"][index] = merged
            self._write_file(path, data)
            return self._object_from_record(merged)

        data["entities"].append(record)
        self._write_file(path, data)
        return self._object_from_record(record)

    def get_by_id(self, obj_id: str | uuid.UUID) -> KnowledgeObject | None:
        parsed_id = self._parse_uuid(obj_id)
        if parsed_id is None:
            return None

        for record in self._all_records():
            if record.get("id") == str(parsed_id):
                return self._object_from_record(record)

        return None

    def get_by_type_and_name(
        self, obj_type: str, name: str, language: str = "en"
    ) -> KnowledgeObject | None:
        data = self._load_file(self._path_for_type(obj_type))
        for record in data["entities"]:
            if self._is_matching(record, obj_type, name, language):
                return self._object_from_record(record)
        return None

    def get_by_type(self, obj_type: str, language: str = "en") -> list[KnowledgeObject]:
        data = self._load_file(self._path_for_type(obj_type))
        return [
            self._object_from_record(record)
            for record in data["entities"]
            if record.get("language") == language
        ]

    def get_all(self) -> list[KnowledgeObject]:
        return [self._object_from_record(record) for record in self._all_records()]

    def get_linked_products(self, obj_id: str | uuid.UUID) -> list[str]:
        parsed_id = self._parse_uuid(obj_id)
        if parsed_id is None:
            return []

        for record in self._all_records():
            if record.get("id") == str(parsed_id):
                return list(record.get("linked_products", []))

        return []

    def link_product(self, obj_id: str | uuid.UUID, product_id: str) -> bool:
        parsed_id = self._parse_uuid(obj_id)
        if parsed_id is None:
            return False

        for path in self.data_dir.glob("*.json"):
            data = self._load_file(path)
            modified = False

            for record in data["entities"]:
                if record.get("id") == str(parsed_id):
                    linked = record.setdefault("linked_products", [])
                    if product_id not in linked:
                        linked.append(product_id)
                        record["updated_at"] = self._now_iso()
                        modified = True
                        self._write_file(path, data)
                    return modified

        return False

    def get_statistics(self) -> dict[str, Any]:
        records = self._all_records()
        total = len(records)
        counts: dict[str, int] = {}
        total_confidence = 0.0

        for record in records:
            obj_type = record.get("type", "unknown")
            counts[obj_type] = counts.get(obj_type, 0) + 1
            total_confidence += float(record.get("confidence", 0.0))

        return {
            "counts_by_type": counts,
            "total_entities": total,
            "avg_confidence": round(total_confidence / total, 4) if total else 0.0,
        }

    def find_by_metadata(self, key: str, value: Any) -> list[KnowledgeObject]:
        results: list[KnowledgeObject] = []
        for record in self._all_records():
            metadata = record.get("metadata", {})
            if key not in metadata:
                continue
            metadata_value = metadata[key]
            if metadata_value == value:
                results.append(self._object_from_record(record))
                continue
            if isinstance(metadata_value, (list, tuple, set)) and value in metadata_value:
                results.append(self._object_from_record(record))
        return results

    def delete(self, obj_id: str | uuid.UUID) -> bool:
        parsed_id = self._parse_uuid(obj_id)
        if parsed_id is None:
            return False

        for path in self.data_dir.glob("*.json"):
            data = self._load_file(path)
            filtered = [record for record in data["entities"] if record.get("id") != str(parsed_id)]
            if len(filtered) != len(data["entities"]):
                data["entities"] = filtered
                self._write_file(path, data)
                return True

        return False

    def _path_for_type(self, obj_type: str) -> Path:
        safe_name = obj_type.strip().lower().replace(" ", "_")
        return self.data_dir / f"{safe_name}.json"

    def _load_file(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {"entities": []}
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or "entities" not in data:
                raise ValueError("Invalid repository format")
            return {"entities": list(data.get("entities", []))}
        except (json.JSONDecodeError, ValueError):
            backup = path.with_name(f"{path.stem}.corrupt.{int(time.time())}.bak{path.suffix}")
            path.replace(backup)
            return {"entities": []}

    def _write_file(self, path: Path, data: dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _all_records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for path in self.data_dir.glob("*.json"):
            data = self._load_file(path)
            records.extend(data["entities"])
        return records

    def _find_entity(
        self, entities: list[dict[str, Any]], obj_type: str, name: str, language: str
    ) -> dict[str, Any] | None:
        for record in entities:
            if self._is_matching(record, obj_type, name, language):
                return record
        return None

    def _is_matching(self, record: dict[str, Any], obj_type: str, name: str, language: str) -> bool:
        return (
            record.get("type") == obj_type
            and record.get("name") == name
            and record.get("language") == language
        )

    def _merge_entity(self, existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        merged = dict(existing)
        merged["updated_at"] = self._now_iso()
        merged["confidence"] = round(
            (float(existing.get("confidence", 0.0)) + float(incoming.get("confidence", 0.0))) / 2,
            4,
        )
        merged_metadata = dict(existing.get("metadata", {}))
        merged_metadata.update(incoming.get("metadata", {}))
        merged["metadata"] = merged_metadata

        merged_products = list(existing.get("linked_products", []))
        for product_id in incoming.get("linked_products", []):
            if product_id not in merged_products:
                merged_products.append(product_id)
        merged["linked_products"] = merged_products

        merged["source"] = incoming.get("source", merged.get("source"))
        merged["value"] = incoming.get("value", merged.get("value"))

        return merged

    def _record_from_object(self, knowledge_object: KnowledgeObject) -> dict[str, Any]:
        record = knowledge_object.to_dict()
        record["linked_products"] = []
        linked = knowledge_object.metadata.get("linked_products")
        if isinstance(linked, list):
            record["linked_products"] = list(linked)
        product_id = knowledge_object.metadata.get("product_id")
        if isinstance(product_id, str) and product_id not in record["linked_products"]:
            record["linked_products"].append(product_id)
        return record

    def _object_from_record(self, record: dict[str, Any]) -> KnowledgeObject:
        payload = dict(record)
        payload.pop("linked_products", None)
        return KnowledgeObject.from_dict(payload)

    def _parse_uuid(self, obj_id: str | uuid.UUID) -> uuid.UUID | None:
        if isinstance(obj_id, uuid.UUID):
            return obj_id
        try:
            return uuid.UUID(str(obj_id))
        except (ValueError, TypeError):
            return None

    def _now_iso(self) -> str:
        return datetime.utcnow().isoformat()
