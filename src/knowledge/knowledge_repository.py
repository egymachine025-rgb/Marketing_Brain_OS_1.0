"""
Knowledge Repository
"""

import json
from pathlib import Path

from app.knowledge.knowledge_object import KnowledgeObject


class KnowledgeRepository:

    def __init__(self):

        self.folder = Path("data/knowledge")

        self.folder.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(self, knowledge: KnowledgeObject):

        path = self.folder / f"{knowledge.id}.json"

        with open(path, "w", encoding="utf-8") as f:

            json.dump(
                knowledge.to_dict(),
                f,
                indent=4,
                ensure_ascii=False,
            )

    def load(self, knowledge_id):

        path = self.folder / f"{knowledge_id}.json"

        if not path.exists():

            return None

        with open(path, "r", encoding="utf-8") as f:

            data = json.load(f)

        return KnowledgeObject.from_dict(data)

    def all(self):

        result = []

        for file in self.folder.glob("*.json"):

            with open(file, encoding="utf-8") as f:

                result.append(
                    KnowledgeObject.from_dict(
                        json.load(f)
                    )
                )

        return result